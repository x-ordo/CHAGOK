"""
Tests for ConsistencyManager (DynamoDB/Qdrant Saga Pattern)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from app.utils.consistency import (
    ConsistencyManager,
    ConsistencyError,
    OperationStatus,
    CompensatingAction,
    TransactionLog,
    with_retry,
    get_consistency_manager,
)


class TestWithRetry:
    """Tests for retry decorator"""

    def test_success_on_first_attempt(self):
        """Should return result on first successful attempt"""
        call_count = [0]

        @with_retry(max_retries=3)
        def test_func():
            call_count[0] += 1
            return "success"

        result = test_func()

        assert result == "success"
        assert call_count[0] == 1

    def test_success_after_retry(self):
        """Should succeed after retrying"""
        call_count = [0]

        @with_retry(max_retries=3, base_delay=0.01)
        def test_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception(f"fail{call_count[0]}")
            return "success"

        result = test_func()

        assert result == "success"
        assert call_count[0] == 3

    def test_failure_after_max_retries(self):
        """Should raise exception after max retries"""
        call_count = [0]

        @with_retry(max_retries=3, base_delay=0.01)
        def test_func():
            call_count[0] += 1
            raise Exception("always fails")

        with pytest.raises(Exception, match="always fails"):
            test_func()

        assert call_count[0] == 3


class TestCompensatingAction:
    """Tests for CompensatingAction dataclass"""
    
    def test_creation(self):
        """Should create compensating action with defaults"""
        action = CompensatingAction(
            name="test_action",
            action=lambda: None
        )
        
        assert action.name == "test_action"
        assert action.args == ()
        assert action.kwargs == {}
        assert action.executed is False
    
    def test_with_args(self):
        """Should create with arguments"""
        action = CompensatingAction(
            name="delete_item",
            action=Mock(),
            args=("item_id",),
            kwargs={"force": True}
        )
        
        assert action.args == ("item_id",)
        assert action.kwargs == {"force": True}


class TestTransactionLog:
    """Tests for TransactionLog dataclass"""
    
    def test_creation(self):
        """Should create transaction log"""
        now = datetime.now(timezone.utc)
        log = TransactionLog(
            transaction_id="txn_abc123",
            operation_type="create_evidence",
            status=OperationStatus.PENDING,
            started_at=now
        )
        
        assert log.transaction_id == "txn_abc123"
        assert log.status == OperationStatus.PENDING
        assert log.completed_at is None
        assert log.error is None
        assert log.compensated_actions == []


class TestConsistencyManager:
    """Tests for ConsistencyManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create fresh manager for each test"""
        return ConsistencyManager()
    
    def test_generate_transaction_id(self, manager):
        """Should generate unique transaction IDs"""
        id1 = manager._generate_transaction_id()
        id2 = manager._generate_transaction_id()
        
        assert id1.startswith("txn_")
        assert id2.startswith("txn_")
        assert id1 != id2
    
    def test_log_transaction_limit(self, manager):
        """Should limit transaction logs to 1000 entries"""
        for i in range(1100):
            log = TransactionLog(
                transaction_id=f"txn_{i}",
                operation_type="test",
                status=OperationStatus.COMMITTED,
                started_at=datetime.now(timezone.utc)
            )
            manager._log_transaction(log)
        
        assert len(manager._transaction_logs) == 1000
        assert manager._transaction_logs[0].transaction_id == "txn_100"
    
    @patch('app.utils.consistency.dynamo')
    @patch('app.utils.consistency.qdrant')
    def test_create_evidence_success(self, mock_qdrant, mock_dynamo, manager):
        """Should create evidence in both DynamoDB and Qdrant"""
        mock_dynamo.put_evidence_metadata.return_value = {"id": "ev_1"}
        mock_qdrant.index_evidence_document.return_value = "qdrant_id_1"
        
        evidence_data = {
            "evidence_id": "ev_1",
            "case_id": "case_1",
            "type": "text"
        }
        document = {
            "content": "Test content"
        }
        
        result = manager.create_evidence_with_index(evidence_data, document)
        
        assert result is True
        mock_dynamo.put_evidence_metadata.assert_called_once_with(evidence_data)
        mock_qdrant.index_evidence_document.assert_called_once()
    
    @patch('app.utils.consistency.dynamo')
    def test_create_evidence_skip_qdrant(self, mock_dynamo, manager):
        """Should skip Qdrant when skip_qdrant=True"""
        mock_dynamo.put_evidence_metadata.return_value = {"id": "ev_1"}
        
        evidence_data = {
            "evidence_id": "ev_1",
            "case_id": "case_1"
        }
        document = {"content": "Test"}
        
        result = manager.create_evidence_with_index(
            evidence_data, document, skip_qdrant=True
        )
        
        assert result is True
        mock_dynamo.put_evidence_metadata.assert_called_once()
    
    @patch('app.utils.consistency.dynamo')
    @patch('app.utils.consistency.qdrant')
    def test_create_evidence_rollback_on_qdrant_failure(
        self, mock_qdrant, mock_dynamo, manager
    ):
        """Should rollback DynamoDB on Qdrant failure"""
        mock_dynamo.put_evidence_metadata.return_value = {"id": "ev_1"}
        mock_dynamo.delete_evidence_metadata.return_value = True
        mock_qdrant.index_evidence_document.side_effect = Exception("Qdrant error")
        
        evidence_data = {
            "evidence_id": "ev_1",
            "case_id": "case_1"
        }
        document = {"content": "Test"}
        
        with pytest.raises(ConsistencyError) as exc_info:
            manager.create_evidence_with_index(evidence_data, document)
        
        assert "Qdrant error" in str(exc_info.value)
        mock_dynamo.delete_evidence_metadata.assert_called_once_with("ev_1")
    
    @patch('app.utils.consistency.dynamo')
    @patch('app.utils.consistency.qdrant')
    def test_delete_evidence_success(self, mock_qdrant, mock_dynamo, manager):
        """Should delete from both stores"""
        mock_qdrant.get_qdrant_client.return_value = Mock()
        mock_dynamo.delete_evidence_metadata.return_value = True
        
        result = manager.delete_evidence_with_index("case_1", "ev_1")
        
        assert result is True
        mock_dynamo.delete_evidence_metadata.assert_called_once_with("ev_1")
    
    @patch('app.utils.consistency.dynamo')
    @patch('app.utils.consistency.qdrant')
    def test_delete_evidence_continues_on_qdrant_failure(
        self, mock_qdrant, mock_dynamo, manager
    ):
        """Should continue with DynamoDB even if Qdrant fails"""
        mock_qdrant.get_qdrant_client.side_effect = Exception("Qdrant unavailable")
        mock_dynamo.delete_evidence_metadata.return_value = True
        
        # Should not raise, Qdrant failure is non-critical for deletion
        result = manager.delete_evidence_with_index("case_1", "ev_1")
        
        assert result is True
    
    @patch('app.utils.consistency.dynamo')
    def test_update_evidence_not_found(self, mock_dynamo, manager):
        """Should raise error if evidence not found"""
        mock_dynamo.get_evidence_by_id.return_value = None
        
        with pytest.raises(ConsistencyError, match="not found"):
            manager.update_evidence_metadata(
                "ev_1", "case_1", {"status": "processed"}
            )
    
    @patch('app.utils.consistency.dynamo')
    def test_update_evidence_success(self, mock_dynamo, manager):
        """Should update evidence metadata"""
        mock_dynamo.get_evidence_by_id.return_value = {
            "evidence_id": "ev_1",
            "status": "pending"
        }
        mock_dynamo.update_evidence_status.return_value = True
        
        result = manager.update_evidence_metadata(
            "ev_1", "case_1", {"status": "processed"}
        )
        
        assert result is True
        mock_dynamo.update_evidence_status.assert_called_once()
    
    @patch('app.utils.consistency.dynamo')
    @patch('app.utils.consistency.qdrant')
    def test_clear_case_data_success(self, mock_qdrant, mock_dynamo, manager):
        """Should clear all case data from both stores"""
        mock_qdrant.delete_case_collection.return_value = True
        mock_dynamo.clear_case_evidence.return_value = 5
        
        result = manager.clear_case_data("case_1")
        
        assert result["dynamo_deleted"] == 5
        assert result["qdrant_deleted"] is True
        mock_qdrant.delete_case_collection.assert_called_once_with("case_1")
    
    @patch('app.utils.consistency.dynamo')
    @patch('app.utils.consistency.qdrant')
    def test_clear_case_data_skip_qdrant(self, mock_qdrant, mock_dynamo, manager):
        """Should skip Qdrant collection deletion when specified"""
        mock_dynamo.clear_case_evidence.return_value = 3
        
        result = manager.clear_case_data("case_1", delete_qdrant_collection=False)
        
        assert result["dynamo_deleted"] == 3
        assert result["qdrant_deleted"] is False
        mock_qdrant.delete_case_collection.assert_not_called()
    
    def test_get_recent_transactions(self, manager):
        """Should return recent transaction logs"""
        log = TransactionLog(
            transaction_id="txn_test",
            operation_type="test_op",
            status=OperationStatus.COMMITTED,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )
        manager._log_transaction(log)
        
        transactions = manager.get_recent_transactions(limit=10)
        
        assert len(transactions) == 1
        assert transactions[0]["transaction_id"] == "txn_test"
        assert transactions[0]["status"] == "committed"
    
    def test_execute_compensations(self, manager):
        """Should execute compensations in reverse order"""
        order = []
        
        compensations = [
            CompensatingAction(
                name="action_1",
                action=lambda: order.append(1)
            ),
            CompensatingAction(
                name="action_2",
                action=lambda: order.append(2)
            ),
            CompensatingAction(
                name="action_3",
                action=lambda: order.append(3)
            ),
        ]
        
        executed = manager._execute_compensations(compensations)
        
        assert order == [3, 2, 1]  # Reverse order
        assert len(executed) == 3
        assert all(c.executed for c in compensations)


class TestConsistencyError:
    """Tests for ConsistencyError exception"""
    
    def test_basic_error(self):
        """Should create basic error"""
        error = ConsistencyError("Test error")
        
        assert str(error) == "Test error"
        assert error.partial_success is False
        assert error.details == {}
    
    def test_error_with_details(self):
        """Should create error with details"""
        error = ConsistencyError(
            "Partial failure",
            partial_success=True,
            details={"failed_step": "qdrant_index"}
        )
        
        assert error.partial_success is True
        assert error.details["failed_step"] == "qdrant_index"


class TestGetConsistencyManager:
    """Tests for singleton accessor"""
    
    def test_returns_singleton(self):
        """Should return same instance"""
        import app.utils.consistency as consistency_module
        
        # Reset singleton for test
        consistency_module._consistency_manager = None
        
        manager1 = get_consistency_manager()
        manager2 = get_consistency_manager()
        
        assert manager1 is manager2
    
    def test_creates_instance_if_none(self):
        """Should create new instance if none exists"""
        import app.utils.consistency as consistency_module
        
        consistency_module._consistency_manager = None
        
        manager = get_consistency_manager()
        
        assert manager is not None
        assert isinstance(manager, ConsistencyManager)

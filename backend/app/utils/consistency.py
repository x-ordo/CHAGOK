"""
Consistency Manager for DynamoDB/Qdrant Operations

Implements Saga pattern for ensuring data consistency across DynamoDB and Qdrant
when operations need to succeed or fail atomically.

Key Features:
- Transaction-like operations across DynamoDB and Qdrant
- Automatic rollback on failure (compensation)
- Retry logic with exponential backoff
- Comprehensive logging for debugging

Usage:
    from app.utils.consistency import ConsistencyManager
    
    manager = ConsistencyManager()
    success = await manager.create_evidence_with_index(
        evidence_data={"id": "...", "case_id": "...", ...},
        document={"content": "...", ...}
    )
"""

import logging
from typing import Dict, Optional, List, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from functools import wraps
import time
import asyncio

from app.utils import dynamo, qdrant

logger = logging.getLogger(__name__)


class OperationStatus(Enum):
    """Status of a transactional operation"""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class CompensatingAction:
    """Represents a compensating action for rollback"""
    name: str
    action: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    executed: bool = False


@dataclass
class TransactionLog:
    """Log entry for transaction tracking"""
    transaction_id: str
    operation_type: str
    status: OperationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    compensated_actions: List[str] = field(default_factory=list)


class ConsistencyError(Exception):
    """Raised when consistency cannot be guaranteed"""
    def __init__(self, message: str, partial_success: bool = False, details: Dict = None):
        super().__init__(message)
        self.partial_success = partial_success
        self.details = details or {}


def with_retry(max_retries: int = 3, base_delay: float = 0.5):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}. "
                            f"Waiting {delay}s..."
                        )
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


class ConsistencyManager:
    """
    Manages consistency between DynamoDB and Qdrant operations.
    
    Implements Saga pattern for distributed transactions:
    1. Execute primary operations
    2. Track compensating actions for rollback
    3. On failure, execute compensations in reverse order
    """
    
    def __init__(self):
        self._transaction_logs: List[TransactionLog] = []
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        import uuid
        return f"txn_{uuid.uuid4().hex[:12]}"
    
    def _log_transaction(self, log: TransactionLog):
        """Store transaction log (in-memory, could be persisted)"""
        self._transaction_logs.append(log)
        if len(self._transaction_logs) > 1000:
            # Keep only last 1000 entries
            self._transaction_logs = self._transaction_logs[-1000:]
    
    @with_retry(max_retries=3)
    def _dynamo_put(self, evidence_data: Dict) -> Dict:
        """Put evidence to DynamoDB with retry"""
        return dynamo.put_evidence_metadata(evidence_data)
    
    @with_retry(max_retries=3)
    def _dynamo_delete(self, evidence_id: str) -> bool:
        """Delete evidence from DynamoDB with retry"""
        return dynamo.delete_evidence_metadata(evidence_id)
    
    @with_retry(max_retries=3)
    def _qdrant_index(self, case_id: str, document: Dict) -> str:
        """Index document in Qdrant with retry"""
        return qdrant.index_evidence_document(case_id, document)
    
    @with_retry(max_retries=2)
    def _qdrant_delete(self, case_id: str, evidence_id: str) -> bool:
        """Delete document from Qdrant with retry"""
        # Use filter-based deletion for Qdrant
        try:
            client = qdrant.get_qdrant_client()
            collection_name = qdrant._get_collection_name(case_id)
            
            from qdrant_client.http import models
            
            # Delete by evidence_id in payload
            client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="evidence_id",
                                match=models.MatchValue(value=evidence_id)
                            )
                        ]
                    )
                )
            )
            return True
        except Exception as e:
            logger.warning(f"Qdrant delete failed for {evidence_id}: {e}")
            return False
    
    def _execute_compensations(self, compensations: List[CompensatingAction]) -> List[str]:
        """Execute compensating actions in reverse order"""
        executed = []
        for comp in reversed(compensations):
            if not comp.executed:
                try:
                    comp.action(*comp.args, **comp.kwargs)
                    comp.executed = True
                    executed.append(comp.name)
                    logger.info(f"Compensation executed: {comp.name}")
                except Exception as e:
                    logger.error(f"Compensation failed: {comp.name} - {e}")
        return executed
    
    def create_evidence_with_index(
        self,
        evidence_data: Dict,
        document: Dict,
        skip_qdrant: bool = False
    ) -> bool:
        """
        Create evidence in DynamoDB and index in Qdrant atomically.
        
        Args:
            evidence_data: Evidence metadata for DynamoDB
            document: Document for Qdrant indexing
            skip_qdrant: If True, skip Qdrant indexing (for cases without vector needs)
        
        Returns:
            True if both operations succeeded
        
        Raises:
            ConsistencyError: If operations fail and cannot be rolled back
        """
        txn_id = self._generate_transaction_id()
        case_id = evidence_data.get("case_id")
        evidence_id = evidence_data.get("evidence_id") or evidence_data.get("id")
        
        log = TransactionLog(
            transaction_id=txn_id,
            operation_type="create_evidence_with_index",
            status=OperationStatus.PENDING,
            started_at=datetime.now(timezone.utc)
        )
        
        compensations: List[CompensatingAction] = []
        
        try:
            # Step 1: Create in DynamoDB
            logger.info(f"[{txn_id}] Creating evidence {evidence_id} in DynamoDB...")
            self._dynamo_put(evidence_data)
            
            # Register compensation for DynamoDB
            compensations.append(CompensatingAction(
                name=f"delete_dynamo_{evidence_id}",
                action=self._dynamo_delete,
                args=(evidence_id,)
            ))
            
            # Step 2: Index in Qdrant (if not skipped)
            if not skip_qdrant and case_id:
                logger.info(f"[{txn_id}] Indexing evidence {evidence_id} in Qdrant...")
                
                # Ensure document has required fields
                doc_for_index = document.copy()
                doc_for_index["evidence_id"] = evidence_id
                doc_for_index["case_id"] = case_id
                
                self._qdrant_index(case_id, doc_for_index)
                
                # Register compensation for Qdrant
                compensations.append(CompensatingAction(
                    name=f"delete_qdrant_{evidence_id}",
                    action=self._qdrant_delete,
                    args=(case_id, evidence_id)
                ))
            
            # Success
            log.status = OperationStatus.COMMITTED
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            logger.info(f"[{txn_id}] Transaction committed successfully")
            return True
            
        except Exception as e:
            # Failure - execute compensations
            logger.error(f"[{txn_id}] Transaction failed: {e}. Executing compensations...")
            
            compensated = self._execute_compensations(compensations)
            
            log.status = OperationStatus.ROLLED_BACK if compensated else OperationStatus.FAILED
            log.error = str(e)
            log.compensated_actions = compensated
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            raise ConsistencyError(
                f"Evidence creation failed: {e}",
                partial_success=False,
                details={
                    "transaction_id": txn_id,
                    "compensated_actions": compensated
                }
            )
    
    def delete_evidence_with_index(
        self,
        case_id: str,
        evidence_id: str
    ) -> bool:
        """
        Delete evidence from DynamoDB and Qdrant atomically.
        
        Deletion follows: Qdrant first (less critical), then DynamoDB
        
        Args:
            case_id: Case ID
            evidence_id: Evidence ID to delete
        
        Returns:
            True if both operations succeeded
        """
        txn_id = self._generate_transaction_id()
        
        log = TransactionLog(
            transaction_id=txn_id,
            operation_type="delete_evidence_with_index",
            status=OperationStatus.PENDING,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            # Step 1: Delete from Qdrant first (non-critical, best effort)
            logger.info(f"[{txn_id}] Deleting evidence {evidence_id} from Qdrant...")
            qdrant_success = self._qdrant_delete(case_id, evidence_id)
            if not qdrant_success:
                logger.warning(f"[{txn_id}] Qdrant deletion failed, continuing with DynamoDB...")
            
            # Step 2: Delete from DynamoDB (critical)
            logger.info(f"[{txn_id}] Deleting evidence {evidence_id} from DynamoDB...")
            self._dynamo_delete(evidence_id)
            
            # Success
            log.status = OperationStatus.COMMITTED
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            logger.info(f"[{txn_id}] Delete transaction committed successfully")
            return True
            
        except Exception as e:
            logger.error(f"[{txn_id}] Delete transaction failed: {e}")
            
            log.status = OperationStatus.FAILED
            log.error = str(e)
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            raise ConsistencyError(
                f"Evidence deletion failed: {e}",
                partial_success=True,  # Qdrant might have been deleted
                details={"transaction_id": txn_id}
            )
    
    def update_evidence_metadata(
        self,
        evidence_id: str,
        case_id: str,
        updates: Dict,
        reindex: bool = False
    ) -> bool:
        """
        Update evidence metadata in DynamoDB and optionally reindex in Qdrant.
        
        Args:
            evidence_id: Evidence ID
            case_id: Case ID
            updates: Fields to update
            reindex: If True, reindex in Qdrant with new content
        
        Returns:
            True if update succeeded
        """
        txn_id = self._generate_transaction_id()
        
        log = TransactionLog(
            transaction_id=txn_id,
            operation_type="update_evidence_metadata",
            status=OperationStatus.PENDING,
            started_at=datetime.now(timezone.utc)
        )
        
        # Get current state for potential rollback
        current_evidence = dynamo.get_evidence_by_id(evidence_id)
        if not current_evidence:
            raise ConsistencyError(f"Evidence {evidence_id} not found")
        
        compensations: List[CompensatingAction] = []
        
        try:
            # Step 1: Update DynamoDB
            logger.info(f"[{txn_id}] Updating evidence {evidence_id} in DynamoDB...")
            
            success = dynamo.update_evidence_status(
                evidence_id=evidence_id,
                status=updates.get("status", current_evidence.get("status", "pending")),
                additional_fields={k: v for k, v in updates.items() if k != "status"}
            )
            
            if not success:
                raise Exception("DynamoDB update failed")
            
            # Register compensation with original values
            compensations.append(CompensatingAction(
                name=f"restore_dynamo_{evidence_id}",
                action=lambda: dynamo.put_evidence_metadata(current_evidence),
                args=()
            ))
            
            # Step 2: Reindex in Qdrant if requested
            if reindex and updates.get("content"):
                logger.info(f"[{txn_id}] Reindexing evidence {evidence_id} in Qdrant...")
                
                updated_evidence = dynamo.get_evidence_by_id(evidence_id)
                doc = {
                    "evidence_id": evidence_id,
                    "case_id": case_id,
                    "content": updates["content"],
                    **{k: v for k, v in updated_evidence.items() if k not in ["content", "vector"]}
                }
                
                self._qdrant_index(case_id, doc)
            
            # Success
            log.status = OperationStatus.COMMITTED
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            logger.info(f"[{txn_id}] Update transaction committed successfully")
            return True
            
        except Exception as e:
            logger.error(f"[{txn_id}] Update transaction failed: {e}. Executing compensations...")
            
            compensated = self._execute_compensations(compensations)
            
            log.status = OperationStatus.ROLLED_BACK if compensated else OperationStatus.FAILED
            log.error = str(e)
            log.compensated_actions = compensated
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            raise ConsistencyError(
                f"Evidence update failed: {e}",
                details={"transaction_id": txn_id, "compensated_actions": compensated}
            )
    
    def clear_case_data(
        self,
        case_id: str,
        delete_qdrant_collection: bool = True
    ) -> Dict[str, int]:
        """
        Clear all evidence data for a case from both DynamoDB and Qdrant.
        
        Used when case is closed/deleted.
        
        Args:
            case_id: Case ID
            delete_qdrant_collection: If True, delete entire Qdrant collection
        
        Returns:
            Dict with counts: {"dynamo_deleted": N, "qdrant_deleted": bool}
        """
        txn_id = self._generate_transaction_id()
        
        log = TransactionLog(
            transaction_id=txn_id,
            operation_type="clear_case_data",
            status=OperationStatus.PENDING,
            started_at=datetime.now(timezone.utc)
        )
        
        result = {"dynamo_deleted": 0, "qdrant_deleted": False}
        
        try:
            # Step 1: Delete Qdrant collection (entire collection, not individual docs)
            if delete_qdrant_collection:
                logger.info(f"[{txn_id}] Deleting Qdrant collection for case {case_id}...")
                result["qdrant_deleted"] = qdrant.delete_case_collection(case_id)
            
            # Step 2: Clear DynamoDB evidence
            logger.info(f"[{txn_id}] Clearing DynamoDB evidence for case {case_id}...")
            result["dynamo_deleted"] = dynamo.clear_case_evidence(case_id)
            
            # Success
            log.status = OperationStatus.COMMITTED
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            logger.info(
                f"[{txn_id}] Case data cleared: "
                f"DynamoDB={result['dynamo_deleted']}, Qdrant={result['qdrant_deleted']}"
            )
            return result
            
        except Exception as e:
            logger.error(f"[{txn_id}] Case data clearing failed: {e}")
            
            log.status = OperationStatus.FAILED
            log.error = str(e)
            log.completed_at = datetime.now(timezone.utc)
            self._log_transaction(log)
            
            raise ConsistencyError(
                f"Case data clearing failed: {e}",
                partial_success=result["qdrant_deleted"] or result["dynamo_deleted"] > 0,
                details={"transaction_id": txn_id, "partial_result": result}
            )
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Get recent transaction logs for monitoring/debugging"""
        return [
            {
                "transaction_id": log.transaction_id,
                "operation_type": log.operation_type,
                "status": log.status.value,
                "started_at": log.started_at.isoformat(),
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "error": log.error,
                "compensated_actions": log.compensated_actions
            }
            for log in self._transaction_logs[-limit:]
        ]


# Global singleton instance
_consistency_manager: Optional[ConsistencyManager] = None


def get_consistency_manager() -> ConsistencyManager:
    """Get or create singleton ConsistencyManager instance"""
    global _consistency_manager
    if _consistency_manager is None:
        _consistency_manager = ConsistencyManager()
    return _consistency_manager

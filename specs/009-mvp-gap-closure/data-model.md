# Data Model: MVP 구현 갭 해소

**Feature**: 009-mvp-gap-closure
**Date**: 2025-12-09
**Status**: Complete

## Overview

This feature uses existing data models. No new entities are required.
This document serves as reference for the key entities involved.

---

## 1. Evidence (DynamoDB)

### Storage
- **Table**: `leh_evidence_{env}` (e.g., `leh_evidence_dev`)
- **Partition Key**: `case_id`
- **Sort Key**: `evidence_id`

### Schema

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | String | Parent case identifier (FK) |
| `evidence_id` | String | Unique evidence identifier |
| `type` | Enum | `image`, `audio`, `video`, `text`, `pdf` |
| `file_name` | String | Original file name |
| `s3_key` | String | S3 object path |
| `sha256` | String | File content hash for integrity |
| `timestamp` | ISO8601 | Evidence collection timestamp |
| `speaker` | String | `원고`, `피고`, `제3자` |
| `ai_summary` | String | AI-generated summary |
| `labels` | List[String] | `폭언`, `불륜`, `유책사유` etc. |
| `article_840_tags` | Object | Legal article tagging results |
| `evidence_score` | Float | AI-assigned evidence strength (0-1) |
| `qdrant_id` | String | Vector ID in Qdrant |
| `status` | Enum | `pending`, `processing`, `completed`, `failed` |
| `created_at` | ISO8601 | Record creation time |
| `updated_at` | ISO8601 | Last update time |

### GSI (Global Secondary Index)
- **GSI1**: `type-timestamp-index` (Query by type)
- **GSI2**: `status-created_at-index` (Query pending items)

### Validation Rules
- `case_id` must exist in RDS cases table
- `sha256` computed on upload, immutable
- `status` transitions: `pending` → `processing` → `completed|failed`

---

## 2. AuditLog (PostgreSQL/RDS)

### Location
- **Table**: `audit_logs`
- **Database**: PostgreSQL (RDS)

### Schema

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)  # Additional context
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
```

### Action Types (AuditAction Enum)

| Action | Description | Resource Type |
|--------|-------------|---------------|
| `VIEW_CASE` | User viewed case | `case` |
| `CREATE_CASE` | User created case | `case` |
| `UPDATE_CASE` | User modified case | `case` |
| `DELETE_CASE` | User deleted case | `case` |
| `VIEW_EVIDENCE` | User viewed evidence | `evidence` |
| `UPLOAD_EVIDENCE` | User uploaded evidence | `evidence` |
| `GENERATE_DRAFT` | User requested draft | `draft` |
| `EXPORT_DRAFT` | User exported draft | `draft` |
| `ACCESS_DENIED` | Unauthorized access attempt | `*` |
| `LOGIN` | User logged in | `auth` |
| `LOGOUT` | User logged out | `auth` |

### Indexes
- `ix_audit_logs_user_id` - Query by user
- `ix_audit_logs_action` - Query by action type
- `ix_audit_logs_resource_type` - Query by resource
- `ix_audit_logs_created_at` - Time-range queries

### Compliance Notes
- **Immutable**: No UPDATE or DELETE operations allowed
- **Retention**: 7 years minimum for legal compliance
- **IP Logging**: For evidence chain of custody

---

## 3. CaseMember (PostgreSQL/RDS)

### Location
- **Table**: `case_members`
- **Database**: PostgreSQL (RDS)

### Schema

```python
class CaseMember(Base):
    __tablename__ = "case_members"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    case_id = Column(UUID, ForeignKey("cases.id"), nullable=False, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(Enum(CaseMemberRole), nullable=False)
    added_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
```

### Role Types (CaseMemberRole Enum)

| Role | Permissions | Description |
|------|-------------|-------------|
| `OWNER` | Full access | Case creator, can delete |
| `MEMBER` | Read/Write | Can edit evidence, drafts |
| `VIEWER` | Read only | Can only view |

### Unique Constraint
- `(case_id, user_id)` - User can only have one role per case

### Business Rules
- Every case must have at least one `OWNER`
- `OWNER` cannot demote themselves if only owner
- Case access requires membership (403 otherwise)

---

## 4. Qdrant Vector Collection

### Naming Convention
- **Pattern**: `case_rag_{case_id}`
- **Example**: `case_rag_550e8400-e29b-41d4-a716-446655440000`

### Vector Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique vector ID |
| `vector` | Float[1536] | OpenAI text-embedding-3-small |
| `payload.evidence_id` | String | Source evidence ID |
| `payload.case_id` | String | Parent case ID |
| `payload.chunk_text` | String | Text chunk (max 8000 chars) |
| `payload.chunk_index` | Integer | Position in document |
| `payload.file_name` | String | Source file name |
| `payload.timestamp` | ISO8601 | Evidence timestamp |
| `payload.speaker` | String | Speaker attribution |
| `payload.labels` | List[String] | Evidence labels |

### Payload Indexes (for filtering)
- `evidence_id` - Text index
- `speaker` - Keyword index
- `labels` - Keyword list index
- `timestamp` - Integer index (unix epoch)

### Collection Lifecycle
1. **Created**: When first evidence uploaded to case
2. **Updated**: On each evidence analysis completion
3. **Deleted**: On case closure (soft delete in RDS triggers)

---

## Entity Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│                         PostgreSQL (RDS)                         │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────┐     ┌─────────────┐     ┌────────────┐              │
│  │  User   │────▶│ CaseMember  │◀────│    Case    │              │
│  └─────────┘     └─────────────┘     └────────────┘              │
│       │                                     │                     │
│       │                                     │                     │
│       ▼                                     │                     │
│  ┌──────────┐                               │                     │
│  │ AuditLog │◀──────────────────────────────┘                     │
│  └──────────┘                                                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                           DynamoDB                               │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Evidence (PK: case_id, SK: evidence_id)                  │    │
│  │   - Metadata, AI analysis results, status                │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         Qdrant Cloud                             │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ case_rag_{case_id}                                       │    │
│  │   - Embedding vectors + payload metadata                 │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                            AWS S3                                │
├──────────────────────────────────────────────────────────────────┤
│  s3://leh-evidence-{env}/                                        │
│    └── cases/{case_id}/                                          │
│        └── raw/{evidence_id}_{filename}                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## State Transitions

### Evidence Processing States

```
┌─────────┐     ┌────────────┐     ┌───────────┐
│ pending │────▶│ processing │────▶│ completed │
└─────────┘     └────────────┘     └───────────┘
                      │
                      ▼
                ┌──────────┐
                │  failed  │
                └──────────┘
```

### Case Status States

```
┌──────┐     ┌─────────────┐     ┌────────┐
│ open │────▶│ in_progress │────▶│ closed │
└──────┘     └─────────────┘     └────────┘
```

---

## 5. DetectiveEarnings (PostgreSQL/RDS) - NEW (US11)

### Location
- **Table**: `detective_earnings`
- **Database**: PostgreSQL (RDS)

### Schema

```python
class DetectiveEarnings(Base):
    __tablename__ = "detective_earnings"

    id = Column(UUID, primary_key=True, default=uuid4)
    detective_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    case_id = Column(UUID, ForeignKey("cases.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(Enum(EarningsStatus), default='pending')  # pending, paid
    created_at = Column(DateTime, default=func.now())
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    detective = relationship("User", foreign_keys=[detective_id])
    case = relationship("Case", foreign_keys=[case_id])
```

### Status Types (EarningsStatus Enum)

| Status | Description |
|--------|-------------|
| `pending` | Earnings recorded, awaiting payment |
| `paid` | Payment completed |

### Indexes
- `ix_detective_earnings_detective_id` - Query by detective
- `ix_detective_earnings_case_id` - Query by case
- `ix_detective_earnings_status` - Filter by payment status

---

## 6. Evidence Status Extension (US10)

### Additional Fields for Evidence (DynamoDB)

| Field | Type | Description |
|-------|------|-------------|
| `review_status` | Enum | `pending_review`, `approved`, `rejected` |
| `uploaded_by` | String | User ID who uploaded (client vs lawyer) |
| `reviewed_by` | String | User ID who approved/rejected |
| `reviewed_at` | ISO8601 | Review decision timestamp |

### Review Status State Machine

```
Client Upload → pending_review
                    ↓
        Lawyer Review Decision
            ↓           ↓
        approved    rejected

Lawyer Upload → approved (auto-approved)
```

### Business Rules
- Client uploads default to `pending_review`
- Lawyer uploads default to `approved`
- Only case OWNER/MEMBER can review
- Review changes are logged in audit_logs

---

## 7. User Role Extension (US9)

### Existing UserRole Enum

```python
class UserRole(str, enum.Enum):
    LAWYER = "lawyer"
    STAFF = "staff"
    ADMIN = "admin"
    CLIENT = "client"       # 의뢰인
    DETECTIVE = "detective" # 탐정/조사원
```

### Self-Signup Roles
Only these roles can self-register:
- `LAWYER`
- `CLIENT`
- `DETECTIVE`

Staff and Admin require invitation.

### Role-Based Dashboard Mapping

| Role | Dashboard Path |
|------|---------------|
| `lawyer` | `/lawyer/dashboard` |
| `client` | `/client/dashboard` |
| `detective` | `/detective/dashboard` |
| `staff` | `/lawyer/dashboard` (same as lawyer) |
| `admin` | `/admin/dashboard` |

---

## Migration Notes

### New Migration Required: detective_earnings

```python
# alembic/versions/xxx_add_detective_earnings.py
def upgrade():
    op.create_table(
        'detective_earnings',
        sa.Column('id', UUID(), primary_key=True),
        sa.Column('detective_id', UUID(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('case_id', UUID(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('status', sa.Enum('pending', 'paid', name='earningsstatus'), default='pending'),
        sa.Column('created_at', sa.DateTime(), default=func.now()),
        sa.Column('paid_at', sa.DateTime()),
    )
    op.create_index('ix_detective_earnings_detective_id', 'detective_earnings', ['detective_id'])
    op.create_index('ix_detective_earnings_case_id', 'detective_earnings', ['case_id'])

def downgrade():
    op.drop_table('detective_earnings')
```

### Existing Tables - No Migration Needed

### Verification Queries

```sql
-- Verify AuditLog table exists
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'audit_logs';

-- Verify CaseMember roles
SELECT DISTINCT role FROM case_members;

-- Count existing audit logs
SELECT COUNT(*) FROM audit_logs;
```

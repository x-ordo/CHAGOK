"""Add civil_code_ref and typical_evidence_types to lssp_legal_grounds

Revision ID: lssp_003_civil_code_ref
Revises: lssp_002_keypoint_pipeline
Create Date: 2025-12-19

Adds:
- civil_code_ref: Korean civil code reference (e.g., "민법 제840조 제1호")
- typical_evidence_types: JSON array of typical evidence types for this ground
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'lssp_003_civil_code_ref'
down_revision: Union[str, None] = 'lssp_002_keypoint_pipeline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add civil_code_ref and typical_evidence_types columns to lssp_legal_grounds."""
    # Add civil_code_ref column
    op.add_column('lssp_legal_grounds',
        sa.Column('civil_code_ref', sa.String(length=100), nullable=True)
    )

    # Add typical_evidence_types column (JSON array)
    op.add_column('lssp_legal_grounds',
        sa.Column('typical_evidence_types', sa.JSON(), nullable=False, server_default='[]')
    )


def downgrade() -> None:
    """Remove civil_code_ref and typical_evidence_types columns."""
    op.drop_column('lssp_legal_grounds', 'typical_evidence_types')
    op.drop_column('lssp_legal_grounds', 'civil_code_ref')

"""merge_lssp003_and_cascade_delete

Revision ID: 724a7e3ccf5e
Revises: 011b_cascade_delete, lssp_003_civil_code_ref
Create Date: 2025-12-19 17:11:48.356988

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '724a7e3ccf5e'
down_revision: Union[str, Sequence[str], None] = ('011b_cascade_delete', 'lssp_003_civil_code_ref')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

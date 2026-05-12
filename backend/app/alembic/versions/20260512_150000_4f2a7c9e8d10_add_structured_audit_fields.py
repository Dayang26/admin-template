"""add structured audit fields

Revision ID: 4f2a7c9e8d10
Revises: 2e9d5f5e0c41
Create Date: 2026-05-12 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f2a7c9e8d10"
down_revision: str | Sequence[str] | None = "2e9d5f5e0c41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("t_audit_log", sa.Column("resource_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True))
    op.add_column("t_audit_log", sa.Column("resource_id", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True))
    op.add_column("t_audit_log", sa.Column("changes", sa.JSON(), nullable=True))
    op.create_index("ix_audit_log_resource", "t_audit_log", ["resource_type", "resource_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_audit_log_resource", table_name="t_audit_log")
    op.drop_column("t_audit_log", "changes")
    op.drop_column("t_audit_log", "resource_id")
    op.drop_column("t_audit_log", "resource_type")

"""add user avatar upload reference

Revision ID: 2e9d5f5e0c41
Revises: 7b63a4d2f911
Create Date: 2026-05-12 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e9d5f5e0c41"
down_revision: str | Sequence[str] | None = "7b63a4d2f911"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("t_user", sa.Column("avatar_file_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_user_avatar_file_id_upload_file",
        "t_user",
        "t_upload_file",
        ["avatar_file_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_user_avatar_file_id_upload_file", "t_user", type_="foreignkey")
    op.drop_column("t_user", "avatar_file_id")

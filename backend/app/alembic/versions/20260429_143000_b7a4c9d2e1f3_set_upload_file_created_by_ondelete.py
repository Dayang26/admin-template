"""set upload_file created_by_id on delete set null

Revision ID: b7a4c9d2e1f3
Revises: ea0d5c6d048d
Create Date: 2026-04-29 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b7a4c9d2e1f3"
down_revision: Union[str, Sequence[str], None] = "ea0d5c6d048d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("t_upload_file_created_by_id_fkey", "t_upload_file", type_="foreignkey")
    op.create_foreign_key(
        "fk_upload_file_created_by_id_user",
        "t_upload_file",
        "t_user",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_upload_file_created_by_id_user", "t_upload_file", type_="foreignkey")
    op.create_foreign_key(
        "t_upload_file_created_by_id_fkey",
        "t_upload_file",
        "t_user",
        ["created_by_id"],
        ["id"],
    )

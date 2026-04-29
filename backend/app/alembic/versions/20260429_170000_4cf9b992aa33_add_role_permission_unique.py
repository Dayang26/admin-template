"""add role permission unique constraint

Revision ID: 4cf9b992aa33
Revises: 9e422d11bdee
Create Date: 2026-04-29 17:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "4cf9b992aa33"
down_revision: str | Sequence[str] | None = "9e422d11bdee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    inspector = inspect(op.get_bind())
    system_setting_columns = {column["name"] for column in inspector.get_columns("t_system_setting")}
    obsolete_columns = [
        "primary_color",
        "theme_mode",
        "layout_mode",
        "menu_collapsed_default",
        "fixed_header",
        "fixed_sidebar",
        "page_animation_enabled",
        "default_home_path",
        "tab_view_enabled",
        "route_cache_enabled",
        "request_timeout_ms",
    ]
    with op.batch_alter_table("t_system_setting") as batch_op:
        for column_name in obsolete_columns:
            if column_name in system_setting_columns:
                batch_op.drop_column(column_name)

    op.execute(
        """
        DELETE FROM t_role_permission a
        USING t_role_permission b
        WHERE a.role_id = b.role_id
          AND a.permission_id = b.permission_id
          AND a.id > b.id
        """
    )
    op.create_unique_constraint("uq_role_permission", "t_role_permission", ["role_id", "permission_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_role_permission", "t_role_permission", type_="unique")

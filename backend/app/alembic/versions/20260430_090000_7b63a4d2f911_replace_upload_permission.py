"""replace generic upload permission

Revision ID: 7b63a4d2f911
Revises: 4cf9b992aa33
Create Date: 2026-04-30 09:00:00.000000

"""

from collections.abc import Sequence

import uuid

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "7b63a4d2f911"
down_revision: str | Sequence[str] | None = "4cf9b992aa33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove the obsolete generic upload permission from existing databases."""
    op.execute(
        """
        DELETE FROM t_role_permission
        WHERE permission_id IN (
            SELECT id FROM t_permission
            WHERE (resource = 'upload' AND action = 'create')
               OR (resource = 'system_setting' AND action = 'update')
               OR resource IN (
                    'system_setting_logo',
                    'system_setting_favicon',
                    'system_setting_login_background'
                )
        )
        """
    )
    op.execute("DELETE FROM t_permission WHERE resource = 'upload' AND action = 'create'")
    op.execute("DELETE FROM t_permission WHERE resource = 'system_setting' AND action = 'update'")
    op.execute(
        """
        DELETE FROM t_permission
        WHERE resource IN (
            'system_setting_logo',
            'system_setting_favicon',
            'system_setting_login_background'
        )
        """
    )


def downgrade() -> None:
    """Restore the generic upload permission row without role bindings."""
    op.get_bind().execute(
        text(
            """
        INSERT INTO t_permission (id, resource, action)
        SELECT :id, 'upload', 'create'
        WHERE NOT EXISTS (
            SELECT 1 FROM t_permission
            WHERE resource = 'upload' AND action = 'create'
        )
        """
        ),
        {"id": uuid.uuid4()},
    )

"""Enforce journal ownership at database level.

Revision ID: b46o001
Revises: ad05cd2c705d
"""
from alembic import op
import sqlalchemy as sa

revision = "b46o001"
down_revision = "ad05cd2c705d"
branch_labels = None
depends_on = None


def _check_orphans():
    bind = op.get_bind()
    count = bind.execute(sa.text("""
        SELECT COUNT(*) FROM journals AS j
        LEFT JOIN users AS u ON j.user_id = u.id
        WHERE u.id IS NULL
    """)).scalar_one()
    if count:
        raise RuntimeError(
            f"Migration stopped: {count} journal(s) reference missing users. "
            "Back up and reconcile ownership before migrating; no records were changed."
        )


def upgrade():
    _check_orphans()
    with op.batch_alter_table("journals", recreate="always") as batch:
        batch.create_foreign_key("fk_journals_user_id_users", "users", ["user_id"], ["id"], ondelete="RESTRICT")


def downgrade():
    with op.batch_alter_table("journals", recreate="always") as batch:
        batch.drop_constraint("fk_journals_user_id_users", type_="foreignkey")

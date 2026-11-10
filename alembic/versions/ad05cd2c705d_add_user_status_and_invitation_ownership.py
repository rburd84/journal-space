"""add user status and invitation ownership

Revision ID: ad05cd2c705d
Revises: a600fa42c2a9
Create Date: 2026-11-09 00:12:40.310375

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ad05cd2c705d'
down_revision: Union[str, Sequence[str], None] = 'a600fa42c2a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }
    invitation_columns = {
        column["name"]
        for column in inspector.get_columns("invitations")
    }

    if "is_active" not in user_columns:
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "is_active",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.true(),
                )
            )

    if "redeemed_by_user_id" not in invitation_columns:
        with op.batch_alter_table("invitations") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "redeemed_by_user_id",
                    sa.Uuid(),
                    nullable=True,
                )
            )

    with op.batch_alter_table("invitations") as batch_op:
        batch_op.create_foreign_key(
            "fk_invitations_redeemed_by_user_id",
            "users",
            ["redeemed_by_user_id"],
            ["id"],
        )
        batch_op.create_unique_constraint(
            "uq_invitations_redeemed_by_user_id",
            ["redeemed_by_user_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.drop_constraint(
            "uq_invitations_redeemed_by_user_id",
            type_="unique",
        )
        batch_op.drop_constraint(
            "fk_invitations_redeemed_by_user_id",
            type_="foreignkey",
        )
        batch_op.drop_column("redeemed_by_user_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_active")

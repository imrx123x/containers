"""add token_version to users

Revision ID: 0005_add_token_version_to_users
Revises: 0004_add_updated_at_trigger
Create Date: 2026-04-23
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_token_version_to_users"
down_revision = "0004_add_updated_at_trigger"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.execute(
        """
        UPDATE users
        SET token_version = 0
        WHERE token_version IS NULL;
        """
    )


def downgrade():
    op.drop_column("users", "token_version")
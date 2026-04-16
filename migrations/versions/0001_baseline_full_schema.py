"""baseline full schema (users + audit_logs)

Revision ID: 0001_baseline_full_schema
Revises: None
Create Date: 2026-04-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_baseline_full_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # USERS TABLE
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
    )

    # UNIQUE INDEX ON EMAIL (LOWERCASE, ONLY ACTIVE USERS)
    op.execute(
        """
        CREATE UNIQUE INDEX users_email_unique_idx
        ON users (LOWER(email))
        WHERE email IS NOT NULL AND deleted_at IS NULL;
        """
    )

    # AUDIT LOGS TABLE
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("target_email", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade():
    op.drop_table("audit_logs")
    op.execute("DROP INDEX IF EXISTS users_email_unique_idx;")
    op.drop_table("users")
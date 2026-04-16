"""add indexes for users trash and audit logs

Revision ID: 0002_add_indexes
Revises: 0001_baseline_full_schema
Create Date: 2026-04-16
"""

from alembic import op


revision = "0002_add_indexes"
down_revision = "0001_baseline_full_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS users_deleted_at_idx
        ON users (deleted_at);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS audit_logs_created_at_idx
        ON audit_logs (created_at DESC);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS audit_logs_target_user_id_idx
        ON audit_logs (target_user_id);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS audit_logs_target_user_id_idx;")
    op.execute("DROP INDEX IF EXISTS audit_logs_created_at_idx;")
    op.execute("DROP INDEX IF EXISTS users_deleted_at_idx;")
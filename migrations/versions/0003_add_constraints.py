"""add users data constraints

Revision ID: 0003_add_constraints
Revises: 0002_add_indexes
Create Date: 2026-04-16
"""

from alembic import op


revision = "0003_add_constraints"
down_revision = "0002_add_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE users
        ADD CONSTRAINT users_role_check
        CHECK (role IN ('admin', 'user'));
    """)

    op.execute("""
        ALTER TABLE users
        ADD CONSTRAINT users_name_not_blank_check
        CHECK (length(btrim(name)) > 0);
    """)


def downgrade():
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_name_not_blank_check;")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;")
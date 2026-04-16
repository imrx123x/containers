"""add trigger for automatic users.updated_at

Revision ID: 0004_add_updated_at_trigger
Revises: 0003_add_constraints
Create Date: 2026-04-16
"""

from alembic import op


revision = "0004_add_updated_at_trigger"
down_revision = "0003_add_constraints"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        DROP TRIGGER IF EXISTS users_set_updated_at ON users;
    """)

    op.execute("""
        CREATE TRIGGER users_set_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
    """)


def downgrade():
    op.execute("""
        DROP TRIGGER IF EXISTS users_set_updated_at ON users;
    """)

    op.execute("""
        DROP FUNCTION IF EXISTS set_updated_at();
    """)
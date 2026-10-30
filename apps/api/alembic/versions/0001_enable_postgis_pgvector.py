"""TASK-006: Enable postgis and pgvector extensions

Revision ID: 0001
Revises: None
Create Date: 2026-10-30 14:30:00.000000

"""
from alembic import op

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("DROP EXTENSION IF EXISTS vector;")
        op.execute("DROP EXTENSION IF EXISTS postgis;")


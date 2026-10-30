"""TASK-007: Create Civic Enums

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-30 14:31:00.000000

"""
from alembic import op

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("CREATE TYPE lifecycle_status_enum AS ENUM ('Submitted', 'Under Review', 'Assigned', 'Resolved');")
        op.execute("CREATE TYPE priority_rank_enum AS ENUM ('Priority 1', 'Priority 2', 'Priority 3', 'Priority 4');")
        op.execute("CREATE TYPE category_enum AS ENUM ('Waterlogging & Drainage', 'Road Failure & Potholes', 'Waste Management', 'Street Lighting', 'Public Utilities');")

def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS category_enum;")
        op.execute("DROP TYPE IF EXISTS priority_rank_enum;")
        op.execute("DROP TYPE IF EXISTS lifecycle_status_enum;")


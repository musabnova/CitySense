"""TASK-011: Create Spatial, Vector and Composite Indexes

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-30 14:35:00.000000

"""
from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    op.create_index('idx_reports_tracking_id', 'reports', ['tracking_id'])
    op.create_index('idx_reports_status_priority', 'reports', ['lifecycle_status', 'priority_rank'])
    op.create_index('idx_reports_lat_lon', 'reports', ['latitude', 'longitude'])

    if conn.dialect.name == "postgresql":
        op.execute("CREATE INDEX IF NOT EXISTS idx_reports_location ON reports USING GIST (location);")
        op.execute("CREATE INDEX IF NOT EXISTS idx_reports_embedding ON reports USING hnsw (description_embedding vector_cosine_ops);")

def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS idx_reports_embedding;")
        op.execute("DROP INDEX IF EXISTS idx_reports_location;")
    op.drop_index('idx_reports_lat_lon', 'reports')
    op.drop_index('idx_reports_status_priority', 'reports')
    op.drop_index('idx_reports_tracking_id', 'reports')


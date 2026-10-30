"""TASK-008: Create Administrative Geographic Hierarchy Schema

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-30 14:32:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'administrative_zones',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('level', sa.String(32), nullable=False), # City, Division, Zone, Ward
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('administrative_zones.id', ondelete='SET NULL'), nullable=True),
        sa.Column('boundary_geojson', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('administrative_zones')


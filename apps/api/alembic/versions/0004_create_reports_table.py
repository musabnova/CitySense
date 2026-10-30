"""TASK-009: Create Core Reports Relational Table

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-30 14:33:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tracking_id', sa.String(12), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Citizen Input Layer
        sa.Column('raw_description', sa.Text(), nullable=False),
        sa.Column('user_category', sa.String(64), nullable=True),
        sa.Column('media_url', sa.String(512), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('formatted_address', sa.String(256), nullable=True),
        
        # AI Intelligence Layer
        sa.Column('verified_category', sa.String(64), nullable=False),
        sa.Column('concise_summary', sa.String(256), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), default=False, nullable=False),
        sa.Column('master_ticket_id', sa.String(36), sa.ForeignKey('reports.id', ondelete='SET NULL'), nullable=True),
        sa.Column('duplicate_count', sa.Integer(), default=1, nullable=False),
        
        # Workflow & Operations
        sa.Column('lifecycle_status', sa.String(32), default='Submitted', nullable=False),
        sa.Column('assigned_department', sa.String(128), nullable=True),
        sa.Column('dispatch_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('reports')


"""TASK-012: Create Audit Logging Table for Manual AI Overrides

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-30 14:36:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'report_audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('report_id', sa.String(36), sa.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('action_type', sa.String(64), nullable=False),
        sa.Column('previous_value', sa.Text(), nullable=False),
        sa.Column('new_value', sa.Text(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False)
    )
    op.create_index('idx_audit_report_id', 'report_audit_logs', ['report_id'])

def downgrade() -> None:
    op.drop_index('idx_audit_report_id', 'report_audit_logs')
    op.drop_table('report_audit_logs')


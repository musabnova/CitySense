"""TASK-010: Add Vector Embedding and Priority Columns

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-30 14:34:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    op.add_column('reports', sa.Column('priority_rank', sa.String(32), server_default='Priority 4', nullable=False))
    op.add_column('reports', sa.Column('priority_score', sa.Numeric(5, 2), server_default='0.00', nullable=False))
    op.add_column('reports', sa.Column('priority_rationale', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('is_manually_overridden', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('reports', sa.Column('override_reason', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('overridden_by_user_id', sa.String(36), nullable=True))

    if conn.dialect.name == "postgresql":
        op.execute("ALTER TABLE reports ADD COLUMN description_embedding vector(768);")
    else:
        op.add_column('reports', sa.Column('description_embedding_json', sa.Text(), nullable=True))

def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("ALTER TABLE reports DROP COLUMN IF EXISTS description_embedding;")
    else:
        op.drop_column('reports', 'description_embedding_json')
    op.drop_column('reports', 'overridden_by_user_id')
    op.drop_column('reports', 'override_reason')
    op.drop_column('reports', 'is_manually_overridden')
    op.drop_column('reports', 'priority_rationale')
    op.drop_column('reports', 'priority_score')
    op.drop_column('reports', 'priority_rank')


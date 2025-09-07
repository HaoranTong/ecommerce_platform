"""add certificates table

Revision ID: ddc5d075a832
Revises: 0002_product
Create Date: 2025-09-07
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ddc5d075a832'
down_revision = '0002_product'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('issuer', sa.String(length=200), nullable=True),
        sa.Column('serial', sa.String(length=200), nullable=False, unique=True),
        sa.Column('description', sa.String(length=1000), nullable=True),
    )


def downgrade():
    op.drop_table('certificates')

"""create products table

Revision ID: 0002_product
Revises: 0001_initial
Create Date: 2025-09-07
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_product'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'products',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.String(1000), nullable=True),
    )


def downgrade():
    op.drop_table('products')

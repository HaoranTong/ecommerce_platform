"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-08 12:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('wx_openid', sa.String(length=100), nullable=True),
        sa.Column('wx_unionid', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('real_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('wx_openid'),
        sa.UniqueConstraint('wx_unionid')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('attributes', sa.Text(), nullable=True),
        sa.Column('images', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index('idx_category_status', 'products', ['category_id', 'status'], unique=False)
    op.create_index('idx_status_created', 'products', ['status', 'created_at'], unique=False)

    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_no', sa.String(length=32), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('subtotal', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('shipping_fee', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('discount_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('total_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('shipping_address', sa.Text(), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('shipped_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index('idx_order_no', 'orders', ['order_no'], unique=False)
    op.create_index('idx_status_created', 'orders', ['status', 'created_at'], unique=False)
    op.create_index('idx_user_status', 'orders', ['user_id', 'status'], unique=False)

    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('product_sku', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('total_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)
    op.create_index('idx_order_product', 'order_items', ['order_id', 'product_id'], unique=False)

    # Create certificates table (legacy, to be refactored)
    op.create_table('certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('issuer', sa.String(length=200), nullable=True),
        sa.Column('serial', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial')
    )
    op.create_index(op.f('ix_certificates_id'), 'certificates', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_certificates_id'), table_name='certificates')
    op.drop_table('certificates')
    op.drop_index('idx_order_product', table_name='order_items')
    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index('idx_user_status', table_name='orders')
    op.drop_index('idx_status_created', table_name='orders')
    op.drop_index('idx_order_no', table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index('idx_status_created', table_name='products')
    op.drop_index('idx_category_status', table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

"""add_member_event_outbox_and_update_relationships

Revision ID: cff8c8c92d59
Revises: 6b06e71fe59a
Create Date: 2025-10-23 21:02:02.804892

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'cff8c8c92d59'
down_revision = '6b06e71fe59a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建会员事件外发表
    op.create_table(
        'member_event_outbox',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='事件ID'),
        sa.Column('member_id', sa.Integer(), nullable=True, comment='会员ID'),
        sa.Column('event_type', sa.String(length=100), nullable=False, comment='事件类型'),
        sa.Column('payload', sa.JSON(), nullable=False, comment='事件数据载荷'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='事件状态: pending/sending/sent/failed'),
        sa.Column('available_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='可发送时间'),
        sa.Column('delivered_at', sa.DateTime(), nullable=True, comment='投递完成时间'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0', comment='重试次数'),
        sa.Column('last_error', sa.Text(), nullable=True, comment='最后一次错误信息'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['member_id'], ['member_profiles.id'], name='fk_member_event_outbox_member_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_member_event_outbox_status_available', 'member_event_outbox', ['status', 'available_at'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_member_event_outbox_status_available', table_name='member_event_outbox')
    
    # 删除表
    op.drop_table('member_event_outbox')

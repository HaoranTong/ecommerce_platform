"""支付模块完善 - 添加新字段和退款表

Revision ID: payment_enhancement_v1
Revises: b85e9d5a6922
Create Date: 2025-09-11 12:00:00.000000

主要变更:
1. Payment表添加新字段：pay_url, qr_code, expires_at, description
2. Payment表更新支付方式枚举：支持unionpay, paypal, balance
3. Payment表更新状态枚举：支持cancelled, expired, refunding
4. 新建Refund表：支持退款管理
5. 添加相关索引优化查询性能
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = 'payment_enhancement_v1'
down_revision = 'b85e9d5a6922'
branch_labels = None
depends_on = None


def upgrade():
    """添加支付模块完善功能"""
    
    # 1. 为payments表添加新字段
    op.add_column('payments', sa.Column('pay_url', sa.String(1000), nullable=True))
    op.add_column('payments', sa.Column('qr_code', sa.Text, nullable=True))
    op.add_column('payments', sa.Column('expires_at', sa.DateTime, nullable=True))
    
    # 确保description字段存在（如果不存在则添加）
    try:
        op.add_column('payments', sa.Column('description', sa.String(1000), nullable=True))
    except Exception:
        # 字段可能已经存在，忽略错误
        pass
    
    # 2. 创建refunds表
    op.create_table(
        'refunds',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('payment_id', sa.Integer, sa.ForeignKey('payments.id'), nullable=False),
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('reason', sa.String(500), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='processing'),
        sa.Column('gateway_refund_id', sa.String(200), nullable=True),
        sa.Column('operator_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime, nullable=True),
    )
    
    # 3. 为refunds表创建索引
    op.create_index('idx_payment_status', 'refunds', ['payment_id', 'status'])
    op.create_index('idx_gateway_refund', 'refunds', ['gateway_refund_id'])
    
    # 4. 如果需要，添加约束检查（MySQL特定）
    # 支付方式约束
    op.execute("""
        ALTER TABLE payments 
        ADD CONSTRAINT chk_payment_method 
        CHECK (payment_method IN ('wechat', 'alipay', 'unionpay', 'paypal', 'balance'))
    """)
    
    # 支付状态约束
    op.execute("""
        ALTER TABLE payments 
        ADD CONSTRAINT chk_payment_status 
        CHECK (status IN ('pending', 'paid', 'failed', 'cancelled', 'expired', 'refunding', 'refunded'))
    """)
    
    # 退款状态约束
    op.execute("""
        ALTER TABLE refunds 
        ADD CONSTRAINT chk_refund_status 
        CHECK (status IN ('processing', 'success', 'failed', 'cancelled'))
    """)
    
    print("✅ 支付模块完善迁移完成")
    print("📋 变更内容:")
    print("   - payments表：添加pay_url, qr_code, expires_at字段")
    print("   - payments表：扩展支付方式和状态枚举")
    print("   - 新建refunds表：支持退款管理")
    print("   - 添加必要的索引和约束")


def downgrade():
    """回滚支付模块完善功能"""
    
    # 1. 删除约束
    op.execute("ALTER TABLE payments DROP CONSTRAINT chk_payment_method")
    op.execute("ALTER TABLE payments DROP CONSTRAINT chk_payment_status")
    op.execute("ALTER TABLE refunds DROP CONSTRAINT chk_refund_status")
    
    # 2. 删除refunds表
    op.drop_index('idx_gateway_refund', 'refunds')
    op.drop_index('idx_payment_status', 'refunds')
    op.drop_table('refunds')
    
    # 3. 删除payments表新增字段
    op.drop_column('payments', 'expires_at')
    op.drop_column('payments', 'qr_code')
    op.drop_column('payments', 'pay_url')
    
    print("✅ 支付模块完善迁移回滚完成")

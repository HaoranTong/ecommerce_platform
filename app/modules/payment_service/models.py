"""
文件名：payment.py
文件路径：app/models/payment.py
功能描述：支付管理相关的数据模型定义
主要功能：
- Payment支付模型：支付记录、状态管理、第三方支付集成
- Refund退款模型：退款申请、退款处理、状态跟踪
- 支付流水和退款流水管理
使用说明：
- 导入：from app.models.payment import Payment, Refund
- 关系：Payment与Order的多对一关系，Payment与Refund的一对多关系
依赖模块：
- app.models.base: 基础模型类和时间戳混合类
- sqlalchemy: 数据库字段定义和关系映射
"""

from sqlalchemy import Column, String, Text, DECIMAL, Integer, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, TimestampMixin


class Payment(BaseModel, TimestampMixin):
    """支付模型"""
    __tablename__ = 'payments'
    
    # 关联订单和用户
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 所有权字段
    
    # 支付基础信息
    payment_no = Column(String(100), unique=True, nullable=False, index=True)  # 内部支付单号
    payment_method = Column(String(50), nullable=False)  # 'wechat', 'alipay', 'unionpay', 'paypal', 'balance'
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='CNY', nullable=False)
    
    # 支付状态
    status = Column(String(20), default='pending', nullable=False)  # 'pending', 'processing', 'completed', 'failed', 'cancelled', 'expired', 'refunded'
    
    # 第三方支付信息
    external_payment_id = Column(String(200), nullable=True, index=True)      # 支付网关订单号
    external_transaction_id = Column(String(200), nullable=True, index=True)  # 支付网关交易号
    
    # 支付页面信息
    pay_url = Column(String(1000), nullable=True)         # 支付页面URL
    qr_code = Column(Text, nullable=True)                  # 二维码Base64数据
    expires_at = Column(DateTime, nullable=True)           # 支付过期时间
    
    # 回调和通知信息
    callback_received_at = Column(DateTime, nullable=True)
    callback_data = Column(Text, nullable=True)            # 加密存储的回调数据（JSON格式）
    payment_data = Column(Text, nullable=True)             # 支付相关扩展数据（JSON格式）
    
    # 描述信息
    description = Column(String(1000), nullable=True)
    
    # 时间节点
    paid_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # 关系映射
    order = relationship("Order", back_populates="payments")
    user = relationship("User", back_populates="payments")
    refunds = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")
    
    # 索引优化
    __table_args__ = (
        Index('idx_payment_no', 'payment_no'),
        Index('idx_order_user', 'order_id', 'user_id'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_external_payment', 'external_payment_id'),
        Index('idx_method_status', 'payment_method', 'status'),
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, payment_no='{self.payment_no}', status='{self.status}')>"


class Refund(BaseModel, TimestampMixin):
    """退款模型"""
    __tablename__ = 'refunds'
    
    # 关联支付记录
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    
    # 退款基础信息
    refund_no = Column(String(100), unique=True, nullable=False, index=True)  # 退款单号
    amount = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(String(500), nullable=False)
    status = Column(String(20), default='pending', nullable=False)  # 'pending', 'processing', 'completed', 'failed', 'cancelled'
    
    # 第三方退款信息
    external_refund_id = Column(String(200), nullable=True, index=True)  # 支付网关退款单号
    gateway_response = Column(Text, nullable=True)                       # 网关响应数据（JSON格式）
    
    # 操作信息
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 操作员ID
    operator_note = Column(Text, nullable=True)                           # 操作员备注
    
    # 时间节点
    processed_at = Column(DateTime, nullable=True)  # 退款处理完成时间
    
    # 关系映射
    payment = relationship("Payment", back_populates="refunds")
    operator = relationship("User", foreign_keys=[operator_id])
    
    # 索引优化
    __table_args__ = (
        Index('idx_payment_status', 'payment_id', 'status'),
        Index('idx_external_refund', 'external_refund_id'),
        Index('idx_operator_created', 'operator_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Refund(id={self.id}, refund_no='{self.refund_no}', status='{self.status}')>"
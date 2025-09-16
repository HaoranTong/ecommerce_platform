"""
支付模块认证工具

V1.0 Mini-MVP版本的支付认证依赖和安全工具
"""
from typing import Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.user_auth.models import User
from app.modules.order_management.models import Order
from app.modules.payment_service.models import Payment
from app.core.auth import get_current_active_user, get_current_admin_user


async def verify_payment_ownership(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> tuple[Payment, Order]:
    """
    验证支付单所有权
    
    Args:
        payment_id: 支付单ID
        current_user: 当前用户
        db: 数据库连接
        
    Returns:
        tuple[Payment, Order]: 支付单和关联订单
        
    Raises:
        HTTPException: 支付单不存在或无权访问
    """
    # 查询支付单
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付单不存在"
        )
    
    # 查询关联订单
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联订单不存在"
        )
    
    # 验证所有权
    if not require_ownership(order.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能操作自己的支付单"
        )
    
    return payment, order


async def verify_order_ownership_for_payment(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Order:
    """
    验证订单所有权用于创建支付
    
    Args:
        order_id: 订单ID
        current_user: 当前用户
        db: 数据库连接
        
    Returns:
        Order: 验证通过的订单
        
    Raises:
        HTTPException: 订单不存在或无权访问
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 验证所有权
    if not require_ownership(order.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己的订单创建支付"
        )
    
    # 验证订单状态
    if order.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"订单状态不允许支付，当前状态：{order.status}"
        )
    
    return order


def validate_payment_amount(order: Order, payment_amount: float) -> bool:
    """
    验证支付金额与订单金额一致性
    
    Args:
        order: 订单对象
        payment_amount: 支付金额
        
    Returns:
        bool: 金额是否一致
    """
    return abs(float(order.total_amount) - payment_amount) < 0.01


class PaymentSecurityError:
    """支付安全错误定义"""
    
    PAYMENT_NOT_FOUND = {
        "error": "payment_not_found",
        "message": "支付单不存在",
        "code": 404
    }
    
    PAYMENT_OWNERSHIP_REQUIRED = {
        "error": "payment_ownership_required", 
        "message": "只能操作自己的支付单",
        "code": 403
    }
    
    INVALID_PAYMENT_STATUS = {
        "error": "invalid_payment_status",
        "message": "支付单状态不允许此操作", 
        "code": 400
    }
    
    PAYMENT_AMOUNT_MISMATCH = {
        "error": "payment_amount_mismatch",
        "message": "支付金额与订单金额不符",
        "code": 400
    }
    
    ORDER_NOT_PAYABLE = {
        "error": "order_not_payable",
        "message": "订单状态不允许支付",
        "code": 400
    }


def create_payment_audit_log(
    payment_id: int,
    user_id: int,
    action: str,
    old_status: Optional[str] = None,
    new_status: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Session = None
):
    """
    创建支付审计日志
    
    Args:
        payment_id: 支付单ID
        user_id: 用户ID
        action: 操作类型
        old_status: 原状态
        new_status: 新状态
        ip_address: IP地址
        user_agent: 用户代理
        db: 数据库连接
    """
    # TODO: 实现审计日志记录
    # 当前版本暂时使用日志记录，后续版本添加数据库审计表
    import logging
    
    logger = logging.getLogger("payment_audit")
    log_data = {
        "payment_id": payment_id,
        "user_id": user_id,
        "action": action,
        "old_status": old_status,
        "new_status": new_status,
        "ip_address": ip_address,
        "user_agent": user_agent
    }
    
    logger.info(f"Payment audit: {log_data}")

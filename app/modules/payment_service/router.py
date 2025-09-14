"""
支付管理API路由 - V1.0 Mini-MVP

实现基础的支付功能，包括：
- 创建支付单
- 查询支付状态
- 微信支付回调处理
- 支付记录查询
"""
import uuid
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.database import get_db
from app.data_models import Payment, Order, User
from app.auth import get_current_active_user, get_current_admin_user
from app.payment_auth import (
    verify_payment_ownership,
    verify_order_ownership_for_payment,
    validate_payment_amount,
    PaymentSecurityError,
    create_payment_audit_log
)
from app.payment_service import (
    wechat_pay_service,
    payment_validator,
    payment_number_generator,
    create_payment_response
)
from app.api.schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentStatusUpdate,
    WechatPaymentCallback
)

router = APIRouter()


def generate_payment_no() -> str:
    """生成支付单号"""
    return payment_number_generator.generate_payment_no()


@router.post("/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建支付单
    
    用户只能为自己的订单创建支付，管理员可以为任何订单创建支付
    """
    # 验证订单所有权
    order = await verify_order_ownership_for_payment(
        payment_data.order_id, current_user, db
    )
    
    # 检查是否已有待支付的支付单
    existing_payment = db.query(Payment).filter(
        Payment.order_id == payment_data.order_id,
        Payment.status == 'pending'
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该订单已有待支付的支付单"
        )
    
    # 验证支付金额与订单金额一致
    if not validate_payment_amount(order, float(order.total_amount)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="支付金额与订单金额不符"
        )
    
    # 创建支付单
    payment = Payment(
        order_id=payment_data.order_id,
        user_id=current_user.id,
        payment_method=payment_data.payment_method,
        amount=order.total_amount,
        currency='CNY',
        payment_no=generate_payment_no(),
        status='pending'
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # 调用第三方支付服务
    payment_response = {}
    if payment_data.payment_method == 'wechat':
        try:
            wechat_response = wechat_pay_service.create_unified_order(
                payment_no=payment.payment_no,
                amount=payment.amount,
                description=f"订单{order.order_no}支付",
                user_openid=getattr(current_user, 'wx_openid', None)
            )
            payment_response = create_payment_response(payment, wechat_response)
        except Exception as e:
            # 如果第三方支付创建失败，删除支付单
            db.delete(payment)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建微信支付失败: {str(e)}"
            )
    
    # 记录审计日志
    create_payment_audit_log(
        payment_id=payment.id,
        user_id=current_user.id,
        action='create',
        new_status='pending',
        db=db
    )
    
    # 返回支付信息和第三方响应
    result = payment_response if payment_response else payment
    return result


@router.get("/payments/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """查询支付状态（所有权验证）"""
    
    payment, order = await verify_payment_ownership(payment_id, current_user, db)
    return payment


@router.get("/payments", response_model=List[PaymentRead])
async def list_payments(
    order_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取支付记录列表
    
    用户只能查看自己的支付记录，管理员可以查看所有记录
    """
    query = db.query(Payment)
    
    # 权限控制：用户只能查看自己的支付记录
    if current_user.role not in ['admin', 'super_admin']:
        query = query.filter(Payment.user_id == current_user.id)
    
    # 过滤条件
    if order_id:
        query = query.filter(Payment.order_id == order_id)
    
    if status_filter:
        query = query.filter(Payment.status == status_filter)
    
    # 排序和分页
    payments = query.order_by(desc(Payment.created_at)).offset(offset).limit(limit).all()
    
    return payments


@router.post("/payments/callback/wechat")
async def wechat_payment_callback(
    callback_data: WechatPaymentCallback,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    微信支付回调处理
    
    注意：此端点不需要用户认证，但需要验证微信签名
    """
    # TODO: 实现微信签名验证
    # verify_wechat_signature(callback_data.dict(), request.headers.get('Wechatpay-Signature'))
    
    # 根据商户订单号查找支付单
    payment = db.query(Payment).filter(
        Payment.payment_no == callback_data.out_trade_no
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付单不存在"
        )
    
    # 更新支付状态
    old_status = payment.status
    
    if callback_data.trade_state == 'SUCCESS':
        payment.status = 'paid'
        payment.paid_at = datetime.utcnow()
        payment.external_payment_id = callback_data.out_trade_no
        payment.external_transaction_id = callback_data.transaction_id
        
        # 更新订单状态
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if order and order.status == 'pending':
            order.status = 'paid'
            order.paid_at = datetime.utcnow()
    
    elif callback_data.trade_state in ['CLOSED', 'REVOKED', 'PAYERROR']:
        payment.status = 'failed'
        payment.failed_at = datetime.utcnow()
    
    # 记录回调信息
    payment.callback_received_at = datetime.utcnow()
    payment.callback_data = str(callback_data.dict())  # 简化存储，生产环境需要加密
    
    db.commit()
    
    # 记录审计日志
    create_payment_audit_log(
        payment_id=payment.id,
        user_id=payment.user_id,
        action='callback',
        old_status=old_status,
        new_status=payment.status,
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        db=db
    )
    
    return {"code": "SUCCESS", "message": "处理成功"}


@router.get("/admin/payments", response_model=List[PaymentRead])
async def admin_list_all_payments(
    user_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    payment_method: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """管理员查看所有支付记录"""
    
    query = db.query(Payment)
    
    # 过滤条件
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    
    if status_filter:
        query = query.filter(Payment.status == status_filter)
    
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    
    # 排序和分页
    payments = query.order_by(desc(Payment.created_at)).offset(offset).limit(limit).all()
    
    return payments


@router.patch("/admin/payments/{payment_id}/status", response_model=PaymentRead)
async def admin_update_payment_status(
    payment_id: int,
    status_update: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """管理员更新支付状态（用于处理退款等）"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付单不存在"
        )
    
    old_status = payment.status
    
    # 更新支付状态
    payment.status = status_update.status
    
    if status_update.status == 'refunded':
        payment.refunded_at = datetime.utcnow()
    elif status_update.status == 'failed':
        payment.failed_at = datetime.utcnow()
    elif status_update.status == 'paid':
        payment.paid_at = datetime.utcnow()
    
    # 更新第三方信息
    if status_update.external_payment_id:
        payment.external_payment_id = status_update.external_payment_id
    
    if status_update.external_transaction_id:
        payment.external_transaction_id = status_update.external_transaction_id
    
    db.commit()
    db.refresh(payment)
    
    # 记录审计日志
    create_payment_audit_log(
        payment_id=payment.id,
        user_id=current_admin.id,
        action='admin_update',
        old_status=old_status,
        new_status=payment.status,
        db=db
    )
    
    return payment

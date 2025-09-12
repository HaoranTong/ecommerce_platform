"""
文件名：payment.py
文件路径：app/api/routes/payment.py
功能描述：支付和退款管理相关的API路由定义
主要功能：
- 订单支付处理（支付宝、微信、银行卡等）
- 支付状态查询和管理
- 退款申请和处理
- 支付统计和报表
- 支付方式管理
使用说明：
- 路由前缀：/api/v1/payments
- 认证要求：所有接口需要用户认证
- 权限控制：用户只能操作自己的支付记录
依赖模块：
- app.services.PaymentService: 支付业务逻辑服务
- app.schemas.payment: 支付相关输入输出模式
- app.auth: 用户认证和权限控制
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentRead, PaymentStatus,
    RefundCreate, RefundUpdate, RefundRead, RefundStatus,
    PaymentStats, PaymentMethod
)
from app.services import PaymentService
from app.auth import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/payments", tags=["支付管理"])


# === 支付相关路由 ===

@router.get("", response_model=List[PaymentRead])
def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[PaymentStatus] = Query(None),
    method: Optional[PaymentMethod] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户的支付记录列表
    
    - 需要用户认证
    - 支持按状态、支付方式、时间范围筛选
    - 分页查询
    """
    payments = PaymentService.get_user_payments(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        method=method,
        start_date=start_date,
        end_date=end_date
    )
    return payments


@router.get("/all", response_model=List[PaymentRead])
def list_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[PaymentStatus] = Query(None),
    method: Optional[PaymentMethod] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取所有支付记录列表
    
    - 需要管理员权限
    - 支持按用户、状态、支付方式、时间筛选
    """
    payments = PaymentService.get_all_payments(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        method=method,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    return payments


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    根据ID获取支付记录详情
    
    - 需要用户认证
    - 用户只能查看自己的支付记录
    """
    payment = PaymentService.get_payment_by_id(db=db, payment_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    # 检查支付记录所有权
    if payment.order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问此支付记录")
    
    return payment


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    创建支付记录
    
    - 需要用户认证
    - 验证订单归属和状态
    - 调用第三方支付接口
    """
    try:
        payment = PaymentService.create_payment(
            db=db,
            order_id=payment_data.order_id,
            payment_method=payment_data.payment_method,
            amount=payment_data.amount,
            user_id=current_user.id
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="支付创建失败")


@router.put("/{payment_id}/status", response_model=PaymentRead)
def update_payment_status(
    payment_id: int,
    new_status: PaymentStatus,
    transaction_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新支付状态
    
    - 需要管理员权限
    - 通常由支付回调或管理员操作触发
    """
    payment = PaymentService.update_payment_status(
        db=db,
        payment_id=payment_id,
        new_status=new_status,
        transaction_id=transaction_id
    )
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    return payment


@router.post("/{payment_id}/confirm", response_model=PaymentRead)
def confirm_payment(
    payment_id: int,
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    确认支付成功
    
    - 需要用户认证
    - 验证支付交易ID
    - 更新订单状态
    """
    payment = PaymentService.confirm_payment(
        db=db,
        payment_id=payment_id,
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在或已确认")
    return payment


@router.post("/{payment_id}/cancel")
def cancel_payment(
    payment_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    取消支付
    
    - 需要用户认证
    - 只能取消待支付状态的记录
    """
    success = PaymentService.cancel_payment(
        db=db,
        payment_id=payment_id,
        user_id=current_user.id,
        reason=reason
    )
    if not success:
        raise HTTPException(status_code=400, detail="支付记录不存在或状态不允许取消")
    
    return {"message": "支付取消成功"}


# === 退款相关路由 ===

@router.get("/refunds", response_model=List[RefundRead])
def list_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[RefundStatus] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户的退款记录列表
    
    - 需要用户认证
    - 支持按状态、时间范围筛选
    """
    refunds = PaymentService.get_user_refunds(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return refunds


@router.get("/refunds/all", response_model=List[RefundRead])
def list_all_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[RefundStatus] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取所有退款记录列表
    
    - 需要管理员权限
    """
    refunds = PaymentService.get_all_refunds(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    return refunds


@router.get("/refunds/{refund_id}", response_model=RefundRead)
def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    根据ID获取退款记录详情
    
    - 需要用户认证
    - 用户只能查看自己的退款记录
    """
    refund = PaymentService.get_refund_by_id(db=db, refund_id=refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail="退款记录不存在")
    
    # 检查退款记录所有权
    if refund.payment.order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问此退款记录")
    
    return refund


@router.post("/refunds", response_model=RefundRead, status_code=status.HTTP_201_CREATED)
def create_refund(
    refund_data: RefundCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    申请退款
    
    - 需要用户认证
    - 验证支付记录状态
    - 创建退款申请
    """
    try:
        refund = PaymentService.create_refund(
            db=db,
            payment_id=refund_data.payment_id,
            amount=refund_data.amount,
            reason=refund_data.reason,
            user_id=current_user.id
        )
        return refund
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="退款申请创建失败")


@router.put("/refunds/{refund_id}/status", response_model=RefundRead)
def update_refund_status(
    refund_id: int,
    new_status: RefundStatus,
    admin_note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新退款状态
    
    - 需要管理员权限
    - 处理退款申请（同意/拒绝）
    """
    refund = PaymentService.update_refund_status(
        db=db,
        refund_id=refund_id,
        new_status=new_status,
        admin_note=admin_note
    )
    if not refund:
        raise HTTPException(status_code=404, detail="退款记录不存在")
    return refund


@router.post("/refunds/{refund_id}/process")
def process_refund(
    refund_id: int,
    transaction_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    处理退款（执行退款操作）
    
    - 需要管理员权限
    - 调用第三方退款接口
    """
    success = PaymentService.process_refund(
        db=db,
        refund_id=refund_id,
        transaction_id=transaction_id
    )
    if not success:
        raise HTTPException(status_code=400, detail="退款处理失败")
    
    return {"message": "退款处理成功"}


# === 统计相关路由 ===

@router.get("/stats/user", response_model=PaymentStats)
def get_user_payment_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户的支付统计
    
    - 需要用户认证
    - 返回支付金额、退款金额等统计
    """
    stats = PaymentService.get_user_payment_statistics(
        db=db,
        user_id=current_user.id
    )
    return stats


@router.get("/stats/overview", response_model=PaymentStats)
def get_payment_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取支付统计概览
    
    - 需要管理员权限
    - 支持时间范围筛选
    - 返回支付、退款金额和趋势
    """
    stats = PaymentService.get_payment_statistics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return stats


@router.get("/methods", response_model=List[str])
def get_payment_methods():
    """
    获取支持的支付方式列表
    
    - 无需认证
    - 返回可用的支付方式
    """
    return PaymentService.get_available_payment_methods()
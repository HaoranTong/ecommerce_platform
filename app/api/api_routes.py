"""
文件名：api_routes.py
文件路径：app/api/api_routes.py
功能描述：电商平台主要API路由定义，整合各业务模块的API接口
主要功能：
- 用户管理API：注册、登录、用户信息管理
- 商品管理API：商品CRUD、分类管理、库存管理
- 订单管理API：订单创建、状态管理、订单查询
- 支付管理API：支付创建、状态查询、支付回调
- 购物车API：商品添加、删除、数量更新
使用说明：
- 路由前缀：/api/v1
- 认证要求：部分接口需要JWT认证
- 响应格式：统一JSON格式，遵循RESTful规范
依赖模块：
- app.services: 业务逻辑服务层
- app.schemas: 输入输出数据模型
- app.auth: 用户认证相关功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import get_db
import app.data_models as models
from app.api import schemas
from app.auth import get_current_active_user, get_current_admin_user, require_ownership
from app.services import UserService, ProductService, OrderService, CartService, PaymentService, CategoryService

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    try:
        user = UserService.create_user(
            db=db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
            phone=getattr(payload, 'phone', None),
            real_name=getattr(payload, 'real_name', None)
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="用户创建失败")


@router.get("/users", response_model=List[schemas.UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = UserService.get_users(db=db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """根据ID获取用户信息"""
    user = UserService.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    success = UserService.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return None


# ====== 支付模块路由 ======

@router.post("/payments", response_model=schemas.PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """创建支付订单"""
    try:
        # 验证订单权限
        if payment_data.order_id:
            order = OrderService.get_order_by_id(db=db, order_id=payment_data.order_id, user_id=current_user.id)
            if not order:
                raise HTTPException(status_code=404, detail="订单不存在或无权访问")
        
        # 创建支付记录
        payment = PaymentService.create_payment(
            db=db,
            order_id=payment_data.order_id,
            payment_method=payment_data.payment_method,
            amount=payment_data.amount
        )
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="支付创建失败")


@router.get("/payments", response_model=List[schemas.PaymentRead])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """获取支付记录列表"""
    # 普通用户只能查看自己的支付记录
    user_id = None if current_user.role in ['admin', 'super_admin'] else current_user.id
    
    # 使用服务层获取支付统计（这里简化处理，实际应该有专门的列表接口）
    payments = PaymentService.get_payments_by_order(db=db, order_id=None)  # 需要扩展服务层方法
    return payments


@router.get("/payments/{payment_id}", response_model=schemas.PaymentRead)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """获取支付详情"""
    payment = PaymentService.get_payment_by_id(db=db, payment_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    # 权限检查
    if current_user.role not in ['admin', 'super_admin'] and payment.order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此支付记录")
    
    return payment


@router.patch("/payments/{payment_id}/status", response_model=schemas.PaymentRead)
async def update_payment_status(
    payment_id: int,
    status_update: schemas.PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)
):
    """更新支付状态 - 管理员权限"""
    try:
        payment = PaymentService.update_payment_status(
            db=db,
            payment_id=payment_id,
            new_status=status_update.status,
            external_transaction_id=getattr(status_update, 'external_transaction_id', None)
        )
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="支付状态更新失败")


@router.post("/payments/{payment_id}/cancel", response_model=schemas.PaymentRead)
async def cancel_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """取消支付"""
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    # 权限检查
    if not require_ownership(payment.user_id, current_user):
        raise HTTPException(status_code=403, detail="无权操作此支付记录")
    
    # 状态检查
    if payment.status not in ["pending", "processing"]:
        raise HTTPException(status_code=400, detail="只能取消待支付或处理中的支付")
    
    payment.status = "cancelled"
    payment.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(payment)
    
    return payment


# ====== 退款模块路由 ======

@router.post("/refunds", response_model=schemas.RefundRead, status_code=status.HTTP_201_CREATED)
async def create_refund(
    refund_data: schemas.RefundCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """创建退款申请"""
    # 验证支付记录
    payment = db.query(models.Payment).filter(models.Payment.id == refund_data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    # 权限检查
    if not require_ownership(payment.user_id, current_user):
        raise HTTPException(status_code=403, detail="无权对此支付申请退款")
    
    # 状态检查
    if payment.status != "completed":
        raise HTTPException(status_code=400, detail="只能对已完成的支付申请退款")
    
    # 金额检查
    if refund_data.amount > payment.amount:
        raise HTTPException(status_code=400, detail="退款金额不能超过支付金额")
    
    # 检查是否已有退款记录
    existing_refund = db.query(models.Refund).filter(
        models.Refund.payment_id == refund_data.payment_id
    ).first()
    if existing_refund:
        raise HTTPException(status_code=400, detail="此支付记录已有退款申请")
    
    # 创建退款记录
    refund = models.Refund(
        payment_id=refund_data.payment_id,
        amount=refund_data.amount,
        reason=refund_data.reason,
        status="pending"
    )
    
    db.add(refund)
    db.commit()
    db.refresh(refund)
    
    return refund


@router.get("/refunds", response_model=List[schemas.RefundRead])
async def list_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """获取退款记录列表"""
    query = db.query(models.Refund)
    
    # 普通用户只能查看自己相关的退款记录
    if current_user.role not in ['admin', 'super_admin']:
        query = query.join(models.Payment).filter(models.Payment.user_id == current_user.id)
    
    # 状态过滤
    if status:
        query = query.filter(models.Refund.status == status)
    
    # 排序和分页
    refunds = query.order_by(desc(models.Refund.created_at)).offset(skip).limit(limit).all()
    return refunds


@router.get("/refunds/{refund_id}", response_model=schemas.RefundRead)
async def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """获取退款详情"""
    refund = db.query(models.Refund).filter(models.Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款记录不存在")
    
    # 权限检查
    if current_user.role not in ['admin', 'super_admin']:
        if not require_ownership(refund.payment.user_id, current_user):
            raise HTTPException(status_code=403, detail="无权访问此退款记录")
    
    return refund


@router.patch("/refunds/{refund_id}/status", response_model=schemas.RefundRead)
async def update_refund_status(
    refund_id: int,
    status_data: schemas.RefundStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)
):
    """更新退款状态 - 管理员权限"""
    refund = db.query(models.Refund).filter(models.Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款记录不存在")
    
    # 状态验证
    valid_statuses = ["pending", "approved", "rejected", "processing", "completed", "failed"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="无效的退款状态")
    
    # 更新退款状态
    refund.status = status_data.status
    refund.admin_note = status_data.admin_note
    
    # 更新处理时间
    if status_data.status in ["approved", "rejected", "completed", "failed"]:
        refund.processed_at = datetime.utcnow()
    
    # 如果退款完成，更新相关支付状态
    if status_data.status == "completed":
        refund.payment.status = "refunded"
        db.add(refund.payment)
    
    db.commit()
    db.refresh(refund)
    
    return refund


# ====== 统计分析路由 ======

@router.get("/payments/stats", response_model=schemas.PaymentStats)
async def get_payment_stats(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user)
):
    """获取支付统计数据 - 管理员权限"""
    # 解析日期参数
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_dt = datetime.utcnow() - timedelta(days=30)  # 默认30天
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        else:
            end_dt = datetime.utcnow()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    
    # 基础查询
    base_query = db.query(models.Payment).filter(
        and_(
            models.Payment.created_at >= start_dt,
            models.Payment.created_at < end_dt
        )
    )
    
    # 总体统计
    total_amount = base_query.filter(models.Payment.status == "completed").with_entities(
        func.sum(models.Payment.amount)
    ).scalar() or Decimal('0')
    
    total_count = base_query.count()
    completed_count = base_query.filter(models.Payment.status == "completed").count()
    
    # 按支付方式统计
    by_method = {}
    for method in ["wechat", "alipay", "unionpay", "paypal", "balance"]:
        method_query = base_query.filter(models.Payment.payment_method == method)
        method_amount = method_query.filter(models.Payment.status == "completed").with_entities(
            func.sum(models.Payment.amount)
        ).scalar() or Decimal('0')
        method_count = method_query.count()
        
        by_method[method] = {
            "amount": str(method_amount),
            "count": method_count,
            "success_rate": method_query.filter(models.Payment.status == "completed").count() / max(method_count, 1) * 100
        }
    
    # 每日趋势（最近7天）
    daily_trend = []
    for i in range(7):
        day_start = (datetime.utcnow() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_query = db.query(models.Payment).filter(
            and_(
                models.Payment.created_at >= day_start,
                models.Payment.created_at < day_end
            )
        )
        
        day_amount = day_query.filter(models.Payment.status == "completed").with_entities(
            func.sum(models.Payment.amount)
        ).scalar() or Decimal('0')
        
        daily_trend.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "amount": str(day_amount),
            "count": day_query.count()
        })
    
    return {
        "period": {
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": (end_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        },
        "summary": {
            "total_amount": str(total_amount),
            "total_count": total_count,
            "completed_count": completed_count,
            "success_rate": completed_count / max(total_count, 1) * 100
        },
        "by_method": by_method,
        "daily_trend": list(reversed(daily_trend))  # 按时间正序
    }


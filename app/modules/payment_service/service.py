"""
文件名：payment_service.py
文件路径：app/services/payment_service.py
功能描述：支付管理相关的业务逻辑服务
主要功能：
- 支付记录的创建、查询、更新
- 支付状态管理和验证
- 支付方式处理和退款管理
使用说明：
- 导入：from app.services.payment_service import PaymentService
- 在路由中调用：PaymentService.create_payment(payment_data)
"""

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.modules.user_auth.models import User
from app.modules.order_management.models import Order
from .models import Payment
from app.adapters.payment import WechatPayAdapter


class PaymentService:
    """支付管理业务逻辑服务"""
    
    # 支持的支付方式
    PAYMENT_METHODS = {
        'alipay': '支付宝',
        'wechat': '微信支付',
        'credit_card': '信用卡',
        'debit_card': '借记卡',
        'bank_transfer': '银行转账',
        'cash_on_delivery': '货到付款'
    }
    
    # 支付状态
    PAYMENT_STATUSES = {
        'pending': '待支付',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '支付失败',
        'cancelled': '已取消',
        'refunded': '已退款',
        'partial_refunded': '部分退款'
    }
    
    @staticmethod
    def generate_payment_no() -> str:
        """
        生成支付流水号
        
        Returns:
            str: 格式为 PAY{timestamp}{random} 的支付流水号
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4()).replace('-', '')[:8].upper()
        return f"PAY{timestamp}{random_suffix}"
    
    @staticmethod
    def create_payment(db: Session, order_id: int, payment_method: str,
                      amount: Optional[Decimal] = None, 
                      external_transaction_id: Optional[str] = None,
                      payment_data: Optional[Dict[str, Any]] = None) -> Payment:
        """
        创建支付记录
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            payment_method: 支付方式
            amount: 支付金额（可选，默认使用订单金额）
            external_transaction_id: 外部交易流水号
            payment_data: 支付相关数据（JSON格式）
            
        Returns:
            Payment: 创建的支付记录
            
        Raises:
            HTTPException: 订单不存在或支付方式不支持时抛出错误
        """
        # 验证订单存在
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 验证支付方式
        if payment_method not in PaymentService.PAYMENT_METHODS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的支付方式：{payment_method}"
            )
        
        # 使用订单金额或指定金额
        payment_amount = amount or order.total_amount
        
        # 验证金额
        if payment_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="支付金额必须大于0"
            )
        
        # 检查是否已有待支付或已完成的支付记录
        existing_payment = db.query(Payment).filter(
            Payment.order_id == order_id,
            Payment.status.in_(['pending', 'processing', 'completed'])
        ).first()
        
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单已有有效的支付记录"
            )
        
        # 创建支付记录
        payment = Payment(
            payment_no=PaymentService.generate_payment_no(),
            order_id=order_id,
            amount=payment_amount,
            payment_method=payment_method,
            status='pending',
            external_transaction_id=external_transaction_id,
            payment_data=payment_data or {}
        )
        
        try:
            db.add(payment)
            db.commit()
            db.refresh(payment)
            return payment
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="支付记录创建失败，数据冲突"
            )
    
    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
        """
        根据ID获取支付记录
        
        Args:
            db: 数据库会话
            payment_id: 支付ID
            
        Returns:
            Payment: 支付记录或None
        """
        return db.query(Payment).options(
            joinedload(Payment.order).joinedload(Order.user)
        ).filter(Payment.id == payment_id).first()
    
    @staticmethod
    def get_payment_by_no(db: Session, payment_no: str) -> Optional[Payment]:
        """
        根据支付流水号获取支付记录
        
        Args:
            db: 数据库会话
            payment_no: 支付流水号
            
        Returns:
            Payment: 支付记录或None
        """
        return db.query(Payment).options(
            joinedload(Payment.order).joinedload(Order.user)
        ).filter(Payment.payment_no == payment_no).first()
    
    @staticmethod
    def get_payments_by_order(db: Session, order_id: int) -> List[Payment]:
        """
        获取订单的所有支付记录
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            
        Returns:
            List[Payment]: 支付记录列表
        """
        return db.query(Payment).filter(
            Payment.order_id == order_id
        ).order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def update_payment_status(db: Session, payment_id: int, new_status: str,
                             external_transaction_id: Optional[str] = None,
                             payment_data: Optional[Dict[str, Any]] = None) -> Optional[Payment]:
        """
        更新支付状态
        
        Args:
            db: 数据库会话
            payment_id: 支付ID
            new_status: 新状态
            external_transaction_id: 外部交易流水号
            payment_data: 支付相关数据
            
        Returns:
            Payment: 更新后的支付记录或None
            
        Raises:
            HTTPException: 状态转换不合法时抛出错误
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return None
        
        # 验证状态转换合法性
        valid_transitions = {
            'pending': ['processing', 'completed', 'failed', 'cancelled'],
            'processing': ['completed', 'failed', 'cancelled'],
            'completed': ['refunded', 'partial_refunded'],
            'failed': ['pending'],
            'cancelled': ['pending'],
            'refunded': [],
            'partial_refunded': ['refunded']
        }
        
        if new_status not in valid_transitions.get(payment.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法从状态 {payment.status} 转换到 {new_status}"
            )
        
        payment.status = new_status
        
        if external_transaction_id:
            payment.external_transaction_id = external_transaction_id
        
        if payment_data:
            payment.payment_data.update(payment_data)
        
        # 根据支付状态更新订单状态
        if new_status == 'completed':
            order = db.query(Order).filter(Order.id == payment.order_id).first()
            if order and order.status == 'pending':
                order.status = 'paid'
        
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def process_payment_callback(db: Session, payment_no: str, callback_data: Dict[str, Any]) -> Optional[Payment]:
        """
        处理支付回调
        
        Args:
            db: 数据库会话
            payment_no: 支付流水号
            callback_data: 回调数据
            
        Returns:
            Payment: 更新后的支付记录或None
        """
        payment = PaymentService.get_payment_by_no(db, payment_no)
        if not payment:
            return None
        
        # 根据回调数据判断支付状态
        # 这里需要根据具体的支付接口进行实现
        if callback_data.get('status') == 'SUCCESS':
            payment = PaymentService.update_payment_status(
                db, payment.id, 'completed',
                external_transaction_id=callback_data.get('transaction_id'),
                payment_data=callback_data
            )
        elif callback_data.get('status') == 'FAILED':
            payment = PaymentService.update_payment_status(
                db, payment.id, 'failed',
                payment_data=callback_data
            )
        
        return payment
    
    @staticmethod
    def initiate_refund(db: Session, payment_id: int, refund_amount: Optional[Decimal] = None,
                       reason: Optional[str] = None) -> bool:
        """
        发起退款
        
        Args:
            db: 数据库会话
            payment_id: 支付ID
            refund_amount: 退款金额（可选，默认全额退款）
            reason: 退款原因
            
        Returns:
            bool: 退款发起成功返回True
            
        Raises:
            HTTPException: 支付记录不存在或状态不允许退款时抛出错误
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        if payment.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有已完成的支付才能退款"
            )
        
        # 默认全额退款
        refund_amount = refund_amount or payment.amount
        
        if refund_amount <= 0 or refund_amount > payment.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退款金额无效"
            )
        
        # 这里应该调用具体的支付接口进行退款
        # 假设退款成功，更新支付状态
        if refund_amount == payment.amount:
            new_status = 'refunded'
        else:
            new_status = 'partial_refunded'
        
        PaymentService.update_payment_status(
            db, payment_id, new_status,
            payment_data={'refund_amount': float(refund_amount), 'refund_reason': reason}
        )
        
        return True
    
    @staticmethod
    def get_payment_statistics(db: Session, user_id: Optional[int] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取支付统计信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            Dict[str, Any]: 支付统计信息
        """
        query = db.query(Payment).join(Order)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        total_payments = query.count()
        completed_payments = query.filter(Payment.status == 'completed').count()
        failed_payments = query.filter(Payment.status == 'failed').count()
        
        # 计算总金额
        total_amount = query.filter(Payment.status == 'completed').with_entities(
            db.func.sum(Payment.amount)
        ).scalar() or 0
        
        # 按支付方式统计
        payment_methods = db.query(
            Payment.payment_method,
            db.func.count(Payment.id).label('count'),
            db.func.sum(Payment.amount).label('amount')
        ).join(Order)
        
        if user_id:
            payment_methods = payment_methods.filter(Order.user_id == user_id)
        
        if start_date:
            payment_methods = payment_methods.filter(Payment.created_at >= start_date)
        
        if end_date:
            payment_methods = payment_methods.filter(Payment.created_at <= end_date)
        
        payment_methods = payment_methods.filter(
            Payment.status == 'completed'
        ).group_by(Payment.payment_method).all()
        
        method_stats = []
        for method, count, amount in payment_methods:
            method_stats.append({
                'method': method,
                'method_name': PaymentService.PAYMENT_METHODS.get(method, method),
                'count': count,
                'amount': float(amount or 0)
            })
        
        return {
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'failed_payments': failed_payments,
            'success_rate': completed_payments / total_payments if total_payments > 0 else 0,
            'total_amount': float(total_amount),
            'payment_methods': method_stats
        }
    
    @staticmethod
    def get_pending_payments(db: Session, timeout_minutes: int = 30) -> List[Payment]:
        """
        获取超时的待支付记录
        
        Args:
            db: 数据库会话
            timeout_minutes: 超时分钟数
            
        Returns:
            List[Payment]: 超时的支付记录列表
        """
        timeout_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        return db.query(Payment).filter(
            Payment.status == 'pending',
            Payment.created_at < timeout_time
        ).all()
    
    @staticmethod
    def cancel_expired_payments(db: Session, timeout_minutes: int = 30) -> int:
        """
        取消超时的待支付记录
        
        Args:
            db: 数据库会话
            timeout_minutes: 超时分钟数
            
        Returns:
            int: 取消的支付记录数量
        """
        expired_payments = PaymentService.get_pending_payments(db, timeout_minutes)
        
        count = 0
        for payment in expired_payments:
            PaymentService.update_payment_status(db, payment.id, 'cancelled')
            count += 1
        
        return count
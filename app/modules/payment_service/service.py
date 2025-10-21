"""Payment service application layer.

Encapsulates payment domain orchestration following the Router → Service →
Repository → Model architecture. Persistence details are delegated to the
repository layer while this module focuses on business rules, validation, and
integration flows.
"""

from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Mapping, Optional

from fastapi import HTTPException, status
from sqlalchemy import func

from app.adapters.payment import WechatPayAdapter
from app.modules.order_management.models import Order
from app.modules.user_auth.models import User

from .auth_helpers import create_payment_audit_log
from .models import Payment
from .repository import (
    PaymentDomainEvent,
    PaymentRepository,
    PaymentTransactionCreate,
)
from .schemas import PaymentCreate, PaymentStatusUpdate, WechatPaymentCallback
from .utils import PaymentNumberGenerator, PaymentValidator


@dataclass(slots=True)
class PaymentService:
    """Application service coordinating payment workflows."""

    repository: PaymentRepository
    wechat_adapter: WechatPayAdapter
    number_generator: PaymentNumberGenerator
    validator: PaymentValidator

    @contextmanager
    def _transaction_scope(self):
        session = self.repository.session
        if session.in_transaction():
            with session.begin_nested():
                yield
        else:
            with session.begin():
                yield

    def create_payment(
        self,
        *,
        order: Order,
        payload: PaymentCreate,
        current_user: User,
    ) -> Payment:
        amount = payload.amount or order.total_amount
        if not self.validator.validate_amount(Decimal(order.total_amount), Decimal(amount)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="支付金额与订单金额不符",
            )

        if not self.validator.validate_payment_method(payload.payment_method):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的支付方式：{payload.payment_method}",
            )

        existing_payment = self.repository.find_active_for_order(order.id)
        if existing_payment and existing_payment.status in {"pending", "processing"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该订单已有待处理的支付单",
            )

        payment = Payment(
            order_id=order.id,
            user_id=current_user.id,
            payment_method=payload.payment_method,
            amount=Decimal(amount),
            currency=payload.currency or "CNY",
            payment_no=self.number_generator.generate_payment_no(),
            status="pending",
            description=payload.description,
            payment_data=json.dumps(payload.model_dump(exclude_none=True), ensure_ascii=False),
        )

        if payload.payment_method == "wechat":
            order_reference = getattr(order, "order_no", None) or getattr(order, "order_number", None)
            wechat_response = self.wechat_adapter.create_unified_order(
                payment_no=payment.payment_no,
                amount=payment.amount,
                description=payload.description
                or (f"订单{order_reference}支付" if order_reference else "订单支付"),
                user_openid=getattr(current_user, "wx_openid", None),
            )
            payment.qr_code = wechat_response.get("code_url")
            payment.pay_url = wechat_response.get("prepay_id")

        with self._transaction_scope():
            self.repository.create_payment(payment)
            self.repository.enqueue_event(
                PaymentDomainEvent(
                    event_type="PaymentCreated",
                    payload={
                        "payment_id": payment.id,
                        "payment_no": payment.payment_no,
                        "order_id": order.id,
                        "user_id": current_user.id,
                        "amount": str(payment.amount),
                        "currency": payment.currency,
                        "payment_method": payment.payment_method,
                        "created_at": datetime.utcnow().isoformat(),
                    },
                ),
                payment_id=payment.id,
            )

        create_payment_audit_log(
            payment_id=payment.id,
            user_id=current_user.id,
            action="create",
            new_status="pending",
            db=self.repository.session,
        )

        self.repository.session.refresh(payment)
        return payment

    def get_payment(self, *, payment_id: int, current_user: User) -> Payment:
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付单不存在")

        if not self._can_view_payment(payment, current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能操作自己的支付单")
        return payment

    def list_payments_for_user(
        self,
        *,
        current_user: User,
        order_id: Optional[int],
        status_filter: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Payment]:
        return self.repository.list_user_payments(
            user_id=current_user.id,
            order_id=order_id,
            status_filter=status_filter,
            limit=limit,
            offset=offset,
        )

    def list_payments_for_admin(
        self,
        *,
        order_id: Optional[int],
        user_id: Optional[int],
        status_filter: Optional[str],
        payment_method: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Payment]:
        return self.repository.list_admin_payments(
            user_id=user_id,
            order_id=order_id,
            status_filter=status_filter,
            payment_method=payment_method,
            limit=limit,
            offset=offset,
        )

    def process_wechat_callback(
        self,
        *,
        callback: WechatPaymentCallback,
        headers: Mapping[str, str],
        request_client: str | None,
    ) -> Dict[str, str]:
        signature = headers.get("Wechatpay-Signature")
        if not signature or not self.wechat_adapter.verify_callback_signature(
            callback.callback_data, signature
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="回调签名无效")

        with self._transaction_scope():
            payment = self.repository.get_by_payment_no(
                callback.out_trade_no,
                for_update=True,
            )
            if not payment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付单不存在")

            if not self.repository.ensure_callback_idempotent(payment):
                return {"code": "SUCCESS", "message": "重复通知已忽略"}

            paid_at = datetime.utcnow()
            self.repository.mark_callback_processed(
                payment,
                callback_payload=callback.callback_data,
                external_payment_id=callback.out_trade_no,
                external_transaction_id=callback.transaction_id,
                paid_at=paid_at,
            )

            self.repository.append_transaction(
                payment_id=payment.id,
                transaction=PaymentTransactionCreate(
                    transaction_no=f"TRX{uuid.uuid4().hex[:18].upper()}",
                    transaction_type="payment",
                    amount=payment.amount,
                    gateway_response=callback.callback_data,
                ),
            )

            self.repository.enqueue_event(
                PaymentDomainEvent(
                    event_type="PaymentCompleted",
                    payload={
                        "payment_id": payment.id,
                        "payment_no": payment.payment_no,
                        "order_id": payment.order_id,
                        "user_id": payment.user_id,
                        "amount": str(payment.amount),
                        "currency": payment.currency,
                        "transaction_id": callback.transaction_id,
                        "completed_at": paid_at.isoformat(),
                    },
                ),
                payment_id=payment.id,
            )

            order = (
                self.repository.session.query(Order)
                .filter(Order.id == payment.order_id)
                .one_or_none()
            )
            if order and order.status == "pending":
                order.status = "paid"
                order.paid_at = paid_at

        create_payment_audit_log(
            payment_id=payment.id,
            user_id=payment.user_id,
            action="callback",
            old_status="pending",
            new_status="completed",
            ip_address=request_client,
            db=self.repository.session,
        )

        return {"code": "SUCCESS", "message": "处理成功"}

    def admin_update_payment_status(
        self,
        *,
        payment_id: int,
        payload: PaymentStatusUpdate,
        admin_user: User,
    ) -> Payment:
        with self._transaction_scope():
            payment = self.repository.get_by_id(payment_id, for_update=True)
            if not payment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="支付单不存在")

            self.repository.update_status(
                payment,
                new_status=payload.status,
                external_payment_id=payload.external_payment_id,
                external_transaction_id=payload.external_transaction_id,
            )

            if payload.callback_data:
                payment.callback_data = json.dumps(payload.callback_data, ensure_ascii=False)

        create_payment_audit_log(
            payment_id=payment_id,
            user_id=admin_user.id,
            action="admin_update",
            new_status=payload.status,
            db=self.repository.session,
        )

        self.repository.session.refresh(payment)
        return payment

    def get_payment_statistics(
        self,
        *,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Decimal | int | float | List[Dict[str, object]]]:
        session = self.repository.session
        query = session.query(Payment)

        if user_id is not None:
            query = query.filter(Payment.user_id == user_id)
        if start_date is not None:
            query = query.filter(Payment.created_at >= start_date)
        if end_date is not None:
            query = query.filter(Payment.created_at <= end_date)

        total_payments = query.count()
        completed_payments = query.filter(Payment.status == "completed").count()
        failed_payments = query.filter(Payment.status == "failed").count()

        total_amount = (
            query.filter(Payment.status == "completed")
            .with_entities(func.sum(Payment.amount))
            .scalar()
            or Decimal("0")
        )

        method_rows = (
            session.query(
                Payment.payment_method,
                func.count(Payment.id).label("count"),
                func.sum(Payment.amount).label("amount"),
            )
            .filter(Payment.status == "completed")
            .group_by(Payment.payment_method)
            .all()
        )

        method_stats = [
            {
                "method": method,
                "count": count,
                "amount": float(amount or 0),
            }
            for method, count, amount in method_rows
        ]

        return {
            "total_payments": total_payments,
            "completed_payments": completed_payments,
            "failed_payments": failed_payments,
            "success_rate": completed_payments / total_payments if total_payments else 0.0,
            "total_amount": float(total_amount),
            "payment_methods": method_stats,
        }

    def get_pending_payments(self, *, timeout_minutes: int = 30) -> List[Payment]:
        threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        return (
            self.repository.session.query(Payment)
            .filter(Payment.status == "pending", Payment.created_at < threshold)
            .all()
        )

    def cancel_expired_payments(self, *, timeout_minutes: int = 30) -> int:
        pending = self.get_pending_payments(timeout_minutes=timeout_minutes)
        cancelled = 0
        for payment in pending:
            with self._transaction_scope():
                if payment.status != "pending":
                    continue
                self.repository.update_status(payment, new_status="cancelled")
                cancelled += 1
        return cancelled

    def _can_view_payment(self, payment: Payment, user: User) -> bool:
        if getattr(user, "role", None) in {"admin", "super_admin"}:
            return True
        return payment.user_id == user.id

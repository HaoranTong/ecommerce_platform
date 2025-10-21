"""Payment service repository layer implementation.

This module encapsulates all database operations for the payment domain so
service classes can stay focused on business orchestration. The implementation
aligns with the four-layer architecture described in the design documentation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from .models import Payment, PaymentEventOutbox, PaymentTransaction


@dataclass(slots=True)
class PaymentTransactionCreate:
    """Lightweight DTO for creating payment transactions."""

    transaction_no: str
    transaction_type: str
    amount: Decimal
    status: str = "success"
    balance_before: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None
    gateway_response: Optional[Dict[str, Any]] = None
    remark: Optional[str] = None


@dataclass(slots=True)
class PaymentDomainEvent:
    """Domain event payload for outbox storage."""

    event_type: str
    payload: Dict[str, Any]
    available_at: Optional[datetime] = None


class PaymentRepository:
    """Repository responsible for payment aggregates and related entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        """Expose underlying SQLAlchemy session for transactional control."""

        return self._session

    # ---- Payment CRUD & queries -------------------------------------------------

    def create_payment(self, payment: Payment) -> Payment:
        """Persist a new payment entity and return it."""

        self._session.add(payment)
        self._session.flush()
        return payment

    def get_by_id(self, payment_id: int, *, for_update: bool = False) -> Optional[Payment]:
        """Fetch payment by primary key."""

        query = self._session.query(Payment).filter(Payment.id == payment_id)
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def find_active_for_order(self, order_id: int) -> Optional[Payment]:
        """Return existing payment that is still active for a given order."""

        return (
            self._session.query(Payment)
            .filter(
                Payment.order_id == order_id,
                Payment.status.in_(
                    [
                        "pending",
                        "processing",
                        "completed",
                    ]
                ),
            )
            .order_by(Payment.created_at.desc())
            .first()
        )

    def list_user_payments(
        self,
        *,
        user_id: int,
        order_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Payment]:
        """List payments visible to a specific user."""

        query = self._session.query(Payment).filter(Payment.user_id == user_id)
        if order_id is not None:
            query = query.filter(Payment.order_id == order_id)
        if status_filter is not None:
            query = query.filter(Payment.status == status_filter)
        return (
            query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
        )

    def list_admin_payments(
        self,
        *,
        user_id: Optional[int] = None,
        order_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        payment_method: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Payment]:
        """List payments for administrative overview."""

        query = self._session.query(Payment)
        if user_id is not None:
            query = query.filter(Payment.user_id == user_id)
        if order_id is not None:
            query = query.filter(Payment.order_id == order_id)
        if status_filter is not None:
            query = query.filter(Payment.status == status_filter)
        if payment_method is not None:
            query = query.filter(Payment.payment_method == payment_method)
        return (
            query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
        )

    def update_status(
        self,
        payment: Payment,
        *,
        new_status: str,
        external_payment_id: Optional[str] = None,
        external_transaction_id: Optional[str] = None,
    ) -> Payment:
        """Update payment status and optional external references."""

        payment.status = new_status
        if external_payment_id:
            payment.external_payment_id = external_payment_id
        if external_transaction_id:
            payment.external_transaction_id = external_transaction_id
        self._session.add(payment)
        return payment

    def get_by_payment_no(self, payment_no: str, *, for_update: bool = False) -> Optional[Payment]:
        """Fetch a payment entity by payment number with optional row-level lock."""

        query = self._session.query(Payment).filter(Payment.payment_no == payment_no)
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def ensure_callback_idempotent(self, payment: Payment) -> bool:
        """Mark callback reception timestamp if unset and return whether it was first time."""

        if payment.callback_received_at is not None:
            return False

        payment.callback_received_at = datetime.utcnow()
        self._session.add(payment)
        # No flush here; caller controls transaction boundaries.
        return True

    def mark_callback_processed(
        self,
        payment: Payment,
        *,
        callback_payload: Union[str, Dict[str, Any]],
        external_payment_id: Optional[str],
        external_transaction_id: Optional[str],
        paid_at: datetime,
    ) -> Payment:
        """Persist callback result details and return the updated entity."""

        payload_raw = (
            json.dumps(callback_payload, ensure_ascii=False)
            if isinstance(callback_payload, dict)
            else callback_payload
        )

        payment.status = "completed"
        payment.paid_at = paid_at
        payment.callback_data = payload_raw

        if external_payment_id:
            payment.external_payment_id = external_payment_id
        if external_transaction_id:
            payment.external_transaction_id = external_transaction_id

        self._session.add(payment)
        return payment

    def append_transaction(
        self,
        payment_id: int,
        transaction: PaymentTransactionCreate,
    ) -> PaymentTransaction:
        """Insert a payment transaction record bound to the given payment."""

        record = PaymentTransaction(
            payment_id=payment_id,
            transaction_no=transaction.transaction_no,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
            status=transaction.status,
            gateway_response=json.dumps(transaction.gateway_response, ensure_ascii=False)
            if transaction.gateway_response
            else None,
            remark=transaction.remark,
        )
        self._session.add(record)
        self._session.flush()
        return record

    def enqueue_event(self, event: PaymentDomainEvent, *, payment_id: Optional[int] = None) -> PaymentEventOutbox:
        """Persist a domain event into the outbox table for asynchronous dispatch."""

        record = PaymentEventOutbox(
            payment_id=payment_id,
            event_type=event.event_type,
            payload=event.payload,
            status="pending",
            available_at=event.available_at or datetime.utcnow(),
        )
        self._session.add(record)
        self._session.flush()
        return record

    def fetch_pending_outbox(self, *, limit: int = 100) -> List[PaymentEventOutbox]:
        """Retrieve pending outbox events that are ready for dispatch."""

        return (
            self._session.query(PaymentEventOutbox)
            .filter(
                PaymentEventOutbox.status == "pending",
                PaymentEventOutbox.available_at <= datetime.utcnow(),
            )
            .order_by(PaymentEventOutbox.available_at.asc())
            .limit(limit)
            .all()
        )

    def mark_outbox_sending(self, event: PaymentEventOutbox) -> PaymentEventOutbox:
        """Mark an event as being sent to the message bus."""

        event.status = "sending"
        event.last_error = None
        self._session.add(event)
        return event

    def mark_outbox_sent(
        self,
        event: PaymentEventOutbox,
        *,
        delivered_at: Optional[datetime] = None,
    ) -> PaymentEventOutbox:
        """Mark an event as successfully dispatched."""

        event.status = "sent"
        event.delivered_at = delivered_at or datetime.utcnow()
        event.last_error = None
        self._session.add(event)
        return event

    def mark_outbox_retry(
        self,
        event: PaymentEventOutbox,
        *,
        error: str,
        max_retries: int = 5,
    ) -> PaymentEventOutbox:
        """Increment retry count and decide the next status for a failing event."""

        event.retry_count += 1
        event.last_error = error
        if event.retry_count >= max_retries:
            event.status = "failed"
        else:
            event.status = "pending"
            event.available_at = datetime.utcnow()
        self._session.add(event)
        return event


__all__ = [
    "PaymentRepository",
    "PaymentTransactionCreate",
    "PaymentDomainEvent",
]

"""Unit tests for the payment repository layer.

These tests focus on the bespoke data access helpers implemented in
``app.modules.payment_service.repository``. They use the in-memory SQLite
fixture from ``tests.conftest`` so we can exercise real SQLAlchemy behaviour
without spinning up MySQL.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable

import pytest
from sqlalchemy.orm import Session

from app.modules.order_management.models import Order
from app.modules.payment_service.models import Payment, PaymentEventOutbox, PaymentTransaction
from app.modules.payment_service.repository import (
    PaymentDomainEvent,
    PaymentRepository,
    PaymentTransactionCreate,
)
from app.modules.user_auth.models import User
from tests.factories.order_management_factories import OrderFactory
from tests.factories.payment_service_factories import PaymentFactory
from tests.factories.user_auth_factories import UserFactory


@pytest.fixture
def repository(unit_test_db: Session) -> PaymentRepository:  # pragma: no cover - fixture helper
    return PaymentRepository(unit_test_db)


@pytest.fixture(autouse=True)
def _configure_factories(unit_test_db: Session):  # pragma: no cover - helper
    """Bind Factory Boy factories to the unit test session."""

    UserFactory._meta.sqlalchemy_session = unit_test_db
    OrderFactory._meta.sqlalchemy_session = unit_test_db
    PaymentFactory._meta.sqlalchemy_session = unit_test_db
    yield


@pytest.fixture
def make_payment(unit_test_db: Session) -> Callable[..., Payment]:  # pragma: no cover - helper
    def _maker(
        *,
        status: str = "pending",
        payment_method: str = "wechat",
        amount: Decimal = Decimal("99.99"),
        user: User | None = None,
        order: Order | None = None,
    ) -> Payment:
        local_user = user or UserFactory()
        local_order = order or OrderFactory(user_id=local_user.id, total_amount=Decimal("199.99"))

        payment = PaymentFactory(
            order_id=local_order.id,
            user_id=local_user.id,
            status=status,
            amount=amount,
            payment_method=payment_method,
            currency="CNY",
            callback_received_at=None,
        )

        unit_test_db.refresh(payment)
        return payment

    return _maker


def test_create_payment_persists_entity(repository: PaymentRepository, unit_test_db: Session) -> None:
    user = UserFactory()
    order = OrderFactory(user_id=user.id, total_amount=Decimal("10.00"))

    payment = Payment(
        order_id=order.id,
        user_id=user.id,
        payment_no="PAY-create",
        payment_method="wechat",
        amount=Decimal("10.00"),
        currency="CNY",
        status="pending",
    )

    repository.create_payment(payment)
    unit_test_db.commit()

    assert payment.id is not None
    fetched = unit_test_db.get(Payment, payment.id)
    assert fetched is not None
    assert fetched.payment_no == "PAY-create"


def test_find_active_for_order_returns_latest(repository: PaymentRepository, make_payment: Callable[..., Payment]) -> None:
    user = UserFactory()
    order = OrderFactory(user_id=user.id, total_amount=Decimal("50.00"))

    make_payment(status="failed", user=user, order=order)
    second = make_payment(status="processing", user=user, order=order)

    active = repository.find_active_for_order(order.id)

    assert active is not None
    assert active.id == second.id


def test_list_user_payments_filters_by_status(repository: PaymentRepository, make_payment: Callable[..., Payment]) -> None:
    user = UserFactory()
    order = OrderFactory(user_id=user.id)

    active_payment = make_payment(status="completed", user=user, order=order)
    make_payment(status="failed")

    results = repository.list_user_payments(
        user_id=user.id,
        status_filter="completed",
        limit=5,
        offset=0,
    )

    assert len(results) == 1
    assert results[0].status == "completed"


def test_ensure_callback_idempotent_marks_timestamp(repository: PaymentRepository, make_payment: Callable[..., Payment], unit_test_db: Session) -> None:
    payment = make_payment(status="pending")

    first_time = repository.ensure_callback_idempotent(payment)
    second_time = repository.ensure_callback_idempotent(payment)
    unit_test_db.commit()

    assert first_time is True
    assert second_time is False
    assert payment.callback_received_at is not None


def test_append_transaction_persists_record(repository: PaymentRepository, make_payment: Callable[..., Payment], unit_test_db: Session) -> None:
    payment = make_payment(status="pending")

    record = repository.append_transaction(
        payment_id=payment.id,
        transaction=PaymentTransactionCreate(
            transaction_no="TRX-append",
            transaction_type="payment",
            amount=Decimal("99.99"),
            gateway_response={"status": "ok"},
        ),
    )
    unit_test_db.commit()

    fetched = unit_test_db.get(PaymentTransaction, record.id)
    assert fetched is not None
    assert fetched.payment_id == payment.id
    assert fetched.status == "success"
    assert fetched.gateway_response is not None


def test_outbox_lifecycle(repository: PaymentRepository, make_payment: Callable[..., Payment], unit_test_db: Session) -> None:
    payment = make_payment(status="pending")
    event = repository.enqueue_event(
        PaymentDomainEvent(
            event_type="PaymentCreated",
            payload={"payment_id": payment.id},
            available_at=datetime.utcnow() - timedelta(minutes=1),
        ),
        payment_id=payment.id,
    )
    unit_test_db.commit()

    pending = repository.fetch_pending_outbox(limit=10)
    assert len(pending) == 1
    assert pending[0].id == event.id

    repository.mark_outbox_sending(event)
    repository.mark_outbox_sent(event, delivered_at=datetime.utcnow())
    unit_test_db.commit()

    refreshed = unit_test_db.get(PaymentEventOutbox, event.id)
    assert refreshed.status == "sent"
    assert refreshed.delivered_at is not None


def test_mark_outbox_retry_transitions_to_failed(repository: PaymentRepository, make_payment: Callable[..., Payment], unit_test_db: Session) -> None:
    payment = make_payment(status="pending")
    event = repository.enqueue_event(
        PaymentDomainEvent(
            event_type="PaymentCreated",
            payload={"payment_id": payment.id},
            available_at=datetime.utcnow() - timedelta(minutes=5),
        ),
        payment_id=payment.id,
    )

    for _ in range(5):
        repository.mark_outbox_retry(event, error="timeout", max_retries=5)
    unit_test_db.commit()

    refreshed = unit_test_db.get(PaymentEventOutbox, event.id)
    assert refreshed.status == "failed"
    assert refreshed.retry_count == 5

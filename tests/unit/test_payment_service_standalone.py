"""Smoke-level standalone tests for the payment service.

These tests exercise the PaymentService in isolation using the real
repository + SQLite unit session while replacing external adapters with
lightweight stubs. They focus on verifying that core orchestration steps
persist data and interact with collaborators as expected.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Dict

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.modules.payment_service.models import PaymentEventOutbox, PaymentTransaction
from app.modules.payment_service.repository import PaymentRepository
from app.modules.payment_service.schemas import PaymentCreate, WechatPaymentCallback
from app.modules.payment_service.service import PaymentService
from app.modules.payment_service.utils import PaymentNumberGenerator, PaymentValidator
from tests.factories.data_factory import StandardTestDataFactory


class StubWechatAdapter:
    def __init__(self) -> None:
        self.created_orders: list[Dict[str, object]] = []
        self.verified_payloads: list[tuple[Dict[str, object], str]] = []

    def create_unified_order(self, *, payment_no: str, amount: Decimal, description: str, user_openid: str | None = None) -> Dict[str, str]:
        self.created_orders.append({
            "payment_no": payment_no,
            "amount": amount,
            "description": description,
            "user_openid": user_openid,
        })
        return {
            "trade_type": "NATIVE",
            "code_url": f"mock://qr/{payment_no}",
            "prepay_id": f"mock-prepay-{payment_no}",
        }

    def verify_callback_signature(self, data: Dict[str, object], signature: str) -> bool:
        self.verified_payloads.append((data, signature))
        return signature == "valid"


class StubNumberGenerator(PaymentNumberGenerator):
    def __init__(self) -> None:
        self.counter = 0

    def generate_payment_no(self) -> str:
        self.counter += 1
        return f"PAY-STUB-{self.counter:03d}"
class NestedTransactionSession:
    """Wrap a SQLAlchemy session so begin() delegates to a nested transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def begin(self):  # pragma: no cover - proxy helper
        return self._session.begin_nested()

    def __getattr__(self, name):  # pragma: no cover - proxy helper
        return getattr(self._session, name)


@pytest.fixture
def service_ctx(unit_test_db: Session):
    session_factory = sessionmaker(bind=unit_test_db.get_bind(), autocommit=False, autoflush=False)
    service_db = session_factory()
    wrapped_session = NestedTransactionSession(service_db)
    wechat = StubWechatAdapter()
    number_gen = StubNumberGenerator()
    validator = PaymentValidator()
    service = PaymentService(
        repository=PaymentRepository(wrapped_session),
        wechat_adapter=wechat,
        number_generator=number_gen,
        validator=validator,
    )
    yield {
        "service": service,
        "repo": service.repository,
        "wechat": wechat,
        "number_gen": number_gen,
        "db": wrapped_session,
        "_raw": service_db,
    }
    service_db.close()


@pytest.fixture
def make_user_and_order(unit_test_db):
    factory = StandardTestDataFactory()

    def _creator(*, total_amount: Decimal = Decimal("109.99")):
        user = factory.create_user(unit_test_db)
        order = factory.create_order(unit_test_db, user_id=user.id, total_amount=total_amount)
        unit_test_db.refresh(user)
        unit_test_db.refresh(order)
        return user, order

    return _creator


def test_create_payment_wechat_success(service_ctx, make_user_and_order):
    service: PaymentService = service_ctx["service"]
    wechat: StubWechatAdapter = service_ctx["wechat"]
    repo: PaymentRepository = service_ctx["repo"]

    user, order = make_user_and_order()
    user.wx_openid = "openid-123"

    payload = PaymentCreate(
        order_id=order.id,
        payment_method="wechat",
        amount=None,
        description="支付测试",
    )

    payment = service.create_payment(order=order, payload=payload, current_user=user)

    assert payment.payment_no == "PAY-STUB-001"
    assert payment.qr_code == f"mock://qr/{payment.payment_no}"
    assert payment.pay_url == f"mock-prepay-{payment.payment_no}"
    assert wechat.created_orders[-1]["user_openid"] == "openid-123"

    outbox_rows = repo.session.query(PaymentEventOutbox).all()
    assert any(event.event_type == "PaymentCreated" for event in outbox_rows)


def test_process_wechat_callback_marks_payment_complete(service_ctx, make_user_and_order):
    service: PaymentService = service_ctx["service"]
    wechat: StubWechatAdapter = service_ctx["wechat"]
    repo: PaymentRepository = service_ctx["repo"]
    db = service_ctx["db"]

    user, order = make_user_and_order()
    payload = PaymentCreate(
        order_id=order.id,
        payment_method="wechat",
        amount=None,
        description="订单支付",
    )

    payment = service.create_payment(order=order, payload=payload, current_user=user)

    callback_body = {
        "out_trade_no": payment.payment_no,
        "transaction_id": "wx_tx_001",
        "trade_state": "SUCCESS",
        "trade_state_desc": "支付成功",
    }
    callback = WechatPaymentCallback(
        payment_no=payment.payment_no,
        status="SUCCESS",
        transaction_id="wx_tx_001",
        amount=payment.amount,
        callback_data=callback_body,
        out_trade_no=payment.payment_no,
        trade_state="SUCCESS",
        trade_state_desc="支付成功",
    )

    response = service.process_wechat_callback(
        callback=callback,
        headers={"Wechatpay-Signature": "valid"},
        request_client="127.0.0.1",
    )

    db.refresh(payment)

    assert response == {"code": "SUCCESS", "message": "处理成功"}
    assert payment.status == "completed"
    assert json.loads(payment.callback_data)["trade_state"] == "SUCCESS"
    assert payment.paid_at is not None

    transactions = db.query(PaymentTransaction).filter_by(payment_id=payment.id).all()
    assert len(transactions) == 1

    events = repo.fetch_pending_outbox(limit=10)
    assert any(event.event_type == "PaymentCompleted" for event in events)
    assert wechat.verified_payloads[-1][1] == "valid"

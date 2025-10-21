"""Unit tests for :mod:`app.modules.payment_service.service`.

These tests follow the service-layer testing strategy defined in
``docs/standards/testing-standards.md`` by mocking the repository so we can
focus purely on business rules and collaborator interactions without touching
an actual database.
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
import json
import pytest
from fastapi import HTTPException

from app.modules.payment_service.models import Payment
from app.modules.payment_service.repository import PaymentDomainEvent, PaymentTransactionCreate
from app.modules.payment_service.schemas import (
    PaymentCreate,
    PaymentStatusUpdate,
    WechatPaymentCallback,
)
from app.modules.payment_service.service import PaymentService


@pytest.fixture
def service_dependencies(mocker):
    """Build a fully mocked service context for each test."""

    session = mocker.MagicMock()
    begin_cm = mocker.MagicMock()
    begin_cm.__enter__.return_value = None
    begin_cm.__exit__.return_value = False
    session.begin.return_value = begin_cm

    repository = mocker.MagicMock()
    repository.session = session

    wechat_adapter = mocker.MagicMock()
    number_generator = mocker.MagicMock()
    validator = mocker.MagicMock()

    service = PaymentService(
        repository=repository,
        wechat_adapter=wechat_adapter,
        number_generator=number_generator,
        validator=validator,
    )

    session.refresh.side_effect = lambda _: None

    return {
        "service": service,
        "repository": repository,
        "session": session,
        "wechat": wechat_adapter,
        "number_generator": number_generator,
        "validator": validator,
    }


def test_create_payment_wechat_success(mocker, service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]
    wechat = deps["wechat"]
    number_generator = deps["number_generator"]
    validator = deps["validator"]

    mocker.patch("app.modules.payment_service.service.create_payment_audit_log")

    validator.validate_amount.return_value = True
    validator.validate_payment_method.return_value = True
    repository.find_active_for_order.return_value = None
    number_generator.generate_payment_no.return_value = "PAY-STUB-001"

    def _mark_persisted(payment: Payment):
        payment.id = 101
        return payment

    repository.create_payment.side_effect = _mark_persisted
    wechat.create_unified_order.return_value = {
        "code_url": "mock://qr/PAY-STUB-001",
        "prepay_id": "mock-prepay-PAY-STUB-001",
        "trade_type": "NATIVE",
    }

    order = SimpleNamespace(id=10, total_amount=Decimal("199.99"), order_no="ORD-001")
    user = SimpleNamespace(id=5, wx_openid="openid-123", role="user")
    payload = PaymentCreate(
        order_id=order.id,
        payment_method="wechat",
        amount=None,
        description="支付订单",
    )

    payment = deps["service"].create_payment(order=order, payload=payload, current_user=user)

    assert payment.payment_no == "PAY-STUB-001"
    assert payment.qr_code == "mock://qr/PAY-STUB-001"
    assert payment.pay_url == "mock-prepay-PAY-STUB-001"

    repository.create_payment.assert_called_once()
    wechat.create_unified_order.assert_called_once_with(
        payment_no="PAY-STUB-001",
        amount=payment.amount,
        description="支付订单",
        user_openid="openid-123",
    )
    event = repository.enqueue_event.call_args.args[0]
    assert isinstance(event, PaymentDomainEvent)
    assert event.event_type == "PaymentCreated"


def test_create_payment_rejects_existing_active_payment(mocker, service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]
    validator = deps["validator"]

    mocker.patch("app.modules.payment_service.service.create_payment_audit_log")

    validator.validate_amount.return_value = True
    validator.validate_payment_method.return_value = True
    repository.find_active_for_order.return_value = SimpleNamespace(status="pending")

    order = SimpleNamespace(id=22, total_amount=Decimal("88.00"), order_no="ORD-002")
    user = SimpleNamespace(id=9, role="user")
    payload = PaymentCreate(order_id=order.id, payment_method="wechat", amount=None)

    with pytest.raises(HTTPException) as exc:
        deps["service"].create_payment(order=order, payload=payload, current_user=user)

    assert exc.value.status_code == 400
    repository.create_payment.assert_not_called()


def test_process_wechat_callback_success(mocker, service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]
    session = deps["session"]
    wechat = deps["wechat"]

    mocker.patch("app.modules.payment_service.service.create_payment_audit_log")
    mocker.patch("app.modules.payment_service.service.uuid.uuid4", return_value=SimpleNamespace(hex="abcd" * 8))

    wechat.verify_callback_signature.return_value = True

    payment = Payment(
        order_id=17,
        user_id=3,
        payment_method="wechat",
        amount=Decimal("120.00"),
        currency="CNY",
        status="pending",
        payment_no="PAY-200",
    )
    payment.id = 7001
    repository.get_by_payment_no.return_value = payment
    repository.ensure_callback_idempotent.return_value = True
    repository.mark_callback_processed.side_effect = (
        lambda payment_obj, *, callback_payload, external_payment_id, external_transaction_id, paid_at: payment_obj.__setattr__("status", "completed")
        or payment_obj.__setattr__("callback_data", json.dumps(callback_payload))
        or payment_obj.__setattr__("paid_at", paid_at)
        or payment_obj
    )

    order_record = SimpleNamespace(id=17, status="pending", paid_at=None)
    session.query.return_value.filter.return_value.one_or_none.return_value = order_record

    callback = WechatPaymentCallback(
        payment_no="PAY-200",
        status="SUCCESS",
        transaction_id="wx-tx-01",
        amount=payment.amount,
        callback_data={"ok": True},
        out_trade_no="PAY-200",
        trade_state="SUCCESS",
        trade_state_desc="支付成功",
    )

    response = deps["service"].process_wechat_callback(
        callback=callback,
        headers={"Wechatpay-Signature": "valid"},
        request_client="127.0.0.1",
    )

    assert response == {"code": "SUCCESS", "message": "处理成功"}
    repository.mark_callback_processed.assert_called_once()
    repository.append_transaction.assert_called_once()
    txn_args = repository.append_transaction.call_args.kwargs
    assert isinstance(txn_args["transaction"], PaymentTransactionCreate)
    assert txn_args["transaction"].amount == payment.amount
    assert payment.status == "completed"
    assert order_record.status == "paid"


def test_process_wechat_callback_detects_duplicate_notification(mocker, service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]
    wechat = deps["wechat"]

    mocker.patch("app.modules.payment_service.service.create_payment_audit_log")

    wechat.verify_callback_signature.return_value = True

    payment = Payment(
        order_id=1,
        user_id=2,
        payment_method="wechat",
        amount=Decimal("50.00"),
        currency="CNY",
        status="pending",
        payment_no="PAY-dup",
    )
    payment.id = 9
    repository.get_by_payment_no.return_value = payment
    repository.ensure_callback_idempotent.return_value = False

    callback = WechatPaymentCallback(
        payment_no="PAY-dup",
        status="SUCCESS",
        transaction_id="tx-dup",
        amount=payment.amount,
        callback_data={},
        out_trade_no="PAY-dup",
        trade_state="SUCCESS",
        trade_state_desc="重复",
    )

    result = deps["service"].process_wechat_callback(
        callback=callback,
        headers={"Wechatpay-Signature": "valid"},
        request_client=None,
    )

    assert result == {"code": "SUCCESS", "message": "重复通知已忽略"}
    repository.mark_callback_processed.assert_not_called()
    repository.append_transaction.assert_not_called()


def test_admin_update_payment_status_sets_callback_payload(mocker, service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]

    audit_log = mocker.patch("app.modules.payment_service.service.create_payment_audit_log")

    payment = Payment(
        order_id=3,
        user_id=8,
        payment_method="wechat",
        amount=Decimal("75.00"),
        currency="CNY",
        status="pending",
    )
    payment.id = 300
    repository.get_by_id.return_value = payment

    payload = PaymentStatusUpdate(
        status="failed",
        external_payment_id="EP-1",
        external_transaction_id="TX-1",
        callback_data={"reason": "manual"},
    )
    admin = SimpleNamespace(id=99, role="admin")

    updated = deps["service"].admin_update_payment_status(
        payment_id=payment.id,
        payload=payload,
        admin_user=admin,
    )

    repository.update_status.assert_called_once_with(
        payment,
        new_status="failed",
        external_payment_id="EP-1",
        external_transaction_id="TX-1",
    )
    assert json.loads(payment.callback_data)["reason"] == "manual"
    audit_log.assert_called_once()
    assert updated is payment


def test_get_payment_enforces_ownership(service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]

    payment = Payment(
        order_id=1,
        user_id=1,
        payment_method="wechat",
        amount=Decimal("10.00"),
        currency="CNY",
        status="pending",
    )
    payment.id = 1
    repository.get_by_id.return_value = payment

    current_user = SimpleNamespace(id=2, role="customer")

    with pytest.raises(HTTPException) as exc:
        deps["service"].get_payment(payment_id=1, current_user=current_user)

    assert exc.value.status_code == 403


def test_get_payment_allows_admin(service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]

    payment = Payment(
        order_id=2,
        user_id=1,
        payment_method="wechat",
        amount=Decimal("15.00"),
        currency="CNY",
        status="completed",
    )
    payment.id = 5
    repository.get_by_id.return_value = payment

    admin_user = SimpleNamespace(id=7, role="admin")

    result = deps["service"].get_payment(payment_id=5, current_user=admin_user)

    assert result is payment


def test_cancel_expired_payments_updates_status(mocker, service_dependencies):
    deps = service_dependencies
    repository = deps["repository"]

    old_payment = Payment(
        order_id=11,
        user_id=4,
        payment_method="wechat",
        amount=Decimal("45.00"),
        currency="CNY",
        status="pending",
    )
    with mocker.patch.object(PaymentService, "get_pending_payments", return_value=[old_payment]):
        cancelled = deps["service"].cancel_expired_payments(timeout_minutes=30)

    assert cancelled == 1
    repository.update_status.assert_called_once_with(old_payment, new_status="cancelled")


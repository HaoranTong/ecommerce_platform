"""支付服务模块集成测试。

这些测试使用真实MySQL数据库和FastAPI依赖，覆盖支付创建、查询以及微信回调流程。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict

import pytest

from app.adapters.payment import WechatPayAdapter
from app.modules.order_management.models import Order
from app.modules.payment_service.models import Payment
from tests.factories.data_factory import StandardTestDataFactory


@pytest.mark.integration
class TestPaymentServiceIntegration:
    """验证支付服务核心端到端流程。"""

    def test_create_payment_via_api(self, api_client, mysql_integration_db) -> None:
        factory = StandardTestDataFactory()
        token, user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(token)

        order = factory.create_order(
            mysql_integration_db,
            user_id=user.id,
            subtotal=Decimal("120.00"),
            shipping_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("120.00"),
        )

        response = api_client.post(
            "/api/v1/payment-service/payments",
            json={
                "order_id": order.id,
                "payment_method": "wechat",
                "description": "测试订单支付",
            },
        )

        api_client.clear_auth_headers()

        assert response.status_code == 201
        payload = response.json()
        assert payload["success"] is True
        data = payload["data"]
        assert data["order_id"] == order.id
        assert data["status"] == "pending"

        payment = (
            mysql_integration_db.query(Payment)
            .filter(Payment.payment_no == data["payment_no"])
            .one()
        )
        assert payment.user_id == user.id
        assert payment.amount == Decimal("120.00")
        assert payment.payment_method == "wechat"
        assert payment.status == "pending"

    def test_list_payments_for_user(self, api_client, mysql_integration_db) -> None:
        factory = StandardTestDataFactory()
        token, user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(token)

        order = factory.create_order(
            mysql_integration_db,
            user_id=user.id,
            subtotal=Decimal("88.00"),
            shipping_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("88.00"),
        )

        create_resp = api_client.post(
            "/api/v1/payment-service/payments",
            json={
                "order_id": order.id,
                "payment_method": "wechat",
                "description": "列表查询测试",
            },
        )
        assert create_resp.status_code == 201
        created = create_resp.json()["data"]

        list_resp = api_client.get("/api/v1/payment-service/payments")
        api_client.clear_auth_headers()

        assert list_resp.status_code == 200
        payload = list_resp.json()
        assert payload["success"] is True
        results = payload["data"]
        assert isinstance(results, list)
        assert any(item["payment_no"] == created["payment_no"] for item in results)

    def test_wechat_callback_updates_payment(self, api_client, mysql_integration_db) -> None:
        factory = StandardTestDataFactory()
        token, user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(token)

        order = factory.create_order(
            mysql_integration_db,
            user_id=user.id,
            subtotal=Decimal("150.00"),
            shipping_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("150.00"),
        )

        create_resp = api_client.post(
            "/api/v1/payment-service/payments",
            json={
                "order_id": order.id,
                "payment_method": "wechat",
                "description": "回调流程测试",
            },
        )
        assert create_resp.status_code == 201
        payment_payload = create_resp.json()["data"]
        payment_no = payment_payload["payment_no"]

        api_client.clear_auth_headers()

        adapter = WechatPayAdapter()
        callback_data: Dict[str, str] = {
            "out_trade_no": payment_no,
            "transaction_id": "WXTX1234567890",
            "trade_state": "SUCCESS",
            "trade_state_desc": "支付成功",
        }
        signature = adapter._generate_sign(callback_data)  # type: ignore[attr-defined]

        callback_resp = api_client.post(
            "/api/v1/payment-service/payments/callback/wechat",
            json={
                "payment_no": payment_no,
                "status": "SUCCESS",
                "transaction_id": "WXTX1234567890",
                "amount": str(payment_payload["amount"]),
                "callback_data": callback_data,
                "out_trade_no": payment_no,
                "trade_state": "SUCCESS",
                "trade_state_desc": "支付成功",
            },
            headers={"Wechatpay-Signature": signature},
        )

        assert callback_resp.status_code == 200
        assert callback_resp.json() == {"code": "SUCCESS", "message": "处理成功"}

        mysql_integration_db.expire_all()
        payment = (
            mysql_integration_db.query(Payment)
            .filter(Payment.payment_no == payment_no)
            .one()
        )
        assert payment.status == "completed"
        assert payment.paid_at is not None

        order_record = (
            mysql_integration_db.query(Order)
            .filter(Order.id == order.id)
            .one()
        )
        assert order_record.status == "paid"

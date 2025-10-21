"""支付服务端到端测试。"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict

import pytest

from app.adapters.payment import WechatPayAdapter
from app.modules.order_management.models import Order
from app.modules.payment_service.models import Payment
from tests.factories.data_factory import StandardTestDataFactory


@pytest.mark.e2e
@pytest.mark.asyncio
class TestPaymentServiceE2EWorkflow:
    """覆盖用户视角下的核心支付流程。"""

    async def test_user_creates_and_lists_payments(self, async_api_client) -> None:
        factory = StandardTestDataFactory()
        token, user = await async_api_client.authenticate_as_user()
        async_api_client.headers["Authorization"] = f"Bearer {token}"

        order = factory.create_order(
            async_api_client.db,
            user_id=user.id,
            subtotal=Decimal("68.00"),
            shipping_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("68.00"),
        )

        create_resp = await async_api_client.post(
            "/api/v1/payment-service/payments",
            json={
                "order_id": order.id,
                "payment_method": "wechat",
                "description": "E2E创建测试",
            },
        )
        if create_resp.status_code != 201:
            print("create payment response:", create_resp.status_code, create_resp.text)
        assert create_resp.status_code == 201
        created = create_resp.json()["data"]

        list_resp = await async_api_client.get("/api/v1/payment-service/payments")
        async_api_client.headers.pop("Authorization", None)

        assert list_resp.status_code == 200
        payload = list_resp.json()
        assert payload["success"] is True
        records = payload["data"]
        assert any(item["payment_no"] == created["payment_no"] for item in records)

    async def test_wechat_callback_flow(self, async_api_client) -> None:
        factory = StandardTestDataFactory()
        token, user = await async_api_client.authenticate_as_user()
        async_api_client.headers["Authorization"] = f"Bearer {token}"

        order = factory.create_order(
            async_api_client.db,
            user_id=user.id,
            subtotal=Decimal("99.00"),
            shipping_fee=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("99.00"),
        )

        create_resp = await async_api_client.post(
            "/api/v1/payment-service/payments",
            json={
                "order_id": order.id,
                "payment_method": "wechat",
                "description": "E2E回调测试",
            },
        )
        if create_resp.status_code != 201:
            print("create payment response:", create_resp.status_code, create_resp.text)
        assert create_resp.status_code == 201
        payment_payload = create_resp.json()["data"]
        payment_no = payment_payload["payment_no"]

        async_api_client.headers.pop("Authorization", None)

        adapter = WechatPayAdapter()
        callback_data: Dict[str, str] = {
            "out_trade_no": payment_no,
            "transaction_id": "WXE2E987654321",
            "trade_state": "SUCCESS",
            "trade_state_desc": "支付成功",
        }
        signature = adapter._generate_sign(callback_data)  # type: ignore[attr-defined]

        callback_resp = await async_api_client.post(
            "/api/v1/payment-service/payments/callback/wechat",
            json={
                "payment_no": payment_no,
                "status": "SUCCESS",
                "transaction_id": "WXE2E987654321",
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

        async_api_client.db.expire_all()
        payment = (
            async_api_client.db.query(Payment)
            .filter(Payment.payment_no == payment_no)
            .one()
        )
        assert payment.status == "completed"
        assert payment.paid_at is not None

        order_record = (
            async_api_client.db.query(Order)
            .filter(Order.id == order.id)
            .one()
        )
        assert order_record.status == "paid"


@pytest.mark.e2e
@pytest.mark.asyncio
class TestPaymentServiceE2ESecurity:
    """验证支付接口的认证行为。"""

    async def test_unauthenticated_requests_are_rejected(self, async_api_client) -> None:
        response = await async_api_client.get("/api/v1/payment-service/payments")
        assert response.status_code in {401, 403}


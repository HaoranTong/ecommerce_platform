"""Payment service API router aligned with the layered architecture."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import get_current_active_user, get_current_admin_user
from app.modules.user_auth.models import User
from app.shared.response import ApiResponse, success_response

from .auth_helpers import verify_order_ownership_for_payment
from .dependencies import get_payment_service
from .schemas import PaymentCreate, PaymentRead, PaymentStatusUpdate, WechatPaymentCallback
from .service import PaymentService


router = APIRouter()


@router.post(
    "/payment-service/payments",
    response_model=ApiResponse[PaymentRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Create a payment order for the current user."""

    order = await verify_order_ownership_for_payment(
        payment_data.order_id,
        current_user=current_user,
        db=payment_service.repository.session,
    )

    try:
        payment = payment_service.create_payment(
            order=order,
            payload=payment_data,
            current_user=current_user,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建支付失败: {exc}",
        ) from exc

    return success_response(
        data=PaymentRead.model_validate(payment),
        message="创建支付成功",
    )


@router.get("/payment-service/payments/{payment_id}", response_model=ApiResponse[PaymentRead])
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Retrieve a payment visible to the current user."""

    payment = payment_service.get_payment(
        payment_id=payment_id,
        current_user=current_user,
    )
    return success_response(
        data=PaymentRead.model_validate(payment),
        message="获取支付详情成功",
    )


@router.get(
    "/payment-service/payments",
    response_model=ApiResponse[List[PaymentRead]],
)
async def list_payments(
    order_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """List payments for the current user or all payments for admins."""

    if getattr(current_user, "role", None) in {"admin", "super_admin"}:
        payments = payment_service.list_payments_for_admin(
            order_id=order_id,
            user_id=None,
            status_filter=status_filter,
            payment_method=None,
            limit=limit,
            offset=offset,
        )
    else:
        payments = payment_service.list_payments_for_user(
            current_user=current_user,
            order_id=order_id,
            status_filter=status_filter,
            limit=limit,
            offset=offset,
        )

    payload = [PaymentRead.model_validate(payment) for payment in payments]
    return success_response(
        data=payload,
        message="获取支付列表成功",
    )


@router.post("/payment-service/payments/callback/wechat")
async def wechat_payment_callback(
    callback_data: WechatPaymentCallback,
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Handle WeChat payment callbacks."""

    result = payment_service.process_wechat_callback(
        callback=callback_data,
        headers=request.headers,
        request_client=request.client.host if request.client else None,
    )
    return result


@router.get(
    "/payment-service/admin/payments",
    response_model=ApiResponse[List[PaymentRead]],
)
async def admin_list_all_payments(
    user_id: Optional[int] = None,
    order_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    payment_method: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_admin: User = Depends(get_current_admin_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """List payments for administrative views."""

    payments = payment_service.list_payments_for_admin(
        order_id=order_id,
        user_id=user_id,
        status_filter=status_filter,
        payment_method=payment_method,
        limit=limit,
        offset=offset,
    )
    payload = [PaymentRead.model_validate(payment) for payment in payments]
    return success_response(data=payload, message="获取支付记录成功")


@router.patch(
    "/payment-service/admin/payments/{payment_id}/status",
    response_model=ApiResponse[PaymentRead],
)
async def admin_update_payment_status(
    payment_id: int,
    status_update: PaymentStatusUpdate,
    current_admin: User = Depends(get_current_admin_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Allow administrators to adjust payment status when needed."""

    payment = payment_service.admin_update_payment_status(
        payment_id=payment_id,
        payload=status_update,
        admin_user=current_admin,
    )
    return success_response(
        data=PaymentRead.model_validate(payment),
        message="更新支付状态成功",
    )

"""Dependency definitions for the payment service module."""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.payment import WechatPayAdapter
from app.core.database import get_db

from .repository import PaymentRepository
from .service import PaymentService
from .utils import PaymentNumberGenerator, PaymentValidator


@lru_cache
def _get_payment_validator() -> PaymentValidator:
	return PaymentValidator()


@lru_cache
def _get_payment_number_generator() -> PaymentNumberGenerator:
	return PaymentNumberGenerator()


@lru_cache
def _get_wechat_adapter() -> WechatPayAdapter:
	return WechatPayAdapter()


def get_payment_validator() -> PaymentValidator:
	"""Return a shared payment validator instance."""

	return _get_payment_validator()


def get_payment_number_generator() -> PaymentNumberGenerator:
	"""Return a shared payment number generator instance."""

	return _get_payment_number_generator()


def get_wechat_adapter() -> WechatPayAdapter:
	"""Return a shared WeChat adapter instance."""

	return _get_wechat_adapter()


def get_payment_repository(db: Session = Depends(get_db)) -> PaymentRepository:
	"""Provide a repository bound to the current database session."""

	return PaymentRepository(db)


def get_payment_service(
	repository: PaymentRepository = Depends(get_payment_repository),
	wechat_adapter: WechatPayAdapter = Depends(get_wechat_adapter),
	number_generator: PaymentNumberGenerator = Depends(get_payment_number_generator),
	validator: PaymentValidator = Depends(get_payment_validator),
) -> PaymentService:
	"""Construct the payment application service with its dependencies."""

	return PaymentService(
		repository=repository,
		wechat_adapter=wechat_adapter,
		number_generator=number_generator,
		validator=validator,
	)


__all__ = [
	"get_payment_service",
	"get_payment_repository",
	"get_payment_validator",
	"get_payment_number_generator",
	"get_wechat_adapter",
]

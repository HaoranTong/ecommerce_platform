"""Payment outbox worker utilities.

Provides helper functions to consume payment domain events stored in the
`payment_event_outbox` table and forward them to the message infrastructure.
"""

from __future__ import annotations

import logging
from typing import Callable, Protocol

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from ..repository import PaymentRepository

logger = logging.getLogger("payment_outbox_worker")


class PaymentEventPublisher(Protocol):
    """Minimal publisher contract used by the outbox worker."""

    def publish(self, event_type: str, payload: dict) -> None:
        """Publish a payment domain event."""


def dispatch_outbox_events(
    *,
    publisher: PaymentEventPublisher,
    session_factory: Callable[[], Session] = SessionLocal,
    batch_size: int = 100,
    max_retries: int = 5,
) -> None:
    """Dispatch pending outbox events through the provided publisher."""

    session = session_factory()
    try:
        repository = PaymentRepository(session)
        events = repository.fetch_pending_outbox(limit=batch_size)
        if not events:
            return

        for event in events:
            repository.mark_outbox_sending(event)

        session.flush()

        for event in events:
            try:
                publisher.publish(event.event_type, event.payload)
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Failed to publish payment event", extra={"event_id": event.id, "event_type": event.event_type}
                )
                repository.mark_outbox_retry(event, error=str(exc), max_retries=max_retries)
            else:
                repository.mark_outbox_sent(event)

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["dispatch_outbox_events", "PaymentEventPublisher"]

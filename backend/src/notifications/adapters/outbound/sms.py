"""SMS sender adapters.

Dev uses the console adapter (logs the message instead of sending); prod
plugs a real provider behind the same ``SmsSender`` port. Selection happens in
the notifications container via the ``SMS_PROVIDER`` env var.
"""

from __future__ import annotations

import logging

from src.notifications.domain.ports import SmsSender

logger = logging.getLogger(__name__)


class ConsoleSmsSender(SmsSender):
    """Log the SMS body instead of sending (used in dev)."""

    def send(self, *, to_phone: str, body: str) -> None:
        logger.info("[SMS to %s] %s", to_phone, body)


class ProviderSmsSender(SmsSender):
    """Provider-bound sender (Twilio-style interface).

    This is a stub for a real provider integration: it logs and does nothing
    yet. The signature stays provider-neutral so a Twilio/MessageBird/etc.
    client can be dropped in without touching the port or use cases.
    """

    def send(self, *, to_phone: str, body: str) -> None:
        logger.warning(
            "[SMS provider not configured] would send to %s: %s", to_phone, body
        )
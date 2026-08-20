"""Email sender adapter: uses Django's email backend (console in dev, SMTP in
prod via ``EMAIL_*`` settings). Sending is best-effort — failures are logged,
never raised to the queue flow.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail

from src.notifications.domain.ports import EmailSender

logger = logging.getLogger(__name__)


class DjangoEmailSender(EmailSender):
    def send(self, *, to_email: str, subject: str, body: str) -> None:
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to send notification email to %s", to_email)


def send_email(to_email: str, subject: str, body: str) -> None:
    """Module-level convenience, kept for backwards compatibility."""
    DjangoEmailSender().send(to_email=to_email, subject=subject, body=body)

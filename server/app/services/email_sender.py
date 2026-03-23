"""
Transactional email sending service.

Uses the same SMTP configuration as email_processor.py.
When EMAIL_SENDING_ENABLED is False, logs a warning and no-ops.
"""

import logging
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(recipient: str, subject: str, body: str) -> None:
    """Send a transactional email via SMTP."""
    if not settings.EMAIL_SENDING_ENABLED:
        logger.warning(
            "Email sending disabled — would have sent '%s' to %s",
            subject,
            recipient,
        )
        return

    if not settings.EMAIL_SMTP_HOST:
        logger.warning(
            "SMTP not configured — would have sent '%s' to %s",
            subject,
            recipient,
        )
        return

    try:
        import aiosmtplib

        msg = EmailMessage()
        msg["From"] = settings.EMAIL_PROCESSING_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = f"[{settings.PROJECT_NAME}] {subject}"
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=settings.EMAIL_SMTP_HOST,
            port=settings.EMAIL_SMTP_PORT,
            username=settings.EMAIL_SMTP_USER,
            password=settings.EMAIL_SMTP_PASSWORD,
            use_tls=True,
        )
        logger.info("Email sent: '%s' to %s", subject, recipient)
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipient)
        raise


async def send_password_reset_email(recipient: str, reset_token: str) -> None:
    """Send a password reset email with a link containing the token."""
    reset_url = (
        f"{settings.VERIFICATION_BASE_URL.rstrip('/')}"
        f"/reset-password?token={reset_token}"
    )
    body = (
        f"A password reset has been requested for your account.\n\n"
        f"To set a new password, visit:\n"
        f"{reset_url}\n\n"
        f"This link expires in {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.\n\n"
        f"If you did not request this, please ignore this email.\n"
    )
    await send_email(recipient, "Password Reset", body)


async def send_password_changed_notification(recipient: str) -> None:
    """Send confirmation that a password was changed."""
    body = (
        "Your password has been changed successfully.\n\n"
        "If you did not make this change, please contact the "
        "Electoral Commission immediately.\n"
    )
    await send_email(recipient, "Password Changed", body)


async def send_email_changed_notification(
    old_email: str, new_email: str
) -> None:
    """Notify both old and new email addresses of an email change."""
    old_body = (
        "The email address on your account has been changed by the "
        "Electoral Commission.\n\n"
        "If you did not expect this change, please contact the "
        "Electoral Commission.\n"
    )
    new_body = (
        "Your account email has been updated to this address by the "
        "Electoral Commission.\n\n"
        "If you did not expect this, please contact the "
        "Electoral Commission.\n"
    )
    # Send to both addresses (best-effort; don't fail if one bounces)
    try:
        await send_email(old_email, "Email Address Changed", old_body)
    except Exception:
        logger.warning("Failed to notify old email %s of email change", old_email)

    try:
        await send_email(new_email, "Email Address Updated", new_body)
    except Exception:
        logger.warning("Failed to notify new email %s of email change", new_email)

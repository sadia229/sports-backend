"""
Email service: verification codes and transactional mail.

Sending is done over SMTP and is meant to be run inside a FastAPI
BackgroundTask so the HTTP response is not blocked on the mail server.

In development (no SMTP_HOST configured) the code is logged instead of sent,
so the signup -> verify flow is testable without a real mailbox.

NOTE: verification codes are kept in an in-memory dict here for simplicity.
In production store them in Redis with a TTL (e.g. `verify:{email}` -> code,
expire 600s) so they survive across workers and expire automatically.
"""
import smtplib
import secrets
import logging
import time
from email.message import EmailMessage
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# email -> {"code": str, "expires_at": float}
_verification_codes: dict[str, dict] = {}

CODE_TTL_SECONDS = 10 * 60  # 10 minutes


def generate_verification_code(email: str) -> str:
    """Create a 6-digit code, store it with a TTL, and return it."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    _verification_codes[email.lower()] = {
        "code": code,
        "expires_at": time.time() + CODE_TTL_SECONDS,
    }
    return code


def verify_code(email: str, code: str) -> bool:
    """Check a submitted code against the stored one; consume it on success."""
    entry = _verification_codes.get(email.lower())
    if not entry:
        return False
    if time.time() > entry["expires_at"]:
        _verification_codes.pop(email.lower(), None)
        return False
    if secrets.compare_digest(entry["code"], code):
        _verification_codes.pop(email.lower(), None)  # one-time use
        return True
    return False


def _send_smtp(to_email: str, subject: str, body: str) -> None:
    """Low-level SMTP send. Raises on failure (caught by the caller)."""
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_verification_email(to_email: str, code: str) -> None:
    """
    Send the verification code. Designed to be passed to BackgroundTasks.

    Never raises out to the request: a mail failure must not 500 a signup that
    already succeeded — the user can request a resend.
    """
    subject = "Your AI Match Predictor verification code"
    body = (
        f"Welcome to AI Match Predictor!\n\n"
        f"Your verification code is: {code}\n\n"
        f"It expires in 10 minutes. If you didn't sign up, ignore this email."
    )

    if not settings.SMTP_HOST:
        # Dev mode: no SMTP configured. Log the code so the flow is testable.
        logger.info("[email:dev] verification code for %s = %s", to_email, code)
        return

    try:
        _send_smtp(to_email, subject, body)
        logger.info("[email] verification code sent to %s", to_email)
    except Exception as exc:  # noqa: BLE001 - background task must not crash
        logger.error("[email] failed to send to %s: %s", to_email, exc)

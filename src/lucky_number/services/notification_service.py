"""Notification service for email and WhatsApp delivery.

Abstrai o envio de notificações transacionais: reset de senha,
códigos de ativação, alertas. Suporta email (SMTP/Resend) e
WhatsApp (Twilio API).
"""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Raised when notification delivery fails."""


@dataclass
class EmailConfig:
    host: str = os.getenv("SMTP_HOST", "localhost")
    port: int = int(os.getenv("SMTP_PORT", "587"))
    user: str = os.getenv("SMTP_USER", "")
    password: str = os.getenv("SMTP_PASS", "")
    use_tls: bool = True
    from_email: str = os.getenv("EMAIL_FROM", "noreply@luckynumber.app")
    from_name: str = os.getenv("EMAIL_FROM_NAME", "Lucky Number")


@dataclass
class WhatsAppConfig:
    account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number: str = os.getenv("TWILIO_WHATSAPP_FROM", "")


class EmailChannel:
    """Sends transactional emails via SMTP.

    Prevents CWE-522: credentials loaded from env vars, never hardcoded.
    Prevents CWE-200: no sensitive data in logs.
    """

    def __init__(self, config: EmailConfig | None = None) -> None:
        self.config = config or EmailConfig()

    async def send(self, to: str, subject: str, body_html: str) -> bool:
        """Send an HTML email. Returns True on success, False on failure."""
        if not self.config.user or not self.config.password:
            logger.warning(
                "Email not configured — skipping send to %s", _mask_email(to)
            )
            return False
        try:
            import aiosmtplib

            message = _build_email_message(
                self.config.from_email, self.config.from_name, to, subject, body_html
            )
            await aiosmtplib.send(
                message,
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.user,
                password=self.config.password,
                use_tls=self.config.use_tls,
            )
            logger.info("Email sent to %s — subject=%s", _mask_email(to), subject)
            return True
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", _mask_email(to), exc)
            return False


class WhatsAppChannel:
    """Sends WhatsApp messages via Twilio API.

    Prevents CWE-522: credentials from env vars.
    Prevents CWE-200: phone masked in logs.
    """

    def __init__(self, config: WhatsAppConfig | None = None) -> None:
        self.config = config or WhatsAppConfig()

    async def send(self, to: str, message: str) -> bool:
        """Send a WhatsApp message. Returns True on success, False on failure."""
        if not self.config.account_sid or not self.config.auth_token:
            logger.warning(
                "Twilio not configured — skipping WhatsApp to %s", _mask_phone(to)
            )
            return False
        try:
            from twilio.rest import Client

            client = Client(self.config.account_sid, self.config.auth_token)
            await _async_twilio_message(client, to, self.config.from_number, message)
            logger.info("WhatsApp sent to %s", _mask_phone(to))
            return True
        except Exception as exc:
            logger.error("Failed to send WhatsApp to %s: %s", _mask_phone(to), exc)
            return False


class NotificationService:
    """High-level notification service used by auth/reset flows.

    Usage:
        ns = NotificationService()
        await ns.send_reset_link(user, "email", "https://...")
    """

    def __init__(
        self,
        email_channel: EmailChannel | None = None,
        whatsapp_channel: WhatsAppChannel | None = None,
    ) -> None:
        self.email = email_channel or EmailChannel()
        self.whatsapp = whatsapp_channel or WhatsAppChannel()

    async def send_reset_link(self, to: str, channel: str, link: str) -> bool:
        """Send a password reset link via the specified channel."""
        if channel == "email":
            subject = "Redefinição de senha — Lucky Number"
            body_html = _reset_email_html(link)
            return await self.email.send(to, subject, body_html)
        elif channel == "whatsapp":
            message = _reset_whatsapp_text(link)
            return await self.whatsapp.send(to, message)
        else:
            logger.error("Unknown delivery channel: %s", channel)
            return False

    async def send_activation_code(self, to: str, channel: str, code: str) -> bool:
        """Send an activation code via the specified channel."""
        if channel == "email":
            subject = "Código de ativação — Lucky Number"
            body_html = _activation_email_html(code)
            return await self.email.send(to, subject, body_html)
        elif channel == "whatsapp":
            message = _activation_whatsapp_text(code)
            return await self.whatsapp.send(to, message)
        else:
            logger.error("Unknown delivery channel: %s", channel)
            return False


# ─── Private helpers ───────────────────────────────────────────────────


def _mask_email(email: str) -> str:
    """Mask email for logging: j***@example.com. Prevents CWE-200."""
    local, at, domain = email.partition("@")
    return local[0] + "***" + at + domain if local else email


def _mask_phone(phone: str) -> str:
    """Mask phone for logging: +55***9999. Prevents CWE-200."""
    return phone[:3] + "***" + phone[-4:] if len(phone) > 7 else "***"


def _build_email_message(
    from_email: str, from_name: str, to: str, subject: str, body_html: str
):
    """Build an email Message object."""
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))
    return msg


def _reset_email_html(link: str) -> str:
    """HTML email template for password reset."""
    return f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;padding:24px">
<h2>Redefinição de senha</h2>
<p>Você solicitou a redefinição da sua senha no <strong>Lucky Number</strong>.</p>
<p>Clique no botão abaixo para criar uma nova senha. Este link expira em 20 minutos.</p>
<p style="text-align:center;margin:32px 0">
  <a href="{link}" style="background:#4F46E5;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-size:16px">  # noqa: E501
    Redefinir senha
  </a>
</p>
<p>Se você não solicitou esta redefinição, ignore este email.</p>
<hr><small>Lucky Number — Gerador de Combinações</small>
</body></html>"""


def _reset_whatsapp_text(link: str) -> str:
    """WhatsApp message template for password reset."""
    return (
        "🔐 *Lucky Number — Redefinição de Senha*\n\n"
        "Você solicitou a redefinição da sua senha.\n\n"
        f"Clique no link para criar uma nova senha (válido por 20 minutos):\n{link}\n\n"
        "Se você não solicitou, ignore esta mensagem."
    )


def _activation_email_html(code: str) -> str:
    """HTML email template for account activation code."""
    return f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;padding:24px">
<h2>Ativação de conta</h2>
<p>Seu código de ativação do <strong>Lucky Number</strong> é:</p>
<p style="font-size:32px;letter-spacing:8px;text-align:center;font-weight:bold;margin:24px 0">{code}</p>  # noqa: E501
<p>Este código expira em 24 horas.</p>
<hr><small>Lucky Number — Gerador de Combinações</small>
</body></html>"""


def _activation_whatsapp_text(code: str) -> str:
    """WhatsApp message template for activation code."""
    return (
        "✅ *Lucky Number — Ativação de Conta*\n\n"
        f"Seu código de ativação é: *{code}*\n\n"
        "Este código expira em 24 horas."
    )


async def _async_twilio_message(client, to: str, from_number: str, body: str) -> None:
    """Send Twilio WhatsApp message asynchronously using run_in_executor."""
    import asyncio
    from twilio.base.exceptions import TwilioRestException

    def _sync_send():
        return client.messages.create(
            body=body,
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{to}",
        )

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _sync_send)
    except TwilioRestException as exc:
        raise NotificationError(f"Twilio error: {exc}") from exc

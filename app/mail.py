import os
import smtplib
import ssl
from email.message import EmailMessage


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Users App")
    use_tls = _get_bool_env("SMTP_USE_TLS", True)
    use_ssl = _get_bool_env("SMTP_USE_SSL", False)

    if not smtp_host:
        raise RuntimeError("SMTP_HOST is not configured")
    if not smtp_from_email:
        raise RuntimeError("SMTP_FROM_EMAIL is not configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{smtp_from_name} <{smtp_from_email}>"
    message["To"] = to_email
    message.set_content(text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
        return

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_tls:
            context = ssl.create_default_context()
            server.starttls(context=context)
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        server.send_message(message)


def send_password_reset_email(to_email: str, reset_link: str):
    subject = "Reset hasła - Users App"

    text_body = f"""Cześć,

otrzymaliśmy prośbę o reset hasła do Twojego konta.

Kliknij w link poniżej, aby ustawić nowe hasło:
{reset_link}

Jeśli to nie Ty wysłałeś tę prośbę, zignoruj tę wiadomość.

Link wygasa po 30 minutach.
"""

    html_body = f"""
    <html>
      <body>
        <p>Cześć,</p>
        <p>otrzymaliśmy prośbę o reset hasła do Twojego konta.</p>
        <p>
          <a href="{reset_link}">Kliknij tutaj, aby ustawić nowe hasło</a>
        </p>
        <p>Jeśli to nie Ty wysłałeś tę prośbę, zignoruj tę wiadomość.</p>
        <p>Link wygasa po 30 minutach.</p>
      </body>
    </html>
    """

    send_email(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
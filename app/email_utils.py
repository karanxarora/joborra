import os
import smtplib
from email.message import EmailMessage
from typing import Optional

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
SMTP_FROM = os.getenv('SMTP_FROM') or SMTP_USER
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes')


def send_email(to_email: str, subject: str, body: str, html: Optional[str] = None) -> bool:
    """
    Send an email using basic SMTP settings from environment variables.
    Returns True if the email was accepted by the SMTP server, False otherwise.
    """
    if not (SMTP_HOST and SMTP_FROM and (SMTP_PASS or not SMTP_USER)):
        # Not configured; no-op
        return False

    msg = EmailMessage()
    msg['From'] = SMTP_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASS or '')
            resp = server.send_message(msg)
            # send_message returns a dict of {recipient: error} for failures
            return not bool(resp)
    except Exception:
        return False

import os
import smtplib
from email.message import EmailMessage
from typing import Optional
import logging
import requests

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
SMTP_FROM = os.getenv('SMTP_FROM') or SMTP_USER
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes')
SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() in ('1', 'true', 'yes')

# HTTP email providers (preferred in restricted outbound environments)
EMAIL_PROVIDER = (os.getenv('EMAIL_PROVIDER') or '').lower()  # '', 'mailgun', 'sendgrid', 'resend'

# Mailgun
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')  # e.g., mg.example.com
MAILGUN_BASE_URL = os.getenv('MAILGUN_BASE_URL', 'https://api.mailgun.net')

# SendGrid
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Resend
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str, html: Optional[str] = None) -> bool:
    """
    Send an email via configured provider.
    Preferred: HTTP provider (Mailgun/SendGrid) when configured. Fallback: SMTP.
    Returns True if the email was accepted, False otherwise.
    """
    # Try HTTP providers first
    if EMAIL_PROVIDER == 'mailgun' and MAILGUN_API_KEY and MAILGUN_DOMAIN and SMTP_FROM:
        return _send_via_mailgun(to_email, subject, body, html)
    if EMAIL_PROVIDER == 'sendgrid' and SENDGRID_API_KEY and SMTP_FROM:
        return _send_via_sendgrid(to_email, subject, body, html)
    if EMAIL_PROVIDER == 'resend' and RESEND_API_KEY and SMTP_FROM:
        return _send_via_resend(to_email, subject, body, html)

    # Fallback to SMTP if configured
    if not (SMTP_HOST and SMTP_FROM and (SMTP_PASS or not SMTP_USER)):
        logger.warning("Email not configured: set EMAIL_PROVIDER + API keys, or SMTP_* env vars")
        return False

    msg = EmailMessage()
    msg['From'] = SMTP_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype='html')

    try:
        if SMTP_USE_SSL:
            server_cls = smtplib.SMTP_SSL
        else:
            server_cls = smtplib.SMTP

        with server_cls(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASS or '')
            resp = server.send_message(msg)
            # send_message returns a dict of {recipient: error} for failures
            ok = not bool(resp)
            if not ok:
                logger.error(f"SMTP send_message returned failures: {resp}")
            return ok
    except Exception as e:
        logger.exception(f"SMTP send failed: {e}")
        return False


def _send_via_mailgun(to_email: str, subject: str, body: str, html: Optional[str]) -> bool:
    try:
        url = f"{MAILGUN_BASE_URL}/v3/{MAILGUN_DOMAIN}/messages"
        data = {
            'from': SMTP_FROM,
            'to': to_email,
            'subject': subject,
            'text': body,
        }
        if html:
            data['html'] = html
        resp = requests.post(url, auth=('api', MAILGUN_API_KEY), data=data, timeout=30)
        if 200 <= resp.status_code < 300:
            return True
        logger.error(f"Mailgun API error {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        logger.exception(f"Mailgun send failed: {e}")
        return False


def _send_via_sendgrid(to_email: str, subject: str, body: str, html: Optional[str]) -> bool:
    try:
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            'Authorization': f'Bearer {SENDGRID_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'personalizations': [{ 'to': [{ 'email': to_email }] }],
            'from': { 'email': SMTP_FROM.split('<')[-1].rstrip('> ').strip() if '<' in SMTP_FROM else SMTP_FROM },
            'subject': subject,
            'content': [
                { 'type': 'text/plain', 'value': body }
            ]
        }
        if html:
            payload['content'].append({ 'type': 'text/html', 'value': html })
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if 200 <= resp.status_code < 300:
            return True
        logger.error(f"SendGrid API error {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        logger.exception(f"SendGrid send failed: {e}")
        return False


def _send_via_resend(to_email: str, subject: str, body: str, html: Optional[str]) -> bool:
    """Send email via Resend HTTP API."""
    try:
        url = "https://api.resend.com/emails"
        headers = {
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'from': SMTP_FROM,
            'to': [to_email],
            'subject': subject,
            'text': body,
        }
        if html:
            payload['html'] = html
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if 200 <= resp.status_code < 300:
            return True
        logger.error(f"Resend API error {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        logger.exception(f"Resend send failed: {e}")
        return False

# echopage/email_notifier.py
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from echopage.logger import setup_logger

load_dotenv()
logger = setup_logger()

# Load email settings from .env
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")   # comma‑separated list OK
LOG_PATH   = os.getenv("LOG_PATH", "logs/echopage.log")

def _read_log_excerpt(n_lines: int = 50) -> str:
    """Read the last n_lines from the log file."""
    try:
        log_file = Path(LOG_PATH)
        lines = log_file.read_text(encoding="utf-8").splitlines()
        excerpt = "\n".join(lines[-n_lines:])
        return excerpt
    except Exception as e:
        logger.error(f"Could not read log file: {e}")
        return ""

def send_notification(status: str, details: str = ""):
    """
    Send an email to dev address with a summary and log excerpt.
    
    Args:
        status: "SUCCESS", "FAILURE", or "TIMEOUT"
        details: optional extra context or exception message
    """
    subject = f"EchoPage Run: {status}"
    body = f"""\
EchoPage process has completed with status: {status}

Details:
{details}

Last log excerpt:
{_read_log_excerpt(50)}
"""
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = [addr.strip() for addr in EMAIL_TO.split(",")]
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        logger.info(f"Notification email sent: {status}")
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")

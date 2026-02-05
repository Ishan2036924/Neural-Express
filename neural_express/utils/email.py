"""Email delivery for Neural Express newsletters."""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

from .logging import get_logger

logger = get_logger("email")


def send_newsletter_email(
    to_email: str,
    subject: str,
    body_text: str,
    pdf_path: str | None = None,
) -> bool:
    """
    Send newsletter email with optional PDF attachment.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        body_text: Plain text email body (newsletter markdown)
        pdf_path: Path to PDF file to attach (optional)

    Returns:
        True if email sent successfully, False otherwise
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_host = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))

    if not sender_email or not sender_password:
        logger.error("EMAIL_SENDER and EMAIL_PASSWORD must be set in environment")
        return False

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body_text, "plain"))

    # Attach PDF if provided
    if pdf_path:
        pdf_file = Path(pdf_path)
        if pdf_file.exists():
            with open(pdf_file, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=pdf_file.name,
                )
                msg.attach(attachment)
            logger.info(f"Attached PDF: {pdf_file.name}")
        else:
            logger.warning(f"PDF not found, sending without attachment: {pdf_path}")

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        logger.info(f"Newsletter email sent to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check EMAIL_SENDER and EMAIL_PASSWORD.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False

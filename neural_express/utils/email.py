"""Email delivery for Neural Express newsletters."""

import re
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

from .logging import get_logger

logger = get_logger("email")


def _markdown_to_html(markdown_text: str) -> str:
    """
    Convert newsletter markdown to styled HTML email.

    Args:
        markdown_text: Raw markdown newsletter content

    Returns:
        Fully styled HTML string
    """
    html = markdown_text

    # Escape HTML entities (but preserve markdown syntax)
    html = html.replace("&", "&amp;")

    # Horizontal rules
    html = re.sub(r'^---+\s*$', '<hr style="border:none;border-top:2px solid #e0e0e0;margin:24px 0;">', html, flags=re.MULTILINE)

    # Headers
    html = re.sub(
        r'^### (.+)$',
        r'<h3 style="color:#2c3e50;font-size:16px;font-weight:700;margin:20px 0 10px 0;font-family:Arial,Helvetica,sans-serif;">\1</h3>',
        html, flags=re.MULTILINE
    )
    html = re.sub(
        r'^## (.+)$',
        r'<h2 style="color:#1a1a2e;font-size:20px;font-weight:700;margin:24px 0 12px 0;border-bottom:2px solid #3498db;padding-bottom:6px;font-family:Arial,Helvetica,sans-serif;">\1</h2>',
        html, flags=re.MULTILINE
    )
    html = re.sub(
        r'^# (.+)$',
        r'<h1 style="color:#1a1a2e;font-size:28px;font-weight:800;margin:0 0 8px 0;text-align:center;font-family:Arial,Helvetica,sans-serif;">\1</h1>',
        html, flags=re.MULTILINE
    )

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em style="color:#666;">\1</em>', html)

    # Links: [text](url)
    html = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" style="color:#3498db;text-decoration:none;">\1</a>',
        html
    )

    # Bullet list items
    # Collect consecutive bullet lines into <ul> blocks
    lines = html.split('\n')
    result_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- '):
            if not in_list:
                result_lines.append('<ul style="margin:8px 0;padding-left:20px;">')
                in_list = True
            content = stripped[2:]
            result_lines.append(f'<li style="margin:4px 0;color:#333;line-height:1.6;">{content}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            # Numbered list items
            num_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
            if num_match:
                result_lines.append(
                    f'<p style="margin:4px 0 4px 16px;color:#333;line-height:1.6;">'
                    f'<strong>{num_match.group(1)}.</strong> {num_match.group(2)}</p>'
                )
            elif stripped:
                result_lines.append(f'<p style="margin:6px 0;color:#333;line-height:1.6;font-family:Arial,Helvetica,sans-serif;">{stripped}</p>')
            else:
                result_lines.append('')

    if in_list:
        result_lines.append('</ul>')

    body_content = '\n'.join(result_lines)

    # Wrap in full HTML document with inline styles
    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Neural Express Newsletter</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f8;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f8;">
<tr><td align="center" style="padding:20px 10px;">
<table role="presentation" width="640" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

<!-- Header Banner -->
<tr><td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:30px 40px;text-align:center;">
<h1 style="color:#ffffff;font-size:28px;font-weight:800;margin:0;letter-spacing:2px;font-family:Arial,Helvetica,sans-serif;">NEURAL EXPRESS</h1>
<p style="color:#a0c4ff;font-size:14px;margin:8px 0 0 0;font-family:Arial,Helvetica,sans-serif;">Your AI news briefing curated by intelligent agents</p>
</td></tr>

<!-- Content -->
<tr><td style="padding:30px 40px;font-size:14px;color:#333333;line-height:1.7;">
{body_content}
</td></tr>

<!-- Footer -->
<tr><td style="background-color:#f8f9fa;padding:20px 40px;text-align:center;border-top:2px solid #e0e0e0;">
<p style="color:#888;font-size:12px;margin:0;font-family:Arial,Helvetica,sans-serif;">
&copy; 2026 Neural Express. All rights reserved.<br>
Reply to this email with feedback or questions.
</p>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    return styled_html


def send_newsletter_email(
    to_email: str,
    subject: str,
    body_text: str,
    pdf_path: str | None = None,
) -> bool:
    """
    Send newsletter email as formatted HTML with optional PDF attachment.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        body_text: Newsletter markdown content (will be converted to HTML)
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

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach plain text fallback (strip markdown syntax for readability)
    plain_text = body_text.replace("**", "").replace("##", "").replace("# ", "")
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))

    # Attach HTML version (primary)
    html_body = _markdown_to_html(body_text)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

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

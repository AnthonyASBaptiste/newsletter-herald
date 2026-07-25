import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

def mask_email(email: str) -> str:
    """
    Masks an email address to prevent PII exposure in logs.
    Example: user@example.com -> u**r@example.com
             ab@example.com -> a*@example.com
             a@example.com -> *@example.com
    """
    if not email or "@" not in email:
        return email
    try:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        elif len(local) == 2:
            masked_local = local[0] + "*"
        else:
            masked_local = "*"
        return f"{masked_local}@{domain}"
    except Exception:
        return "masked_email"

def send_newsletter_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using Gmail SMTP (Primary) or SendGrid (Fallback).
    """
    masked_to = mask_email(to_email)

    # 1. Try Gmail SMTP first if configured
    if settings.gmail_user and settings.gmail_app_password:
        try:
            logger.info(f"Attempting to send email via Gmail SMTP to {masked_to}")
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.gmail_user
            msg["To"] = to_email
            
            # Attach html content
            part = MIMEText(html_content, "html")
            msg.attach(part)
            
            # Connect to Gmail SMTP server
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings.gmail_user, settings.gmail_app_password)
                server.sendmail(settings.gmail_user, to_email, msg.as_string())
                
            logger.info(f"Email sent successfully via Gmail SMTP to {masked_to}")
            return True
        except Exception as smtp_err:
            logger.error(f"Gmail SMTP failed: {smtp_err}. Falling back if possible.")

    # 2. Fallback to SendGrid
    if settings.sendgrid_api_key and settings.from_email:
        try:
            logger.info(f"Attempting to send email via SendGrid to {masked_to}")
            message = Mail(
                from_email=Email(settings.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            sg = SendGridAPIClient(settings.sendgrid_api_key)
            response = sg.send(message)
            logger.info(f"Email sent successfully via SendGrid to {masked_to}. Status code: {response.status_code}")
            return True
        except Exception as sg_err:
            logger.error(f"SendGrid failed: {sg_err}")
            return False

    logger.error("No valid email configuration (Gmail or SendGrid) available.")
    return False

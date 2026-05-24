import sys
import os
import asyncio

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.email import send_newsletter_email
from config import get_settings

def main():
    settings = get_settings()
    
    print("Starting email test script...")
    
    if settings.gmail_user and settings.gmail_app_password:
        print(f"Gmail SMTP Configured (User: {settings.gmail_user})")
        recipient = settings.gmail_user
    elif settings.from_email:
        print(f"SendGrid Configured (From: {settings.from_email})")
        recipient = settings.from_email
    else:
        print("Error: No email configurations found in settings/.env!")
        return
        
    print(f"Sending test email to: {recipient}...")
    
    subject = "Newsletter Herald SMTP Test Connection"
    html_content = """
    <h2>SMTP Test Connection Successful</h2>
    <p>This is a test email sent from the <strong>Newsletter Herald Backend</strong>.</p>
    <p>If you received this email, your SMTP configurations are working perfectly!</p>
    <hr>
    <p><small>Sent by Newsletter Herald Automated Test</small></p>
    """
    
    success = send_newsletter_email(recipient, subject, html_content)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Please check your credentials and logs.")

if __name__ == "__main__":
    main()

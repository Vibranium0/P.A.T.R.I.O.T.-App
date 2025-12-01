import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

# Set up logging
logger = logging.getLogger(__name__)

def send_verification_email(email, token):
    """
    Send verification email to user.
    In development: logs to console
    In production: sends via SMTP
    """
    config = current_app.config
    
    # Email content
    subject = f"Verify your {config['APP_NAME']} account"
    # Link to backend API for email verification
    verification_link = f"http://127.0.0.1:5001/api/auth/verify-email?token={token}"
    
    # Email body
    html_body = f"""
    <html>
      <body>
        <h2>Welcome to {config['APP_NAME']}!</h2>
        <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_link}">Verify Your Email</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{verification_link}</p>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't create this account, you can safely ignore this email.</p>
      </body>
    </html>
    """
    
    text_body = f"""
    Welcome to {config['APP_NAME']}!
    
    Thank you for registering. Please verify your email address by visiting this link:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create this account, you can safely ignore this email.
    """
    
    # Development mode: log to console (unless MAIL_USERNAME is configured)
    if config.get('ENV') == 'development' and not config.get('MAIL_USERNAME'):
        print("\n" + "="*60)
        print("📧 DEVELOPMENT EMAIL SERVICE")
        print("="*60)
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"Verification Token: {token}")
        print(f"Verification Link: {verification_link}")
        print("-" * 60)
        print("EMAIL BODY (TEXT):")
        print(text_body)
        print("="*60 + "\n")
        return True
    
    # Production mode: send via SMTP
    try:
        return _send_smtp_email(email, subject, text_body, html_body)
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        # In production, we might want to queue for retry or use a different service
        return False

def _send_smtp_email(to_email, subject, text_body, html_body):
    """Send email via SMTP"""
    config = current_app.config
    
    # Check if SMTP is configured
    if not all([config.get('MAIL_SERVER'), config.get('MAIL_USERNAME'), config.get('MAIL_PASSWORD')]):
        logger.warning("SMTP not configured. Email not sent.")
        print(f"⚠️  SMTP not configured. Would send email to: {to_email}")
        print(f"   Subject: {subject}")
        return False
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = config['MAIL_DEFAULT_SENDER']
    message["To"] = to_email
    
    # Add text and HTML parts
    text_part = MIMEText(text_body, "plain")
    html_part = MIMEText(html_body, "html")
    message.attach(text_part)
    message.attach(html_part)
    
    # Send email
    try:
        # Create secure SSL context
        context = ssl.create_default_context()
        
        # Connect to server and send email
        with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
            if config.get('MAIL_USE_TLS'):
                server.starttls(context=context)
            
            server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
            server.sendmail(config['MAIL_DEFAULT_SENDER'], to_email, message.as_string())
            
        logger.info(f"Verification email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
        raise


def send_password_reset_email(email, token):
    """
    Send password reset email to user.
    In development: logs to console
    In production: sends via SMTP
    """
    config = current_app.config
    
    # Email content
    subject = f"Reset your {config['APP_NAME']} password"
    # Link to frontend password reset page
    reset_link = f"{config['APP_URL']}/reset-password?token={token}"
    
    # Email body
    html_body = f"""
    <html>
      <body>
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password for {config['APP_NAME']}.</p>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_link}">Reset Your Password</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{reset_link}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this password reset, you can safely ignore this email.</p>
      </body>
    </html>
    """
    
    text_body = f"""
    Password Reset Request
    
    You requested to reset your password for {config['APP_NAME']}.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this password reset, you can safely ignore this email.
    """
    
    # Development mode: log to console
    if config.get('ENV') == 'development' and not config.get('MAIL_USERNAME'):
        print("\n" + "="*60)
        print("🔐 PASSWORD RESET EMAIL (DEVELOPMENT)")
        print("="*60)
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"Reset Token: {token}")
        print(f"Reset Link: {reset_link}")
        print("-" * 60)
        print("EMAIL BODY (TEXT):")
        print(text_body)
        print("="*60 + "\n")
        return True
    
    # Production mode: send via SMTP
    try:
        return _send_smtp_email(email, subject, text_body, html_body)
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False

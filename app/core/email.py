import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from app.core.config import settings
import logging
import asyncio
from functools import partial
import aiosmtplib
import os

logger = logging.getLogger(__name__)

def create_verification_email(to_email: str, token: str) -> MIMEMultipart:
    """Create a verification email."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Welcome to Jesi AI - Verify Your Email'
    msg['From'] = to_email
    msg['To'] = to_email

    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    max-width: 150px;
                    height: auto;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #FF7900;
                    color: #ffffff;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eeeeee;
                    font-size: 12px;
                    color: #666666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="cid:logo" alt="Jesi AI Logo" class="logo">
                    <h2>Welcome to Jesi AI!</h2>
                </div>
                
                <p>Thank you for creating an account with Jesi AI. To get started, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666666;">{verification_url}</p>
                
                <p>If you did not create an account with Jesi AI, please ignore this email.</p>
                
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; Jesi AI {settings.VERSION}</p>
                </div>
            </div>
        </body>
        </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    return msg

def send_email_sync(msg: MIMEMultipart) -> None:
    """Send email synchronously."""
    try:
        logger.info(f"Attempting to connect to SMTP server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        logger.info(f"Using SMTP user: {settings.SMTP_USER}")
        
        # Create SMTP connection
        logger.info("Creating SMTP connection...")
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.set_debuglevel(1)  # Enable debug output
        
        # Set ESMTP features for MailMug
        server.esmtp_features["auth"] = "LOGIN DIGEST-MD5 PLAIN"
        
        # Only attempt STARTTLS if explicitly enabled
        if settings.SMTP_TLS:
            try:
                logger.info("Attempting to enable STARTTLS...")
                context = ssl.create_default_context()
                server.starttls(context=context)
                logger.info("STARTTLS enabled successfully")
            except smtplib.SMTPNotSupportedError:
                logger.warning("STARTTLS not supported by server, continuing without encryption")
        
        # Login to SMTP server
        logger.info("Logging in to SMTP server...")
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        # Send email
        logger.info("Sending email...")
        server.send_message(msg)
        logger.info("Email sent successfully")
        
        # Close connection
        logger.info("Closing SMTP connection...")
        server.quit()
            
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise

async def send_verification_email(to_email: str, token: str) -> None:
    """Send verification email asynchronously."""
    try:
        msg = create_verification_email(to_email, token)
        # Attach logo
        with open('app/logo.png', 'rb') as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo>')
            msg.attach(logo)

        # Run the synchronous email sending in a thread pool
        await asyncio.get_event_loop().run_in_executor(
            None, 
            partial(send_email_sync, msg)
        )
        logger.info(f"Verification email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        raise

def create_password_reset_email(to_email: str, token: str) -> MIMEMultipart:
    """Create a password reset email."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Reset Your Jesi AI Password'
    msg['From'] = to_email
    msg['To'] = to_email

    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
    
    html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    max-width: 150px;
                    height: auto;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #FF7900;
                    color: #ffffff;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeeba;
                    color: #856404;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eeeeee;
                    font-size: 12px;
                    color: #666666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="cid:logo" alt="Jesi AI Logo" class="logo">
                    <h2>Password Reset Request</h2>
                </div>
                
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666666;">{reset_url}</p>
                
                <div class="warning">
                    <strong>Important:</strong> This link will expire in 1 hour for security reasons.
                </div>
                
                <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
                
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; Jesi AI {settings.VERSION}</p>
                </div>
            </div>
        </body>
        </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    return msg

async def send_password_reset_email(to_email: str, token: str) -> None:
    """Send password reset email asynchronously."""
    try:
        msg = create_password_reset_email(to_email, token)
        # Attach logo
        with open('app/logo.png', 'rb') as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo>')
            msg.attach(logo)

        # Run the synchronous email sending in a thread pool
        await asyncio.get_event_loop().run_in_executor(
            None, 
            partial(send_email_sync, msg)
        )
        logger.info(f"Password reset email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        raise 
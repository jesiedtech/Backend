import asyncio
import aiosmtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_smtp_connection():
    try:
        logger.info(f"Testing SMTP connection to {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        logger.info(f"Using SMTP User: {settings.SMTP_USER}")
        
        # Create test message
        message = MIMEMultipart()
        message["From"] = settings.SMTP_USER
        message["To"] = settings.SMTP_USER  # Send to self for testing
        message["Subject"] = "SMTP Test Email"
        
        body = """
        This is a test email to verify SMTP configuration.
        
        If you receive this email, your SMTP settings are working correctly!
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to SMTP server
        logger.info("Attempting to connect to SMTP server...")
        smtp = aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            use_tls=False,  # We'll use STARTTLS instead
            tls_context=context
        )
        
        # Connect and login
        logger.info("Connecting to SMTP server...")
        await smtp.connect()
        logger.info("Connected successfully!")
        
        logger.info("Starting TLS...")
        await smtp.starttls()
        logger.info("TLS started successfully!")
        
        logger.info("Attempting to login...")
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        logger.info("Login successful!")
        
        # Send test email
        logger.info("Sending test email...")
        await smtp.send_message(message)
        logger.info("Test email sent successfully!")
        
        # Close connection
        await smtp.quit()
        logger.info("SMTP connection closed successfully")
        
    except Exception as e:
        logger.error(f"SMTP test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_smtp_connection()) 
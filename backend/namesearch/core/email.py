"""Email sending utilities."""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union

from fastapi import BackgroundTasks
from pydantic import EmailStr

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)


def send_email(
    email_to: EmailStr,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> None:
    """
    Send an email.
    
    Args:
        email_to: Recipient email address.
        subject: Email subject.
        html_content: HTML content of the email.
        text_content: Plain text content of the email (optional).
        
    Raises:
        RuntimeError: If email sending is not configured.
    """
    if not settings.EMAILS_ENABLED:
        logger.warning("Email sending is disabled")
        return
    
    if not text_content:
        # Simple HTML to text conversion for basic emails
        import re
        text_content = re.sub(r'<[^>]*>', ' ', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = email_to
    
    # Attach both HTML and plain text versions
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}")
        raise


def send_email_async(
    background_tasks: BackgroundTasks,
    email_to: EmailStr,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> None:
    """
    Send an email asynchronously in the background.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance.
        email_to: Recipient email address.
        subject: Email subject.
        html_content: HTML content of the email.
        text_content: Plain text content of the email (optional).
    """
    background_tasks.add_task(
        send_email,
        email_to=email_to,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )


def send_test_email(email_to: EmailStr) -> None:
    """
    Send a test email.
    
    Args:
        email_to: Recipient email address.
    """
    subject = f"{settings.PROJECT_NAME} - Test Email"
    html_content = """
    <h1>Test Email</h1>
    <p>This is a test email from {project_name}.</p>
    """.format(project_name=settings.PROJECT_NAME)
    
    send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
    )


def send_verification_email(
    email_to: EmailStr,
    token: str,
    username: str,
    background_tasks: Optional[BackgroundTasks] = None,
) -> None:
    """
    Send an email verification email.
    
    Args:
        email_to: Recipient email address.
        token: Verification token.
        username: User's username.
        background_tasks: Optional BackgroundTasks instance for async sending.
    """
    subject = f"{settings.PROJECT_NAME} - Verify Your Email"
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    html_content = f"""
    <h1>Welcome to {project_name}!</h1>
    <p>Hello {username},</p>
    <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
    <p style="text-align: center; margin: 30px 0;">
        <a href="{verification_url}" 
           style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Verify Email
        </a>
    </p>
    <p>Or copy and paste this link into your browser:</p>
    <p><code>{verification_url}</code></p>
    <p>If you didn't create an account, you can safely ignore this email.</p>
    <p>Best regards,<br/>{project_name} Team</p>
    """.format(project_name=settings.PROJECT_NAME, verification_url=verification_url, username=username)
    
    if background_tasks:
        send_email_async(
            background_tasks=background_tasks,
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )
    else:
        send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )


def send_password_reset_email(
    email_to: EmailStr,
    token: str,
    username: str,
    background_tasks: Optional[BackgroundTasks] = None,
) -> None:
    """
    Send a password reset email.
    
    Args:
        email_to: Recipient email address.
        token: Password reset token.
        username: User's username.
        background_tasks: Optional BackgroundTasks instance for async sending.
    """
    subject = f"{settings.PROJECT_NAME} - Reset Your Password"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html_content = f"""
    <h1>Reset Your Password</h1>
    <p>Hello {username},</p>
    <p>We received a request to reset your password. Click the button below to set a new password:</p>
    <p style="text-align: center; margin: 30px 0;">
        <a href="{reset_url}" 
           style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Reset Password
        </a>
    </p>
    <p>Or copy and paste this link into your browser:</p>
    <p><code>{reset_url}</code></p>
    <p>If you didn't request a password reset, you can safely ignore this email.</p>
    <p>Best regards,<br/>{project_name} Team</p>
    """.format(project_name=settings.PROJECT_NAME, reset_url=reset_url, username=username)
    
    if background_tasks:
        send_email_async(
            background_tasks=background_tasks,
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )
    else:
        send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Email config from .env
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_TO      = os.getenv("ALERT_EMAIL_TO")

SEVERITY_EMOJI = {
    "critical": "🚨",
    "high": "⚠️",
    "medium": "🔶",
    "low": "🔷",
}

def send_alert_email(subject: str, body: str, severity: str = "medium") -> bool:
    """
    Send a security alert email.

    Args:
        subject:  Email subject line
        body:     Alert details (plain text)
        severity: one of critical / high / medium / low

    Returns:
        True if sent successfully, False otherwise
    """
    if not all([SMTP_USER, SMTP_PASSWORD, ALERT_TO]):
        logger.warning("Email not configured — set SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL_TO in .env")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"]    = SMTP_USER
        msg["To"]      = ALERT_TO
        msg["Subject"] = f"[SecOpsAI ALERT][{severity.upper()}] {subject}"

        # Email body with severity stamp
        full_body = f"Severity: {severity.upper()}\n\n{body}"
        msg.attach(MIMEText(full_body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(SMTP_USER, ALERT_TO, msg.as_string())

        logger.info(f"Alert email sent → {ALERT_TO} | severity={severity} | subject={subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check SMTP_USER and SMTP_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending alert email: {e}")
        return False


if __name__ == "__main__":
    # Quick test — run: python email_notifier.py
    result = send_alert_email(
        subject="Test alert from SecOpsAI",
        body="This is a validation test.\nIP: 1.2.3.4 | Severity: HIGH",
        severity="high"
    )
    print(f"Email sent: {result}")

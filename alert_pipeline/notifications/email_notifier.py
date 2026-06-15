"""
Email Alert Notifier
Sends formatted HTML security alert emails to the SOC team.
Uses SMTP with TLS. Credentials loaded from environment only.
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# --- Environment variables (team-standard names from Day 1 skeleton) ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", EMAIL_USER)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

SEVERITY_COLORS = {
    "critical": "#FF0000",
    "high": "#FF6600",
    "medium": "#FFCC00",
    "low": "#00AA00",
}

SEVERITY_EMOJI = {
    "critical": "🚨",
    "high": "⚠️",
    "medium": "🔶",
    "low": "🔷",
}


def build_html_email(alert: dict) -> str:
    """
    Build a formatted HTML email body for a security alert.
    Includes alert details and threat intelligence enrichment
    (VirusTotal + Shodan) in separate sections.
    """
    severity = alert.get("severity", "medium")
    color = SEVERITY_COLORS.get(severity, "#FFCC00")
    emoji = SEVERITY_EMOJI.get(severity, "⚠️")

    alert_id = alert.get("alert_id", "N/A")
    threat_class = alert.get("threat_class", "Unknown Threat")
    src_ip = alert.get("src_ip", "Unknown")
    threat_score = alert.get("threat_score", 0.0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    enrichment = alert.get("enrichment", {})
    vt = enrichment.get("virustotal", {})
    shodan = enrichment.get("shodan", {})

    vt_malicious = vt.get("malicious", "N/A")
    vt_country = vt.get("country", "Unknown")

    sh_country = shodan.get("country", "Unknown")
    sh_org = shodan.get("org", "Unknown")
    sh_ports = shodan.get("open_ports", [])
    sh_vulns = shodan.get("vulns", [])

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto;">

      <div style="background-color: {color}; padding: 20px; border-radius: 8px 8px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 22px;">
          {emoji} SecOpsAI Security Alert — {severity.upper()}
        </h1>
      </div>

      <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">

        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 200px;">Alert ID</td>
            <td style="padding: 8px; border: 1px solid #ddd; font-family: monospace;">{alert_id}</td>
          </tr>
          <tr style="background-color: #ffffff;">
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Timestamp</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{timestamp}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Threat Type</td>
            <td style="padding: 8px; border: 1px solid #ddd; color: {color}; font-weight: bold;">{threat_class}</td>
          </tr>
          <tr style="background-color: #ffffff;">
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Threat Score</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{threat_score:.1%}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Source IP</td>
            <td style="padding: 8px; border: 1px solid #ddd; font-family: monospace;">{src_ip}</td>
          </tr>
        </table>

        <hr style="margin: 20px 0; border: none; border-top: 1px solid #dee2e6;">

        <h3 style="color: #333;">Threat Intelligence Enrichment</h3>

        <table style="width: 100%; border-collapse: collapse;">
          <tr style="background-color: #e9ecef;">
            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Source</th>
            <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Finding</th>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">VirusTotal</td>
            <td style="padding: 8px; border: 1px solid #ddd;">
              {vt_malicious} malicious detections | Country: {vt_country}
            </td>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Shodan</td>
            <td style="padding: 8px; border: 1px solid #ddd;">
              Org: {sh_org} | Country: {sh_country}<br>
              Open ports: {sh_ports}<br>
              Known CVEs: {sh_vulns if sh_vulns else 'None found'}
            </td>
          </tr>
        </table>

        <hr style="margin: 20px 0; border: none; border-top: 1px solid #dee2e6;">

        <p style="color: #666; font-size: 12px; margin: 0;">
          SecOpsAI Detection Platform — DefenseGrid Team — Expadox Lab
        </p>

      </div>

    </body>
    </html>
    """
    return html


def send_alert_email(alert: dict) -> bool:
    """
    Send a formatted HTML security alert email to the SOC team.
    Returns True if sent successfully, False if failed.
    """
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.warning("EMAIL_USER or EMAIL_PASSWORD not set — skipping email notification")
        return False

    severity = alert.get("severity", "medium")
    threat_class = alert.get("threat_class", "Unknown Threat")
    src_ip = alert.get("src_ip", "Unknown")
    emoji = SEVERITY_EMOJI.get(severity, "⚠️")

    subject = f"{emoji} SecOpsAI Alert [{severity.upper()}] — {threat_class} from {src_ip}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_RECIPIENT
    msg.attach(MIMEText(build_html_email(alert), "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_RECIPIENT, msg.as_string())

        logger.info(f"Email alert sent: {threat_class} from {src_ip} [{severity}] -> {EMAIL_RECIPIENT}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Email authentication failed — check EMAIL_USER and EMAIL_PASSWORD in .env")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Email notification failed: {e}")
        return False

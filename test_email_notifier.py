"""
Test script for the email notifier.
Run with: python3 test_email_notifier.py

Make sure EMAIL_USER, EMAIL_PASSWORD, and EMAIL_RECIPIENT
are set in your .env file before running.
"""

import sys

sys.path.insert(0, ".")

from alert_pipeline.notifications.email_notifier import send_alert_email

test_alert = {
    "alert_id": "TEST-DAY2-001",
    "severity": "high",
    "threat_class": "c2_beaconing",
    "src_ip": "203.0.113.42",
    "threat_score": 0.91,
    "enrichment": {
        "virustotal": {
            "malicious": 7,
            "country": "RU",
            "as_owner": "AS12345 Some ISP",
        },
        "shodan": {
            "country": "Russia",
            "org": "Test Organization",
            "open_ports": [22, 80, 443, 3389],
            "vulns": ["CVE-2021-44228"],
        },
    },
}

success = send_alert_email(test_alert)
print(f"Email sent successfully: {success}")

if success:
    print("Check your inbox for the formatted alert email")
else:
    print("Check .env for SMTP credentials (EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECIPIENT)")

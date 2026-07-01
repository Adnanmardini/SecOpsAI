import json
import logging
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from kafka import KafkaConsumer

from enrichment.enricher import AlertEnricher
from notifications.email_notifier import send_alert_email
from response.containment import ContainmentEngine

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("secopsai.alert_consumer")

# ── Configuration ─────────────────────────────────────────────────────────
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC             = "detection-results"
GROUP_ID          = "secopsai-alert-consumer"
ALERT_THRESHOLD   = float(os.getenv("ALERT_THRESHOLD", "0.70"))
AUTO_CONTAIN_THRESHOLD = float(os.getenv("AUTO_CONTAIN_THRESHOLD", "0.90"))

# ── Severity classification ───────────────────────────────────────────────
def classify_severity(threat_score: float, threat_class: str) -> str:
    """Classify alert severity based on score and threat category."""
    if threat_score >= 0.90:
        return "critical"
    if threat_score >= 0.80:
        return "high"
    if threat_score >= 0.70:
        return "medium"
    return "low"


# ── PostgreSQL alert writer ───────────────────────────────────────────────
def write_alert_to_db(alert_data: dict) -> None:
    """Write enriched alert record to PostgreSQL security_alerts table."""
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO security_alerts (
                    alert_id, threat_class, threat_score, severity,
                    src_ip, dst_ip, vt_malicious_count, shodan_open_ports,
                    email_notified, status, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                alert_data["alert_id"],
                alert_data["threat_class"],
                alert_data["threat_score"],
                alert_data["severity"],
                alert_data.get("src_ip", "unknown"),
                alert_data.get("dst_ip", "unknown"),
                alert_data.get("vt_malicious_count", 0),
                json.dumps(alert_data.get("shodan_open_ports", [])),
                alert_data.get("email_sent", False),
                "open",
                datetime.now(timezone.utc)
            ))
            conn.commit()
        logger.info(f"Alert written to PostgreSQL: {alert_data['alert_id']}")
    except Exception as e:
        logger.error(f"Failed to write alert to PostgreSQL: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


# ── Main consumer loop ────────────────────────────────────────────────────
def run_consumer():
    """Main consumer loop — processes detection results from Kafka."""
    logger.info(f"Starting alert consumer on topic: {TOPIC}")
    logger.info(f"Alert threshold: {ALERT_THRESHOLD}")
    logger.info(f"Auto-containment threshold: {AUTO_CONTAIN_THRESHOLD}")

    enricher    = AlertEnricher()
    containment = ContainmentEngine()

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=-1,  # Run indefinitely
    )

    logger.info("Consumer ready — waiting for detection results...")

    for message in consumer:
        detection = message.value

        threat_score = float(detection.get("threat_score", 0.0))
        threat_class = str(detection.get("threat_class", "unknown"))
        src_ip       = detection.get("src_ip", "unknown")
        dst_ip       = detection.get("dst_ip", "unknown")

        # Filter: below threshold — log and skip
        if threat_score < ALERT_THRESHOLD or threat_class.lower() == "benign":
            logger.info(
                f"BELOW THRESHOLD — score={threat_score:.4f} "
                f"class={threat_class} — no alert"
            )
            continue

        # Above threshold — process alert
        import uuid
        alert_id = str(uuid.uuid4())
        severity = classify_severity(threat_score, threat_class)

        logger.info(
            f"ALERT TRIGGERED — "
            f"id={alert_id[:8]} "
            f"score={threat_score:.4f} "
            f"class={threat_class} "
            f"severity={severity} "
            f"src={src_ip}"
        )

        # Step 1: Enrich IP address
        logger.info(f"Enriching IP: {src_ip}")
        enrichment = enricher.enrich_ip(src_ip)

        alert_data = {
            "alert_id":            alert_id,
            "threat_class":        threat_class,
            "threat_score":        threat_score,
            "severity":            severity,
            "src_ip":              src_ip,
            "dst_ip":              dst_ip,
            "vt_malicious_count":  enrichment.get("vt_malicious_count", 0),
            "shodan_open_ports":   enrichment.get("open_ports", []),
            "timestamp":           datetime.now(timezone.utc).isoformat(),
        }

        # Step 2: Send email notification
        try:
            send_alert_email(alert_data)
            alert_data["email_sent"] = True
            logger.info("Email notification sent")
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            alert_data["email_sent"] = False

        # Step 3: Write to PostgreSQL
        write_alert_to_db(alert_data)

        # Step 4: Auto-containment for critical threats
        if (threat_score >= AUTO_CONTAIN_THRESHOLD and
                severity == "critical"):
            logger.info(
                f"AUTO-CONTAINMENT triggered — "
                f"score={threat_score:.4f} src={src_ip}"
            )
            containment.block_ip(
                ip=src_ip,
                reason=f"Auto-containment: {threat_class} score={threat_score:.4f}",
                alert_id=alert_id,
                triggered_by="automated_pipeline"
            )

        logger.info(f"Alert processing complete: {alert_id[:8]}")


if __name__ == "__main__":
    run_consumer()

import json
import os
import hashlib
import uuid
import time
from kafka import KafkaConsumer
from kafka.serializer import Deserializer
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.7"))


def compute_alert_hash(alert: dict) -> str:
    alert_str = json.dumps(alert, sort_keys=True, default=str)
    return hashlib.sha256(alert_str.encode()).hexdigest()


def process_detection(detection: dict):
    threat_score = float(detection.get("threat_score", 0.0))
    threat_class = detection.get("threat_class", "unknown")
    src_ip = detection.get("src_ip", "0.0.0.0")

    if threat_score < ALERT_THRESHOLD:
        logger.debug(f"Below threshold ({threat_score:.2f}): {threat_class}")
        return None

    logger.info(f"ALERT: {threat_class} | score={threat_score:.2%} | src={src_ip}")

    from alert_pipeline.enrichment.enricher import AlertEnricher
    from alert_pipeline.notifications.email_notifier import send_alert_email

    enricher = AlertEnricher()
    enrichment = enricher.enrich_ip(src_ip) if src_ip != "0.0.0.0" else {}

    alert = {
        "alert_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "threat_score": threat_score,
        "threat_class": threat_class,
        "src_ip": src_ip,
        "dst_ip": detection.get("dst_ip", "unknown"),
        "severity": enrichment.get("severity", "medium"),
        "enrichment": enrichment,
        "status": "open",
    }

    alert["alert_hash"] = compute_alert_hash(alert)
    email_sent = send_alert_email(alert)
    alert["email_notified"] = email_sent

    logger.info(f"Alert {alert['alert_id']} processed | severity={alert['severity']} | email={email_sent}")
    return alert


class JSONDeserializer(Deserializer):
    def deserialize(self, topic, bytes_):
        if bytes_ is None:
            return None
        return json.loads(bytes_.decode("utf-8"))


def run_consumer():
    logger.info("Starting alert pipeline consumer...")
    logger.info(f"Alert threshold: {ALERT_THRESHOLD}")

    consumer = KafkaConsumer(
        "detection-results",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="alert-pipeline-group",
        value_deserializer=JSONDeserializer(),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    logger.info("Consumer connected to Kafka. Waiting for messages...")
    processed = 0
    alerts_fired = 0

    try:
        for message in consumer:
            try:
                detection = message.value
                alert = process_detection(detection)

                if alert:
                    alerts_fired += 1
                    logger.info(f"Alert fired #{alerts_fired}: {alert['alert_id']}")

                processed += 1
                consumer.commit()

                if processed % 100 == 0:
                    logger.info(f"Processed {processed} messages, {alerts_fired} alerts fired")

            except Exception as e:
                logger.error(f"Error processing message: {e}")

    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    finally:
        consumer.close()
        logger.info(f"Consumer shutdown. Total processed: {processed}, alerts fired: {alerts_fired}")


if __name__ == "__main__":
    run_consumer()

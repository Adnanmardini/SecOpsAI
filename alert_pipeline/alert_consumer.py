import json
import os
from datetime import datetime
from kafka import KafkaConsumer
from loguru import logger
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def run_consumer():
    logger.info("Starting alert pipeline consumer...")
    
    try:
        consumer = KafkaConsumer(
            "detection-results",
            bootstrap_servers=["kafka:29092"],
            group_id="alert-group",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            enable_auto_commit=False,
            auto_offset_reset='earliest'
        )
    except Exception as e:
        logger.error(f"Kafka connection failed: {e}")
        return
    
    logger.info("Consumer connected to Kafka...")
    
    # Database connection
    try:
        conn = psycopg2.connect(host="postgres", port="5432", database="secopsai", user="postgres", password="postgres")
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        conn = None
    
    for message in consumer:
        try:
            detection = message.value
            threat_score = detection.get("threat_score", 0)
            prediction = detection.get("prediction", "unknown")
            alert_triggered = detection.get("alert_triggered", False)
            
            severity = "CRITICAL" if threat_score >= 0.9 else "HIGH" if threat_score >= 0.7 else "MEDIUM" if threat_score >= 0.5 else "LOW"
            
            logger.info(f"Received: {prediction} - score={threat_score} - severity={severity}")
            
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO security_alerts (threat_class, severity, threat_score, alert_triggered, timestamp) VALUES (%s, %s, %s, %s, %s)",
                    (prediction, severity, threat_score, alert_triggered, datetime.utcnow())
                )
                conn.commit()
                cursor.close()
                logger.info(f"Alert logged to database: {prediction}")
            
            consumer.commit()
        except Exception as e:
            logger.error(f"Error: {e}")
    
    if conn:
        conn.close()

if __name__ == "__main__":
    run_consumer()

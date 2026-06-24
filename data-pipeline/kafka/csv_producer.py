"""
CICIDS CSV Kafka Producer
Reads CICIDS 2017 CSV files and publishes records to Kafka.
"""

import pandas as pd
import json
import time
import os
import glob
import hashlib
import hmac as hmac_lib
from kafka import KafkaProducer
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
HMAC_SECRET = os.getenv("KAFKA_HMAC_SECRET", "default-secret-change-in-prod")
TOPIC = "raw-network-flows"
DATA_DIR = "datasets/cicids2017"


def sign_message(payload: bytes, secret: str) -> str:
    return hmac_lib.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
        retries=3,
    )


def produce_from_csv(csv_file: str, producer: KafkaProducer, limit: int = 10000):
    logger.info(f"Loading: {csv_file}")
    df = pd.read_csv(csv_file, low_memory=False)
    df.columns = df.columns.str.strip()

    sent = 0
    errors = 0

    for _, row in df.head(limit).iterrows():
        try:
            record = row.to_dict()
            record["_source"] = "cicids_csv"
            record["_file"] = os.path.basename(csv_file)
            record["_ingestion_time"] = time.time()
            payload = json.dumps(record, sort_keys=True, default=str).encode()
            record["_integrity_hmac"] = sign_message(payload, HMAC_SECRET)
            producer.send(TOPIC, value=record)
            sent += 1
            if sent % 1000 == 0:
                logger.info(f"  Sent {sent:,} records from {os.path.basename(csv_file)}")
        except Exception as e:
            errors += 1
            logger.warning(f"  Failed to send record: {e}")

    producer.flush()
    logger.info(f"  Complete: {sent:,} sent, {errors} errors")
    return sent


def main():
    files = glob.glob(f"{DATA_DIR}/*.csv")
    if not files:
        logger.error(f"No CSV files in {DATA_DIR}/")
        return
    logger.info(f"Found {len(files)} CSV files")
    producer = create_producer()
    total_sent = 0
    for csv_file in files:
        records = produce_from_csv(csv_file, producer)
        total_sent += records
    producer.close()
    logger.info(f"Pipeline complete. Total records sent: {total_sent:,}")


if __name__ == "__main__":
    main()

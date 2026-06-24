from kafka import KafkaProducer
import json, os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode()
)

producer.send("detection-results", value={
    "threat_score": 0.35,
    "threat_class": "benign",
    "src_ip":       "192.168.1.10",
    "dst_ip":       "8.8.8.8",
})
print("Sent: below-threshold detection (should NOT fire alert)")

producer.send("detection-results", value={
    "threat_score": 0.94,
    "threat_class": "c2_beaconing",
    "src_ip":       "8.8.8.8",
    "dst_ip":       "192.168.1.100",
})
print("Sent: high-score detection (SHOULD fire alert + email)")
producer.flush()
producer.close()


import time
import json
import os
import random
from kafka import KafkaProducer
from dotenv import load_dotenv
load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode()
)

THREAT_TYPES = ['c2_beaconing', 'lateral_movement', 'dns_tunneling', 'exfiltration', 'benign']

print("Generating demo traffic...")
start = time.time()
sent = 0

while time.time() - start < 300:  # 5 minutes only (not 30) to save time
    threat_class = random.choice(THREAT_TYPES)
    score = random.uniform(0.75, 0.98) if threat_class != 'benign' else random.uniform(0.05, 0.35)
    producer.send("detection-results", value={
        "threat_score": round(score, 4),
        "threat_class": threat_class,
        "src_ip": f"192.168.{random.randint(1,10)}.{random.randint(1,255)}",
        "dst_ip": f"203.0.113.{random.randint(1,50)}",
    })
    sent += 1
    if sent % 50 == 0:
        print(f"Sent {sent} detections ({(time.time()-start)/60:.1f} min elapsed)")
    time.sleep(2)

producer.flush()
producer.close()
print(f"Complete: {sent} detections sent")

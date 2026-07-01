#!/bin/bash

TOPICS=(
raw-network-flows
feature-vectors
detection-results
security-alerts
)

for topic in "${TOPICS[@]}"
do
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
--bootstrap-server localhost:9092 \
--create \
--if-not-exists \
--topic "$topic" \
--partitions 3 \
--replication-factor 1

echo "✓ $topic"
done

#!/bin/bash
# Creates all Kafka topics needed for SecOpsAI
KAFKA_BROKER="${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"

echo "[*] Setting up Kafka topics on $KAFKA_BROKER ..."

kafka-topics --create \
    --bootstrap-server "$KAFKA_BROKER" \
    --topic raw-network-flows \
    --partitions 3 \
    --replication-factor 1 \
    --config retention.ms=86400000 \
    --if-not-exists
echo "  ✓ raw-network-flows"

kafka-topics --create \
    --bootstrap-server "$KAFKA_BROKER" \
    --topic feature-vectors \
    --partitions 3 \
    --replication-factor 1 \
    --config retention.ms=86400000 \
    --if-not-exists
echo "  ✓ feature-vectors"

kafka-topics --create \
    --bootstrap-server "$KAFKA_BROKER" \
    --topic detection-results \
    --partitions 2 \
    --replication-factor 1 \
    --config retention.ms=604800000 \
    --if-not-exists
echo "  ✓ detection-results"

kafka-topics --create \
    --bootstrap-server "$KAFKA_BROKER" \
    --topic security-alerts \
    --partitions 2 \
    --replication-factor 1 \
    --config retention.ms=2592000000 \
    --if-not-exists
echo "  ✓ security-alerts"

echo "[*] Current topics:"
kafka-topics --list --bootstrap-server "$KAFKA_BROKER"

# Data Pipeline Guide — SecOpsAI (Team DefenseGrid)


## Overview

This document describes the complete SecOpsAI data pipeline — from raw CICIDS 2017 CSV ingestion through Kafka message streaming to final storage in PostgreSQL. It covers the pipeline architecture, Kafka topic schema, data integrity controls, and a full troubleshooting reference for common failures.

---

## Pipeline Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  CICIDS 2017    │     │   Kafka Producer     │     │  Kafka Broker    │     │  Kafka Consumer  │
│  CSV Dataset    │────▶│  (cicids_producer.py) │────▶│  Topic:          │────▶│ (consumer.py)    │
│  (./data/)      │     │  Reads, cleans,      │     │  network-events  │     │  Validates,      │
│                 │     │  serialises to JSON  │     │                  │     │  normalises,     │
└─────────────────┘     └──────────────────────┘     └──────────────────┘     │  writes to DB    │
                                                                               └────────┬─────────┘
                                                                                        │
                                                                                        ▼
                                                                               ┌──────────────────┐
                                                                               │   PostgreSQL     │
                                                                               │   secopsai DB    │
                                                                               │   (network_flows │
                                                                               │    table)        │
                                                                               └──────────────────┘
```

---

## Stage 1: CSV Ingestion (Producer)

### Dataset

The pipeline uses the **CICIDS 2017** (Canadian Institute for Cybersecurity Intrusion Detection dataset). It contains 78 network flow features per record, labelled as either `BENIGN` or a named attack class (e.g., `DoS Hulk`, `PortScan`, `Bot`).

**File location (inside container):** `/data/cicids.csv`  
**Host mount:** `./data/cicids.csv` (relative to project root)

### Producer Behaviour

1. **Load** — The producer reads the CSV using `pandas` in chunked mode to avoid loading the full dataset into memory.
2. **Clean** — Columns with all-null values, infinite values, and whitespace-padded column names are handled at this stage.
3. **Select** — Only a subset of the 78 features are forwarded downstream (see Feature Selection below).
4. **Serialise** — Each cleaned row is serialised to a JSON string and published to Kafka.
5. **Batch publish** — Records are published in configurable batches (default: 500 per batch) with a short interval between batches to avoid overwhelming the broker.

### Feature Selection (Fields Published to Kafka)

| Field | Type | Description |
|---|---|---|
| `flow_id` | string | Unique identifier per flow record |
| `src_ip` | string | Source IP address |
| `src_port` | integer | Source port number |
| `dst_ip` | string | Destination IP address |
| `dst_port` | integer | Destination port number |
| `protocol` | integer | Protocol code (6=TCP, 17=UDP) |
| `flow_duration` | float | Duration of the flow in microseconds |
| `total_fwd_packets` | integer | Total packets in forward direction |
| `total_bwd_packets` | integer | Total packets in backward direction |
| `flow_bytes_per_sec` | float | Bytes per second throughput |
| `flow_packets_per_sec` | float | Packets per second throughput |
| `label` | string | Ground truth class (`BENIGN` or attack name) |
| `timestamp` | string | ISO 8601 event timestamp |

---

## Stage 2: Kafka Message Broker

### Topic Descriptions

| Topic Name | Partitions | Retention | Purpose |
|---|---|---|---|
| `network-events` | 1 | 24 hours | Primary pipeline topic. All CICIDS flow records are published here by the producer and consumed by the main consumer. |
| `dead-letter-queue` | 1 | 72 hours | Malformed or unprocessable messages are routed here by the consumer for inspection and replay. |

### Message Format

Each Kafka message on `network-events` is a JSON-encoded string with the fields listed in the Feature Selection table above. The Kafka message key is set to `src_ip` to ensure all flows from the same source are handled by the same consumer partition (relevant when scaling consumers).

**Example message payload:**
```json
{
  "flow_id": "f3a91c2e-...",
  "src_ip": "192.168.1.45",
  "src_port": 54312,
  "dst_ip": "203.0.113.5",
  "dst_port": 80,
  "protocol": 6,
  "flow_duration": 1842350.0,
  "total_fwd_packets": 14,
  "total_bwd_packets": 11,
  "flow_bytes_per_sec": 2104.5,
  "flow_packets_per_sec": 13.56,
  "label": "DoS Hulk",
  "timestamp": "2026-06-20T14:32:10Z"
}
```

### Consumer Group

| Setting | Value |
|---|---|
| Group ID | `secops-consumer-group` |
| Auto offset reset | `earliest` (processes from beginning if no committed offset exists) |
| Commit mode | Manual (consumer commits offset only after successful DB write) |

---

## Stage 3: Consumer & Database Write

### Consumer Behaviour

1. **Poll** — Consumer polls `network-events` in a continuous loop.
2. **Deserialise** — JSON string decoded to a Python dict.
3. **Validate** — Data integrity checks applied (see Data Integrity Controls below).
4. **Normalise** — Field types cast to match PostgreSQL schema.
5. **Write** — Record inserted into the `network_flows` table via `psycopg2`.
6. **Commit** — Kafka offset committed after successful DB insertion.
7. **Dead-letter** — If validation or DB write fails after retries, the raw message is published to `dead-letter-queue`.

### PostgreSQL Schema: `network_flows`

```sql
CREATE TABLE IF NOT EXISTS network_flows (
    id              SERIAL PRIMARY KEY,
    flow_id         VARCHAR(64) UNIQUE NOT NULL,
    src_ip          INET,
    src_port        INTEGER,
    dst_ip          INET,
    dst_port        INTEGER,
    protocol        SMALLINT,
    flow_duration   DOUBLE PRECISION,
    total_fwd_pkts  INTEGER,
    total_bwd_pkts  INTEGER,
    bytes_per_sec   DOUBLE PRECISION,
    pkts_per_sec    DOUBLE PRECISION,
    label           VARCHAR(64),
    is_attack       BOOLEAN GENERATED ALWAYS AS (label != 'BENIGN') STORED,
    ingested_at     TIMESTAMP DEFAULT NOW(),
    raw_timestamp   TIMESTAMPTZ
);
```

---

## Data Integrity Controls

The consumer applies the following checks before writing any record to PostgreSQL:

| Check | Rule | On Failure |
|---|---|---|
| **Schema validation** | All required fields must be present in the JSON payload | Route to dead-letter-queue |
| **Null check** | `flow_id`, `src_ip`, `dst_ip`, and `label` must not be null | Route to dead-letter-queue |
| **Type coercion** | Numeric fields cast to correct Python types; invalid values caught with try/except | Route to dead-letter-queue |
| **Duplicate detection** | `flow_id` has a `UNIQUE` constraint in PostgreSQL | PostgreSQL raises `UniqueViolation`; consumer logs and skips |
| **Range check** | Ports must be 0–65535; protocol must be in `{6, 17, 1}` | Log warning; clamp or discard |
| **Infinite / NaN values** | `float('inf')` and `float('nan')` are rejected | Replace with `NULL` and log |
| **Label whitelist** | `label` must be a known CICIDS class or `BENIGN` | Log anomaly; still write with `label=UNKNOWN` |

---

## Stress Test Summary

A 50,000-record stress test was successfully executed on the `dev` branch in GitHub Codespaces:

| Metric | Result |
|---|---|
| Records published | 50,000 |
| Records consumed & written | 50,000 |
| Dead-letter messages | 0 |
| Duplicate rejections | 0 |
| End-to-end duration | ~4 minutes |
| PostgreSQL row count (post-test) | 50,000 |
| Data loss | None |

---

## Troubleshooting

### T1 — Producer exits with `NoBrokersAvailable`

**Symptom:** Producer container starts and immediately exits. Logs show `NoBrokersAvailable` or `KafkaConnectionError`.

**Cause:** Kafka broker is not yet ready when the producer attempts to connect. This is a startup race condition.

**Fix:**
```bash
# Check if kafka is running
docker compose ps

# If kafka exited, restart it
docker compose restart kafka

# Add retry logic — the producer already has a retry loop.
# If it failed before Kafka was ready, simply restart the producer:
docker compose restart producer
```

**Prevention:** The producer's connection logic includes exponential backoff retries (5 attempts, 5s apart). If Kafka takes longer than 25s to start, increase `KAFKA_CONNECT_RETRIES` in the environment.

---

### T2 — Consumer not writing to PostgreSQL

**Symptom:** Consumer logs show messages being polled but row count in `network_flows` does not increase.

**Cause (a):** PostgreSQL connection failure.
```bash
docker compose logs consumer | grep "OperationalError"
# If you see psycopg2.OperationalError, Postgres may be starting up
docker compose restart consumer
```

**Cause (b):** Schema mismatch — table does not exist yet.
```bash
docker compose exec postgres psql -U secops -d secopsai -c "\dt"
# If network_flows is missing, run the init script:
docker compose exec postgres psql -U secops -d secopsai -f /docker-entrypoint-initdb.d/init.sql
```

---

### T3 — Messages stuck in `network-events` topic (lag building up)

**Symptom:** `kafka-consumer-groups.sh` shows increasing consumer lag. Producer is publishing but consumer is not keeping up.

**Fix:**
```bash
# Check consumer logs for errors
docker compose logs -f consumer

# If consumer is healthy but slow, scale up:
docker compose up -d --scale consumer=3
```

> Note: Scaling consumers only helps if the topic has multiple partitions. In dev (1 partition), only 1 consumer will be active at a time.

---

### T4 — Duplicate `flow_id` errors in consumer logs

**Symptom:** Logs show `psycopg2.errors.UniqueViolation` on `flow_id`.

**Cause:** Producer restarted mid-run and re-published records already committed to PostgreSQL.

**Fix:** This is handled gracefully — the consumer catches `UniqueViolation`, logs a warning, and skips the duplicate without crashing. No action required. To clear and re-run from scratch:
```bash
docker compose down -v
docker compose up -d
```

---

### T5 — Dead-letter messages appearing unexpectedly

**Symptom:** `dead-letter-queue` topic has messages after a run.

**Fix:**
```bash
# Inspect dead-letter messages using kafka-console-consumer
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic dead-letter-queue \
  --from-beginning \
  --max-messages 10
```
Review the raw JSON to identify which validation check failed. Common causes: missing `flow_id`, unexpected null in `src_ip`, or a CSV column that was renamed in a newer dataset version.

---

### T6 — GitHub Codespaces: port not accessible in browser

**Symptom:** FastAPI or frontend not reachable via the Codespaces forwarded URL.

**Fix:**
1. Open the **Ports** tab in the Codespaces panel.
2. Ensure ports `3000`, `8000`, and `5432` are forwarded.
3. Set visibility to **Public** if collaborators need access.
4. If a port shows as "not running", confirm the container is up: `docker compose ps`.

---

### T7 — `docker compose up` fails with `bind: address already in use`

**Symptom:** Error on startup: `Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use`.

**Fix (local machine):**
```bash
# Find what's using the port
sudo lsof -i :5432
# Stop local PostgreSQL
sudo systemctl stop postgresql
```

**Fix (Codespaces):** Another Codespace session may have forwarded the same port. Close the other session or change the host port mapping in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"   # map to 5433 on host instead
```

---

## Monitoring Queries

Use these SQL queries to verify pipeline health after a run:

```sql
-- Total records ingested
SELECT COUNT(*) FROM network_flows;

-- Breakdown by label
SELECT label, COUNT(*) AS count
FROM network_flows
GROUP BY label
ORDER BY count DESC;

-- Attack vs benign ratio
SELECT is_attack, COUNT(*) FROM network_flows GROUP BY is_attack;

-- Last 10 records ingested
SELECT flow_id, src_ip, dst_ip, label, ingested_at
FROM network_flows
ORDER BY ingested_at DESC
LIMIT 10;

-- Check for any NULL flow_ids (data quality)
SELECT COUNT(*) FROM network_flows WHERE flow_id IS NULL;
```

---


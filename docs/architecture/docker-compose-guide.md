# Docker Compose Guide — SecOpsAI (Team DefenseGrid)


## Overview

This guide covers every service defined in the SecOpsAI `docker-compose.yml`, their dependencies, environment variables, common operational commands, and how the stack starts up end-to-end. Follow this guide to spin up, monitor, and tear down the full development environment.

---

## Prerequisites

| Requirement | Minimum Version |
|---|---|
| Docker Engine | 24.x |
| Docker Compose (plugin) | v2.x (`docker compose` not `docker-compose`) |
| Available RAM | 4 GB |
| Available Disk | 10 GB free |

> **GitHub Codespaces users:** Docker-in-Docker is pre-configured. Run all commands in the integrated terminal without any additional setup.

---

## Service Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│                    Docker Network: secops-net           │
│                                                        │
│  [Zookeeper] ──▶ [Kafka Broker] ──▶ [Kafka Producer]  │
│                        │                               │
│                        ▼                               │
│                 [Kafka Consumer] ──▶ [PostgreSQL]      │
│                                         │              │
│                  [FastAPI Backend] ◀────┘              │
│                        │                               │
│                   [Frontend UI]                        │
└────────────────────────────────────────────────────────┘
```

---

## Services

### 1. `zookeeper`

**Image:** `confluentinc/cp-zookeeper:7.5.0`  
**Role:** Coordination service required by Kafka for broker registration, leader election, and cluster metadata management.

| Environment Variable | Value | Description |
|---|---|---|
| `ZOOKEEPER_CLIENT_PORT` | `2181` | Port Kafka uses to connect to Zookeeper |
| `ZOOKEEPER_TICK_TIME` | `2000` | Heartbeat interval in milliseconds |

**Ports:** `2181:2181`  
**Dependencies:** None (starts first)  
**Health check:** Zookeeper is considered ready when Kafka successfully registers with it.

---

### 2. `kafka`

**Image:** `confluentinc/cp-kafka:7.5.0`  
**Role:** Core message broker. Receives network event records from the producer and queues them for the consumer pipeline.

| Environment Variable | Value | Description |
|---|---|---|
| `KAFKA_BROKER_ID` | `1` | Unique broker identifier in the cluster |
| `KAFKA_ZOOKEEPER_CONNECT` | `zookeeper:2181` | Zookeeper connection string |
| `KAFKA_ADVERTISED_LISTENERS` | `PLAINTEXT://kafka:9092` | Listener address advertised to producers/consumers |
| `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR` | `1` | Single-node replication (dev mode) |
| `KAFKA_AUTO_CREATE_TOPICS_ENABLE` | `true` | Allows topics to be created on first publish |

**Ports:** `9092:9092`  
**Dependencies:** `zookeeper` (must be healthy)

---

### 3. `postgres`

**Image:** `postgres:15-alpine`  
**Role:** Persistent data store for processed network flow records and ML-scored threat events.

| Environment Variable | Value | Description |
|---|---|---|
| `POSTGRES_USER` | `secops` | Database superuser username |
| `POSTGRES_PASSWORD` | `secops_pass` | Database superuser password |
| `POSTGRES_DB` | `secopsai` | Default database name |

**Ports:** `5432:5432`  
**Volume:** `postgres_data:/var/lib/postgresql/data` (data persists across restarts)  
**Dependencies:** None

> **Security note:** These are development-only credentials. Never use these values in staging or production. Use `.env` files and Docker secrets for sensitive environments.

---

### 4. `producer`

**Build context:** `./kafka_producer`  
**Role:** Reads CICIDS 2017 CSV data, preprocesses records, and publishes them to the `network-events` Kafka topic. Acts as the entry point of the data pipeline.

| Environment Variable | Value | Description |
|---|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Kafka broker address |
| `KAFKA_TOPIC` | `network-events` | Target topic for published events |
| `CSV_PATH` | `/data/cicids.csv` | Path to the mounted CICIDS dataset |
| `BATCH_SIZE` | `500` | Records per Kafka batch publish |
| `PUBLISH_INTERVAL_MS` | `100` | Delay between batches (milliseconds) |

**Dependencies:** `kafka`  
**Volume (read-only):** `./data:/data:ro`

---

### 5. `consumer`

**Build context:** `./kafka_consumer`  
**Role:** Subscribes to the `network-events` Kafka topic, applies data validation and normalisation, then writes records to PostgreSQL.

| Environment Variable | Value | Description |
|---|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Kafka broker address |
| `KAFKA_TOPIC` | `network-events` | Topic to subscribe to |
| `KAFKA_GROUP_ID` | `secops-consumer-group` | Consumer group identifier |
| `DB_HOST` | `postgres` | PostgreSQL service hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `secopsai` | Target database |
| `DB_USER` | `secops` | Database user |
| `DB_PASSWORD` | `secops_pass` | Database password |

**Dependencies:** `kafka`, `postgres`

---

### 6. `backend`

**Build context:** `./backend`  
**Role:** FastAPI application exposing REST endpoints for the frontend and external integrations. Queries PostgreSQL for threat summaries, live stats, and alert data.

| Environment Variable | Value | Description |
|---|---|---|
| `DB_HOST` | `postgres` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `secopsai` | Database name |
| `DB_USER` | `secops` | Database user |
| `DB_PASSWORD` | `secops_pass` | Database password |
| `API_PORT` | `8000` | Port FastAPI listens on |

**Ports:** `8000:8000`  
**Dependencies:** `postgres`

---

### 7. `frontend`

**Build context:** `./frontend`  
**Role:** Web UI for the SecOpsAI dashboard. Displays real-time threat detection results, pipeline status, and alert summaries.

| Environment Variable | Value | Description |
|---|---|---|
| `REACT_APP_API_URL` | `http://backend:8000` | Backend API base URL |

**Ports:** `3000:3000`  
**Dependencies:** `backend`

---

## Volumes

| Volume Name | Used By | Purpose |
|---|---|---|
| `postgres_data` | `postgres` | Persistent storage for all database data |

---

## Common Commands

### Start the full stack
```bash
docker compose up -d
```

### Start and stream logs
```bash
docker compose up
```

### Start specific services only
```bash
docker compose up -d zookeeper kafka postgres
```

### View logs for a service
```bash
docker compose logs -f consumer
docker compose logs -f producer
```

### Stop all services (preserve volumes)
```bash
docker compose down
```

### Stop and delete all data (full reset)
```bash
docker compose down -v
```

### Rebuild a service image after code changes
```bash
docker compose build consumer
docker compose up -d consumer
```

### Check running service health
```bash
docker compose ps
```

### Open a shell inside a running container
```bash
docker compose exec postgres psql -U secops -d secopsai
docker compose exec consumer bash
```

### Scale the consumer (parallel processing)
```bash
docker compose up -d --scale consumer=3
```

---

## Startup Order & Dependency Chain

Docker Compose respects the `depends_on` directives in this order:

```
1. zookeeper         (no dependencies)
2. postgres          (no dependencies)
3. kafka             (depends on: zookeeper)
4. producer          (depends on: kafka)
5. consumer          (depends on: kafka, postgres)
6. backend           (depends on: postgres)
7. frontend          (depends on: backend)
```

> Allow 20–30 seconds after `docker compose up` for Kafka and Zookeeper to fully initialise before the producer begins publishing.

---

## Environment File (.env)

For local development, create a `.env` file in the project root to override defaults:

```env
POSTGRES_USER=secops
POSTGRES_PASSWORD=secops_pass
POSTGRES_DB=secopsai
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

Docker Compose automatically loads `.env` from the project root. Never commit this file to version control — it is listed in `.gitignore`.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `kafka` exits immediately | Zookeeper not ready | Add `restart: on-failure` to kafka service or wait 10s and re-run `docker compose up` |
| `consumer` can't reach PostgreSQL | Postgres still initialising | Consumer has retry logic — check logs with `docker compose logs consumer` |
| Port `5432` already in use | Local PostgreSQL running | Stop local service: `sudo systemctl stop postgresql` |
| `producer` finishes with 0 records | CSV path wrong or file missing | Confirm `./data/cicids.csv` exists relative to `docker-compose.yml` |
| Codespaces: port not accessible | Port forwarding not set | Open Ports tab → forward 8000, 3000, 5432 |

---
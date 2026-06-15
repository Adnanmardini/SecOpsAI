# Network Telemetry Pipeline — SecOpsAI

## Overview
Ingests raw PCAP, processes it through Zeek into structured JSON logs, and prepares Kafka topics for downstream feature engineering and detection.

## Data Flow
External PCAP → Zeek (local.zeek) → JSON logs → (future Kafka producer) → `raw-network-flows` topic

## Zeek Configuration
- **Config file**: `data-pipeline/zeek-config/local.zeek`
- **Loaded analyzers**: conn, dns, http, ssl, notice  
- **Output**: JSON (`redef LogAscii::use_json = T`)
- **Rationale**: protocol coverage directly targets C2, DNS tunneling, and lateral movement.

## PCAP Processing Script
- **Script**: `data-pipeline/zeek-config/process_pcap.sh`
- **Usage**: `./process_pcap.sh <pcap_file> [output_dir]`
- **Effect**: runs Zeek with the SecOpsAI config and writes JSON logs to the given directory.

## Kafka Topics
- **Setup script**: `data-pipeline/kafka/setup_topics.sh`
- **Topics created**:
  - `raw-network-flows` (retention 1 day)
  - `feature-vectors` (1 day)
  - `detection-results` (7 days)
  - `security-alerts` (30 days)
- The script is idempotent (`--if-not-exists`) and lists all topics after creation.

## Verification
- `zeek --version` shows a valid version.
- `process_pcap.sh` can process a dummy PCAP and produce JSON logs.
- `setup_topics.sh` (run when Kafka is available) creates and lists the four topics.

## Security Note
- Trust boundary: raw PCAP is untrusted; Zeek runs with only necessary analyzers.
- Future Kafka producers will implement HMAC message signing (per STRIDE T01).

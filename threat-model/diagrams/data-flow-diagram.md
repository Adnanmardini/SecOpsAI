# Data Flow Diagram — SecOpsAI
**Version:** 1.0
**Date:** 2026-06-10
**Author:** Security Architect

## Flow 1 - Telemetry Ingestion

Network Traffic
→ Zeek/Suricata
→ Kafka Producer
→ Feature Consumer
→ PostgreSQL

Security Control:
- HMAC Signing
- Message Validation

## Flow 2 - Threat Detection

PostgreSQL
→ Detection API
→ StandardScaler
→ XGBoost Model
→ Detection Results Table

Security Control:
- JWT Authentication
- RBAC
- Input Validation
- SQLAlchemy ORM

## Flow 3 - Alert Pipeline

Detection Results
→ Kafka Topic
→ Alert Consumer
→ VirusTotal
→ Shodan
→ Severity Calculator
→ Security Alerts Table
→ Email Notification

Security Control:
- API Response Validation
- Timeouts
- Retry Logic

## Flow 4 - Automated Response

Critical Alert
→ Containment Engine
→ Audit Log
→ Mock Containment Action
→ Analyst Notification

Security Control:
- Action Logging
- Rollback Support

## Flow 5 - Observability

API Requests
→ Prometheus
→ Grafana

API Requests
→ Audit Log

ML Predictions
→ MLflow

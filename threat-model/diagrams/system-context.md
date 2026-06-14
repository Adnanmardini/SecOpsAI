# System Context Diagram — SecOpsAI
**Version:** 1.0
**Date:** 2026-06-10
**Author:** Security Architect

## External Actors

| Actor | Description |
|---|---|
| Network Traffic Sources | Endpoints, switches and firewalls generating traffic |
| VirusTotal | Threat intelligence provider |
| Shodan | External host intelligence provider |
| SOC Analysts | Human users of the platform |
| Notification Recipients | Security team email inbox |
| GitHub | Source code and CI/CD platform |

## Internal Components

| Component | Technology |
|---|---|
| Data Ingestion | Zeek + Suricata |
| Message Queue | Apache Kafka |
| Feature Engineering | Python |
| ML Detection Engine | XGBoost + PyTorch |
| Detection API | FastAPI |
| Alert Pipeline | Python |
| Database | PostgreSQL |
| Model Tracking | MLflow |
| Monitoring | Prometheus + Grafana |

## Data Flow

Network Traffic → Zeek/Suricata → Kafka → Feature Engineering → ML Detection Engine → Alert Pipeline

Alert Pipeline → VirusTotal

Alert Pipeline → Shodan

Alert Pipeline → Email Notifications

SOC Analyst → Detection API

GitHub → Docker Deployment

## Trust Boundaries

TB1: External Network → Zeek

TB2: Kafka → Feature Engineering

TB3: Client → Detection API

TB4: Application → PostgreSQL

TB5: Alert Pipeline → External APIs

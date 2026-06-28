# STRIDE Implementation Audit — Day 3
Date: 2026-06-23
Auditor: Security Architect

## Audit Method
For each threat, inspect the actual code/config. Record evidence with file paths and line numbers.

## Audit Table
| Threat ID | Mitigation Required | Where to Check | Status | Evidence | Gap? |
|---|---|---|---|---|---|
| T01 | HMAC signing on Kafka messages | data-pipeline/kafka/zeek_producer.py | | | |
| T02 | Adversarial training + input validation | ml-engine/adversarial/ + api/app/main.py | | | |
| T03 | JWT 30-min expiry + HTTPS | api/app/auth.py | | | |
| T04 | Rate limiting on API endpoints | api/app/main.py (slowapi) | | | |
| T05 | Parameterized queries only | api/app/models/crud.py | | | |
| T06 | Hash-chained audit log + no-delete rule | api/app/audit_logger.py + init.sql | | | |
| T07 | Training data integrity checks | data-pipeline/feature_engineering/ | | | |
| T08 | RBAC scope check on every endpoint | api/app/auth.py (require_role) | | | |
| T09 | .env in .gitignore + secret scanning in CI | .gitignore + .github/workflows/ci.yml | | | |
| T10 | Feature distribution monitoring | data-pipeline/feature_engineering/engineer.py | | | |
| T11 | Non-root users in all Dockerfiles | api/Dockerfile + alert_pipeline/Dockerfile | | | |
| T12 | Audit log before action + rollback doc | alert_pipeline/response/containment.py | | | |
| AI01 | Rate limiting + return class only | api/app/main.py | | | |
| AI02 | Anomaly detection on label distribution | data-pipeline/feature_engineering/ | | | |
| AI03 | Rate limiting + query monitoring | api/app/main.py | | | |

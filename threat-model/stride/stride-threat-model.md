# STRIDE Threat Model — SecOpsAI
**Version:** 1.0
**Date:** 2026-06-10
**Author:** Security Architecture Team

| ID | Threat | Mitigation | Severity |
|----|---------|------------|----------|
| T01 | Kafka Message Tampering | HMAC Signing | Critical |
| T02 | ML Evasion Attacks | Adversarial Training | Critical |
| T03 | JWT Token Replay | Short Token Lifetime | High |
| T04 | API DoS Attack | Rate Limiting | High |
| T05 | SQL Injection | ORM + Validation | High |
| T06 | Audit Log Manipulation | Append-only Logs | High |
| T07 | Training Data Poisoning | Dataset Validation | Critical |
| T08 | Privilege Escalation | RBAC Enforcement | Critical |
| T09 | Secret Leakage | GitLeaks + .gitignore | High |
| T10 | Feature Manipulation | Input Validation | High |
| T11 | Container Escape | Non-root Containers | High |
| T12 | False Positive Response | Audit Logging | High |

## AI Threats

| ID | Threat | Mitigation |
|----|---------|------------|
| AI01 | Model Inversion | Rate Limiting |
| AI02 | Membership Inference | Dataset Monitoring |

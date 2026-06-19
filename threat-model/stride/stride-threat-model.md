# STRIDE Threat Model — SecOpsAI

**Version:** 1.1
**Date:** 2026-06-11
**Author:** Security Architecture Team

| ID  | STRIDE Category        | Threat                  | Mitigation            | Severity | Owner               | Status  |
| --- | ---------------------- | ----------------------- | --------------------- | -------- | ------------------- | ------- |
| T01 | Tampering              | Kafka Message Tampering | HMAC Signing          | Critical | Data Pipeline Team  | Planned |
| T02 | Tampering              | ML Evasion Attacks      | Adversarial Training  | Critical | ML Team             | Planned |
| T03 | Spoofing               | JWT Token Replay        | Short Token Lifetime  | High     | API Security Team   | Planned |
| T04 | Denial of Service      | API DoS Attack          | Rate Limiting         | High     | API Security Team   | Planned |
| T05 | Tampering              | SQL Injection           | ORM + Validation      | High     | API Security Team   | Planned |
| T06 | Repudiation            | Audit Log Manipulation  | Append-only Logs      | High     | Infrastructure Team | Planned |
| T07 | Tampering              | Training Data Poisoning | Dataset Validation    | Critical | ML Team             | Planned |
| T08 | Elevation of Privilege | Privilege Escalation    | RBAC Enforcement      | Critical | Infrastructure Team | Planned |
| T09 | Information Disclosure | Secret Leakage          | GitLeaks + .gitignore | High     | Infrastructure Team | Planned |
| T10 | Tampering              | Feature Manipulation    | Input Validation      | High     | ML Team             | Planned |
| T11 | Elevation of Privilege | Container Escape        | Non-root Containers   | High     | Infrastructure Team | Planned |
| T12 | Repudiation            | False Positive Response | Audit Logging         | High     | Alerting/SOC Team   | Planned |

## AI-Specific Threats

| ID   | STRIDE Category        | Threat               | Mitigation         | Severity | Owner   | Status  |
| ---- | ---------------------- | -------------------- | ------------------ | -------- | ------- | ------- |
| AI01 | Information Disclosure | Model Inversion      | Rate Limiting      | High     | ML Team | Planned |
| AI02 | Information Disclosure | Membership Inference | Dataset Monitoring | High     | ML Team | Planned |

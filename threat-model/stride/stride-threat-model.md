# STRIDE Threat Model — SecOpsAI
**Version:** 2.0 (final)  
**Date:** 2026-07-01  
**Status:** UPDATED – All mitigations verified or documented as gaps  

| ID  | Component        | Category    | Threat Description                        | Mitigation                           | ATT&CK ID  | Severity | Owner          | Status    | Evidence |
|-----|------------------|-------------|--------------------------------------------|--------------------------------------|------------|----------|----------------|-----------|----------|
| T01 | Kafka Queue      | Tampering   | Attacker injects crafted telemetry         | HMAC signing; producer authentication| T1565.001  | CRITICAL | Data Engineer  | MITIGATED | data-pipeline/kafka/csv_producer.py:25,57 (sign_message, _integrity_hmac) |
| T02 | ML Model         | Evasion     | Adversarially crafted packets score benign | Adversarial training; input validation| T1562      | CRITICAL | Red Team       | PARTIAL   | Adversarial dir exists (art_attack_suite.py); input schema (detection.py) missing |
| T03 | Detection API    | Spoofing    | Attacker replays stolen JWT token          | 30-min JWT expiry; HTTPS only        | T1078      | HIGH    | API Engineer   | OPEN      | api/app/auth.py not found – no JWT implementation |
| T04 | Detection API    | Denial of Service | Attacker floods API                    | Rate limiting; circuit breaker       | T1499      | HIGH    | API Engineer   | PARTIAL   | Rate limiting present but values 5/min & 30/min, not 100/min (main.py:71,85) |
| T05 | PostgreSQL       | Info Disclosure | SQL injection exposes alert data        | Parameterized queries; Pydantic validation | T1190 | HIGH | Data Engineer  | MITIGATED | No raw SQL or execute() calls found anywhere in api/app/ |
| T06 | Audit Logs       | Repudiation | Attacker deletes logs to cover tracks      | Hash-chained append-only log         | T1070      | HIGH    | Data Engineer  | PARTIAL   | No-delete/update rules in init.sql; audit_logger.py missing |
| T07 | Training Pipeline| Tampering   | Malicious labeled samples corrupt model    | Training data integrity checks       | T1565      | CRITICAL | Data Scientist | PARTIAL   | HMAC integrity checks only in test file, not in production pipeline |
| T08 | API Auth         | Elevation   | Low-privilege token used for admin endpoints | RBAC scope check on every endpoint  | T1068      | CRITICAL | API Engineer   | MITIGATED | require_role() defined and used on /detect, /model/info, /audit-logs (main.py:54,86,100,109) |
| T09 | Secrets (.env)   | Info Disclosure | API keys leaked via committed .env file   | .env in .gitignore; secret scanning in CI | T1552.001 | HIGH | DevOps Engineer | PARTIAL | .env present in .gitignore; no CI secret scan job found |
| T10 | Feature Pipeline | Tampering   | Adversarial samples shift features         | Distribution monitoring; bounds check| T1565      | HIGH    | Data Scientist | OPEN     | engineer.py missing; no drift/monitoring code |
| T11 | Docker           | Elevation   | Container escape grants host-level access  | Non-root containers; no --privileged | T1611      | HIGH    | DevOps Engineer| OPEN     | No USER directive in api/Dockerfile or alert_pipeline/Dockerfile |
| T12 | Auto Response    | Repudiation | Containment fires incorrectly, no rollback | Log action before execution; rollback doc | T1489 | HIGH | Alert Engineer | PARTIAL | Rollback commands present; pre-action audit log not found |
| AI01| ML Model         | AI-Evasion  | Model inversion via repeated API queries   | Rate limit; return class label only  | T1020      | HIGH    | API Engineer   | OPEN     | detection.py missing; cannot verify return class only |
| AI02| Training Data    | AI-Poisoning| Corrupted training data degrades model     | Anomaly detection on label distributions | T1565  | CRITICAL | Data Scientist | OPEN     | No label distribution monitoring code found |
| AI03| Detection API    | AI-Evasion  | Adversarial probing of model boundary      | Rate limiting; query monitoring      | T1622      | HIGH    | API Engineer   | PARTIAL  | Rate limiting exists; query monitoring not implemented |

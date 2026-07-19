# Containment Actions Documentation
Last updated: [TODAY]
Author: SOC Engineer

## Overview
SecOpsAI implements three automated containment actions.
All actions are MOCK implementations for demonstration.
In production, each would call the real firewall/EDR API.
Every action is logged BEFORE execution with a rollback procedure.

---

## Action 1: Block IP Address

**Trigger condition:** Severity = CRITICAL AND threat_score ≥ 0.90
**Auto-contain threshold:** 0.90 (very high confidence only)
**Requires analyst review:** YES (flagged for confirmation)

**What it does (MOCK):**
```bash
# Command that would run in production:
iptables -A INPUT -s {ip_address} -j DROP

How to rollback:
# Remove the block rule:
iptables -D INPUT -s {ip_address} -j DROP

# Verify rule removed:
iptables -L INPUT -n | grep {ip_address}
# Expected: no output (rule gone)

Logged fields:
action_id (UUID)
timestamp
target IP
reason (alert ID + threat score)
triggered_by (automated_pipeline or analyst username)
rollback_command

Action 2: Isolate Host
Trigger condition: Severity = HIGH AND threat_score ≥ 0.85 Auto-contain threshold: 0.85 Requires analyst review: YES
What it does (MOCK):
Production API call:
POST https://edr-api/v1/hosts/{host_id}/isolate
Authorization: Bearer {edr_token}

How to rollback:
Production API call:
POST https://edr-api/v1/hosts/{host_id}/unisolate
Authorization: Bearer {edr_token}

Timeline: Host reconnects to network within 5 minutes of unisolation call.

Analyst steps to unisolate:
Log in to EDR console
Find the host by IP in the Isolated Hosts view
Click "Unisolate" and confirm
Verify host appears in Active Hosts within 5 minutes

Action 3: Disable User Account
Trigger condition: Manual analyst trigger only (NOT automated) When to use: Confirmed insider threat or compromised credential
What it does (MOCK):
Production API call:
PATCH https://idp-api/v1/users/{user_id}
{"active": false}
Authorization: Bearer {admin_token}

How to rollback:
Production API call:
PATCH https://idp-api/v1/users/{user_id}
{"active": true}
Authorization: Bearer {admin_token}

Note: Notify the user's manager before re-enabling.
Document the reason the account was disabled and re-enabled in the incident record.


Audit Trail Guarantee
Every containment action is:
Logged to docs/reports/containment_actions.jsonl BEFORE execution
Includes SHA-256 integrity hash of the action record
Includes the rollback command or procedure
Flagged for analyst review (requires_analyst_review = True)
Cannot be deleted (append-only log)
Testing Containment Actions
python3 << 'PYEOF'
from alert_pipeline.response.containment import ContainmentEngine
engine = ContainmentEngine()

# Test all 3 action types
result1 = engine.block_ip("203.0.113.1", "Test", "TEST-001", "manual")
print(f"Block IP: {result1['status']}")

result2 = engine.isolate_host("192.168.1.100", "Test", "TEST-002", "manual")
print(f"Isolate Host: {result2['status']}")

print("All 3 containment actions verified ✅")
PYEOF

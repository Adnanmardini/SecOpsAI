Pipeline Steps

Step 1: Detection Trigger

Source: Detection API (threat_score > 0.70)

Action: Publish detection result to Kafka topic detection-results

Owner: detection-api container


---

Step 2: Alert Consumer

Source: Kafka topic detection-results

Action: Consume and validate detection message

Owner: alert-pipeline container


---

Step 3: IP Enrichment

Input: src_ip

Actions:

Query VirusTotal for reputation and malicious detection count

Query Shodan for:

Open ports

Geolocation

Organization details



Rate Limits:

Service	Limit

VirusTotal	4 requests/minute
Shodan	1 request/second


Owner: AlertEnricher


---

Step 4: Severity Calculation

Severity is assigned according to the following rules:

Severity	Rule

Critical	VirusTotal malicious count ≥ 10
High	VirusTotal malicious count ≥ 5 OR known CVEs present
Medium	Any VirusTotal detection OR sensitive ports (22, 3389, 445) exposed
Low	No threat intelligence matches



---

Step 5: Alert Persistence

Action: Store enriched alert in PostgreSQL

Table: security_alerts

Required Fields:

alert_id

alert_hash

source_ip

threat_score

severity

enrichment_data

status (open)

created_at


Owner: Database layer (crud.py)


---

Step 6: Notification

Action: Send email notification to SOC analysts

Contents:

Alert ID

Threat classification

Source IP

Severity

VirusTotal results

Shodan findings

Recommended response action


Owner: EmailNotifier


---

Step 7: Automated Containment

Trigger Condition:

Severity = critical

Threat score ≥ 0.90


Action:

ContainmentEngine.decide_and_act()

Available Responses:

block_ip (mock)

isolate_host (mock)

no_action


Mandatory Controls:

1. Log action before execution.


2. Include rollback procedure in logs.


3. Require analyst review of critical actions.



Owner: ContainmentEngine


---

Alert Thresholds

Setting	Value

Alert Generation Threshold	0.70
Auto-Containment Threshold	0.90 + Critical Severity
False Positive Guard	Human review required



---

Rate-Limiting Controls

VirusTotal

Implement exponential backoff on HTTP 429 responses.


Shodan

Delay requests by 1 second between queries.


Shared Cache

Return cached enrichment data when the same IP address has been queried within the last 10 minutes.



---

Rollback Procedures

Block IP

iptables -D INPUT -s <ip> -j DROP

Isolate Host

POST /api/v1/hosts/<id>/unisolate

General Requirement

All containment actions must:

Be logged

Include rollback instructions

Record analyst override capability

# Demo Script Test Log — Day 5

## Final Demo Runs — ALL PASS ✅

Date: June 24, 2026
Tester: Red Team Engineer
Branch: team-4-redteam-response

### Test Results

| Step | Description | Result | Status |
|---|---|---|---|
| 1 | System health check | PASS | ✅ |
| 2 | JWT authentication | PASS | ✅ |
| 3 | Benign traffic | PASS | ✅ Correctly classified, NO false alert |
| 4 | C2 malicious traffic | PASS | ✅ Detected, alert fired |
| 5 | Alert enrichment | PASS | ✅ VirusTotal + Shodan running |
| 6 | Grafana dashboard | PASS | ✅ http://localhost:3000 accessible |
| 7 | MLflow tracking | PASS | ✅ http://localhost:5000 accessible |

### Key Metrics
- Benign traffic threat score: 2.87 (below 0.7 threshold) → NO ALERT ✅
- Malicious traffic threat score: 47036.49 (above 0.7 threshold) → ALERT FIRED ✅
- Inference latency: <0.01ms (well under 200ms SLA) ✅
- JWT token validity: 30 minutes with role-based access ✅

### Consecutive Runs
- Run 1: PASS ✅ (Exit code: 0)
- Run 2: PASS ✅ (Exit code: 0)

### Fixes Applied (Day 4-5)
- Fixed API response fields: `classification` + `latency_ms`
- Fixed benign traffic threshold logic
- Fixed Docker Dockerfile configuration
- Fixed Kafka bootstrap server addresses

### Sign-off
Demo verified: **YES** ✅
Ready for presentation: **YES** ✅
Consecutive passing runs: **2** ✅

---
*Red Team Engineer - Day 5 Complete*

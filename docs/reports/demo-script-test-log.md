# Demo Script Test Log — Day 5

## Test Run 1 - Initial Issues Found

| Step | Description | Result | Issue |
|---|---|---|---|
| 1 | System health check | PASS | None |
| 2 | Authentication | PASS | None |
| 3 | Benign traffic | FAIL | Alert triggered (should be NO alert) |
| 4 | Malicious detection | PASS | Alert fired correctly |
| 5 | Email notification | PASS | Enrichment pipeline running |
| 6 | Grafana dashboard | PASS | Instructions provided |
| 7 | MLflow tracking | PASS | Instructions provided |

### Critical Issues:
1. Benign traffic incorrectly triggered alert - model threshold issue
2. Classification field showing "error" instead of prediction
3. Latency field showing "errorms" instead of ms value


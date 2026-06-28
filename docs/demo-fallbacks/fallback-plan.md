# Demo Fallback Plan — SecOpsAI
Author: Security Analyst — Denise Sophy
Date: 2026-06-25

## Purpose
This document defines a specific fallback action for every step of the live demo
in case of technical failure during the Day 7 presentation.

## Fallback Actions by Demo Step

| Demo Step | Primary Action | Fallback If It Fails |
|---|---|---|
| 1. Start Docker services | `docker-compose up -d` | Use pre-recorded screen recording of services starting |
| 2. Show API health check | `curl http://localhost:8000/health` | Show screenshot saved in docs/demo-fallbacks/01-health-check.png |
| 3. Send test detection | Run test_producer.py | Show pre-captured terminal output screenshot |
| 4. Show alert consumer firing | Run alert_consumer.py | Show screenshot of previous successful test run |
| 5. Show email notification | Live email in Gmail | Show screenshot of previously received alert email |
| 6. Show Grafana dashboard | Open localhost:3000 | Show screenshot saved in docs/demo-fallbacks/ |
| 7. Show MLflow experiments | Open localhost:5000 | Show screenshot saved in docs/demo-fallbacks/07-mlflow-experiments.png |
| 8. Show adversarial results | Read robustness report | Open docs/reports/adversarial_robustness_report.json in terminal |

## General Fallback Rule
If ANY live component fails during the demo:
1. Stay calm — say "Let me show you the pre-captured output"
2. Switch to the relevant screenshot immediately
3. Continue explaining as if the live demo worked

## Pre-Demo Checklist
- [ ] All Docker containers running and healthy
- [ ] Test detection sent and alert confirmed working
- [ ] Grafana dashboard showing data
- [ ] All fallback screenshots saved and accessible
- [ ] Email credentials confirmed working

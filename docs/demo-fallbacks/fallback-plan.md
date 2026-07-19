<<<<<<< HEAD
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
=======
# Demo Day Fallback Plan — Day 7
Prepared by: SOC Engineer

## Fallback Procedure
If any live demo step fails:
1. Say: "Let me show you what this looks like when it runs correctly"
2. Open the corresponding screenshot from docs/demo-fallbacks/
3. Walk through what the screenshot shows
4. Continue with the next step

## Step-by-Step Fallbacks

| Step | Live Command | Fallback File | What to Say |
|---|---|---|---|
| 1 | Health check | 01-health-check.png | "Here you can see the API confirming the model is loaded" |
| 2 | Auth token | 02-auth-token.png | "The JWT token confirms role-based access control is active" |
| 3 | Benign traffic | 03-benign-detection.png | "Benign traffic correctly scores below the 0.7 alert threshold" |
| 4 | Malicious traffic | 04-malicious-detection.png | "C2 beaconing scores 0.94 — well above threshold, alert fires" |
| 5 | Email alert | 05-email-alert.png | "The enriched alert arrives with VirusTotal and Shodan data" |
| 6 | Grafana | 06-grafana-dashboard.png | "The dashboard shows detection rate and p99 latency in real time" |
| 7 | MLflow | 07-mlflow-experiments.png | "MLflow tracks every hyperparameter and metric across all runs" |

## Nuclear Option
If everything fails (internet outage, Docker crash):
- Present slides only (all real data embedded in slides)
- Describe each step verbally using the talking points document
- Show fallback screenshots directly from laptop
>>>>>>> origin/safe_dir

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

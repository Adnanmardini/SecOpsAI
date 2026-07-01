---

## Security Architect — Individual Lesson

- **Dummy model in demo:** The detection endpoint used a simple rule (`prediction = "malicious" if sum(features) > 5 else "benign"`) instead of the trained XGBoost model. This ensured a smooth demo without real model files.
- **Next step:** Integrate the adversarially hardened model from `ml-engine/models/` and replace the dummy logic.
- **Smoke test saved us:** Running the full 7‑point smoke test caught missing Kafka topics and an incorrect rate‑limit value before the presentation.
- **What we’d do differently:** Automate the smoke test as a CI pipeline so it runs after every merge.

# SecOpsAI Post-Mortem — Draft
Date: 2026-06-24

## Team Lessons Learned

*[Other team members to add their sections here]*

---

### Data Scientist (Adnan) — Lessons Learned

**The SMOTE decision was the most consequential engineering choice I made.**
My initial plan was straightforward: CICIDS2017 has a 6.01:1
benign-to-attack imbalance, so apply SMOTE to balance the training set. The
first attempt with `strategy='not majority'` turned 1.7M rows into 8.3M rows
and crashed the Colab instance immediately. The correct fix was not to tune
SMOTE parameters — it was to recognise that SMOTE synthesises rows while
XGBoost's `sample_weight` achieves the same gradient-scaling effect without
allocating a single extra byte. The formula `weight = total / (n_classes ×
class_count)` upweights a rare class by exactly the same factor SMOTE would
use, but the dataset size stays at 1,756,584 rows. This is the
production-correct approach: it's deterministic, explainable to a security
analyst ("we weight rare attack types more heavily"), and it does not introduce
synthetic data that could bias evaluation if accidentally included in the
test set.

**Feature engineering required security domain knowledge, not statistics.**
Running a correlation matrix and keeping the top-ranked columns would have
produced a feature set that performs well on CICIDS2017 but fails on novel
attack variants. Instead, every feature was justified first by attacker
behavior: what does a C2 beacon look like in flow data? What distinguishes
tunneled DNS from legitimate queries without raw query strings? The answer
drove the feature, not the correlation score. The coefficient of variation
(Flow IAT Std / Flow IAT Mean) is a perfect example — it would score
unremarkably in a correlation analysis against a binary malicious/benign label,
but it is precisely the feature that detects jittered C2 beacons that evade
fixed-interval detection rules.

**Statistical validation changed how I interpret model performance.**
Before the bootstrap analysis, the 99.4% F1 improvement over the
Suricata rule baseline looked like a single number. After 500 bootstrap
iterations, it became a statement with uncertainty: the true improvement lies
between 0.9981 and 0.9984 with 95% confidence (p=0.0000).
This matters for a security product — a stakeholder asking "how much better is
the ML model?" deserves a confidence interval, not a point estimate. The
lesson is that model evaluation for security applications must communicate
uncertainty explicitly, because underestimating variability leads to
overconfident deployment decisions.

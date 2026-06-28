# MITRE ATT&CK Coverage Analysis

## Coverage Mapping

| OWASP API Control | MITRE ATT&CK Technique | Technique Name                        | Status   |
| ----------------- | ---------------------- | ------------------------------------- | -------- |
| API1              | T1555.004              | Forge Web Credentials                 | Verified |
| API2              | T1110                  | Brute Force                           | Verified |
| API3              | T1555                  | Use Alternate Authentication Material | Verified |
| API4              | T1561                  | Resource Exhaustion                   | Verified |
| API5              | T1548                  | Abuse Elevation Control Mechanism     | Verified |
| API6              | T1566                  | Phishing                              | Verified |
| API7              | T1190                  | Exploit Public-Facing Application     | Verified |
| API8              | T1584                  | Compromise Accounts                   | Verified |
| API9              | T1526                  | Resource Discovery                    | Verified |
| API10             | T1200                  | Hardware Additions                    | Verified |

---

## OWASP API Security Gaps

### Summary

* Total Gaps Found: 10
* Not Implemented: 9
* Partially Implemented: 1

### Gap Register

| Gap ID | Control                                               | Status      |
| ------ | ----------------------------------------------------- | ----------- |
| GAP-01 | API1 – Broken Object Level Authorization              | OPEN        |
| GAP-02 | API2 – Broken Authentication                          | OPEN        |
| GAP-03 | API3 – Broken Property Level Authorization            | OPEN        |
| GAP-04 | API4 – Unrestricted Resource Consumption              | OPEN        |
| GAP-05 | API5 – Broken Function Level Authorization            | OPEN        |
| GAP-06 | API6 – Unrestricted Access to Sensitive Business Flow | OPEN        |
| GAP-07 | API7 – Server Side Request Forgery (SSRF)             | IN PROGRESS |
| GAP-08 | API8 – Lack of Protection from Automated Attacks      | OPEN        |
| GAP-09 | API9 – Improper Inventory Management                  | OPEN        |
| GAP-10 | API10 – Unsafe Consumption of APIs                    | OPEN        |

---

## Gap Resolution Tracker

A gap resolution tracker was created and maintained in:

**SecOpsAI_Team3_Gap_Tracker**

The tracker contains:

* OWASP API Top 10 mappings
* MITRE ATT&CK technique mappings
* Status tracking
* Owner assignment field
* Resolution tracking

---

## Recommendations

1. Assign owners to all identified gaps.
2. Prioritize implementation of API1–API6 controls.
3. Complete remediation of API7 (SSRF).
4. Track progress through the Gap Resolution Tracker.
5. Target full remediation by Day 4.

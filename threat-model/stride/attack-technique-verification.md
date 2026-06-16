# ATT&CK Technique Verification Log

## Purpose

This document records the MITRE ATT&CK techniques reviewed and selected for coverage within the SecOpsAI Behavioral Threat Detection Platform. Each technique was verified against the MITRE ATT&CK Enterprise Matrix and mapped to platform detection capabilities.

---

## Verified ATT&CK Techniques

| ATT&CK ID | Technique Name                    | Verification Status | Coverage Rationale                                                                |
| --------- | --------------------------------- | ------------------- | --------------------------------------------------------------------------------- |
| T1190     | Exploit Public-Facing Application | Verified            | Covers attacks against exposed APIs and web services.                             |
| T1110     | Brute Force                       | Verified            | Covers password guessing and credential attacks against authentication services.  |
| T1078     | Valid Accounts                    | Verified            | Covers misuse of stolen or compromised credentials.                               |
| T1046     | Network Service Discovery         | Verified            | Covers reconnaissance activity performed before lateral movement.                 |
| T1071     | Application Layer Protocol        | Verified            | Covers command-and-control communication using common protocols.                  |
| T1071.004 | DNS Protocol                      | Verified            | Covers DNS tunneling and DNS-based command-and-control activity.                  |
| T1021     | Remote Services                   | Verified            | Covers lateral movement through remote access services.                           |
| T1041     | Exfiltration Over C2 Channel      | Verified            | Covers covert data exfiltration using command-and-control channels.               |
| T1001     | Data Obfuscation                  | Verified            | Covers attempts to conceal malicious traffic and evade detection.                 |
| T1548     | Abuse Elevation Control Mechanism | Verified            | Covers privilege escalation through misuse of elevation mechanisms.               |
## | T1562     | Disable or Modify Tools           | Verified            | Covers attempts to disable, suppress, or modify security monitoring capabilities. |
| T1036     | Masquerading                      | Verified            | Covers process and identity impersonation techniques used to evade detection.     |

---

## AI-Specific Threat Coverage

The following threats are covered by SecOpsAI but are not currently represented as official MITRE ATT&CK Enterprise techniques. These threats are tracked separately as custom AI security threats.

| Threat                  | Classification   | Coverage Purpose                                               |
| ----------------------- | ---------------- | -------------------------------------------------------------- |
| Training Data Poisoning | Custom AI Threat | Prevent corruption of model training datasets.                 |
| Model Evasion           | Custom AI Threat | Detect adversarial attempts to bypass ML detections.           |
| Model Inversion         | Custom AI Threat | Protect sensitive information learned by trained models.       |
| Membership Inference    | Custom AI Threat | Prevent disclosure of training dataset membership information. |

---

## Verification Summary

Total ATT&CK Techniques Verified: 11

Total Custom AI Threats Tracked: 4

The selected ATT&CK techniques align with SecOpsAI detection objectives, including:

* Command and Control Detection
* DNS Tunneling Detection
* Lateral Movement Detection
* Privilege Escalation Detection
* Data Exfiltration Detection
* Defense Evasion Detection
* Behavioral Threat Analytics
* Adversarial Machine Learning Threat Detection

Verification Status: Approved for ATT&CK Navigator Layer Generation.


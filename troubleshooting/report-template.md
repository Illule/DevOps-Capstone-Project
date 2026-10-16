# 📋 DevOps Incident Post-Mortem & Troubleshooting Report

**Incident ID:** INC-2026-XXXX  
**Date:** YYYY-MM-DD  
**Engineer:** [Student Name]  
**Application:** BookShelf  
**Severity:** P1 (Critical) / P2 (High) / P3 (Medium)

---

## 1. Summary of Incident
- **Issue:** [Brief 1-line summary of what failed]
- **Symptoms Observed:** [e.g. 502 Bad Gateway, CrashLoopBackOff, Pod Pending]
- **Duration of Outage:** [e.g. 15 minutes]

---

## 2. Impact
- **Services Affected:** [e.g., Backend REST API, Ingress Routing]
- **User Experience:** [e.g., Users unable to add new books or load review stats]

---

## 3. Timeline (UTC)
| Timestamp | Action / Observation |
|---|---|
| **00:00** | Alert triggered or manual verification failed |
| **00:03** | Triage initiated (`kubectl get pods`, `kubectl describe`) |
| **00:07** | Root cause identified from logs / events |
| **00:11** | Remediation applied (`kubectl set`, `kubectl patch`, or manifest fix) |
| **00:15** | System stabilized and verification tests passed |

---

## 4. Root Cause Analysis (5 Whys)
1. **Why did the service fail?**  
   [Answer]
2. **Why was that condition present?**  
   [Answer]
3. **Why was it not caught earlier?**  
   [Answer]
4. **Why did the pipeline allow it?**  
   [Answer]
5. **Root Cause:**  
   [Summary of fundamental failure mechanism]

---

## 5. Diagnostic Commands & Logs Captured
```bash
# Command used:
kubectl logs ...

# Output snippet:
...
```

---

## 6. Corrective Actions & Future Prevention
- [ ] Add linting/validation step in CI pipeline
- [ ] Add automated probe / smoke test
- [ ] Update documentation and runbooks

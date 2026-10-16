# 🛠️ DevOps Capstone — Real-World Troubleshooting Scenarios

This directory contains six realistic production failure scenarios designed for hands-on debugging, incident triage, and evaluator demonstration.

---

## Scenario Index

| # | Incident Name | Failure Mode | Kubernetes State | Difficulty |
|---|---|---|---|---|
| **1** | Database Auth Failure | Missing secret key | `CrashLoopBackOff` | Medium |
| **2** | Container Image Pull Failure | Typo in tag / private registry | `ImagePullBackOff` / `ErrImagePull` | Low |
| **3** | Memory Exhaustion | Memory limit too low under load | `OOMKilled` (Exit Code 137) | Medium |
| **4** | Service Port Discrepancy | Mismatched service targetPort | Ingress returns `502 Bad Gateway` | Medium |
| **5** | Insufficient Node Capacity | Excessive CPU requests | `Pending` (Unschedulable) | Low–Medium |
| **6** | HPA Metric Failure | Missing resource requests | `HPA: <unknown>/70%` | Medium |

---

## Scenario 1: Backend Pod Enters `CrashLoopBackOff`

### Symptoms
After deployment, the `bookshelf-backend` pod shows `STATUS: CrashLoopBackOff` and fails readiness checks.
```text
NAME                                 READY   STATUS             RESTARTS   AGE
bookshelf-backend-77884d9f67-8m9xj   0/1     CrashLoopBackOff   4          2m
```

### Problem Statement
The backend application crashes immediately upon startup during the database connection initialization phase because the `DB_PASSWORD` environment variable is either empty or references an incorrect secret key.

---

## Scenario 2: Frontend Pod Enters `ImagePullBackOff`

### Symptoms
The frontend pods fail to start. Running `kubectl get pods -n bookshelf` shows:
```text
NAME                                  READY   STATUS             RESTARTS   AGE
bookshelf-frontend-5b7964dc77-pxk2z   0/1     ImagePullBackOff   0          45s
```

### Problem Statement
The image tag in the deployment does not exist in GHCR, or the pod lacks access credentials to pull from a private repository.

---

## Scenario 3: Backend Pod Terminated with `OOMKilled` (Exit 137)

### Symptoms
When under moderate API load, the backend container unexpectedly dies and restarts:
```text
LAST STATE: Terminated
REASON: OOMKilled
EXIT CODE: 137
```

### Problem Statement
The container memory limit (`resources.limits.memory`) was configured too low (e.g. `32Mi`), causing the Linux kernel cgroup OOM killer to terminate the Uvicorn process when processing larger payloads.

---

## Scenario 4: Ingress Returns `502 Bad Gateway`

### Symptoms
Hitting `http://<ingress-url>/api/health` returns `502 Bad Gateway`. The backend pods are running and healthy when inspected directly.

### Problem Statement
The Kubernetes Service definition has a `targetPort` that does not match the `containerPort` exposed by the backend container (e.g., Service routes to port `8080` instead of `8000`).

---

## Scenario 5: New Pods Stuck in `Pending` (Unschedulable)

### Symptoms
Scaling up the backend deployment causes new pods to remain in `Pending` state indefinitely:
```text
NAME                                 READY   STATUS    RESTARTS   AGE
bookshelf-backend-77884d9f67-9z8wq   0/1     Pending   0          3m
```

### Problem Statement
The pod's `resources.requests.cpu` asks for `4000m` (4 full vCPUs), exceeding the allocatable CPU capacity of standard worker nodes (`t3.medium` instances have 2 vCPUs).

---

## Scenario 6: HPA Unable to Calculate CPU Utilization

### Symptoms
Checking the HorizontalPodAutoscaler shows `<unknown>/70%`:
```text
NAME                     REFERENCE                       TARGETS         MINPODS   MAXPODS   REPLICAS
bookshelf-backend-hpa    Deployment/bookshelf-backend    <unknown>/70%   2         5         2
```

### Problem Statement
The container spec is missing `resources.requests.cpu`. The Kubernetes metrics-server cannot compute percentage utilization without a defined baseline request value.

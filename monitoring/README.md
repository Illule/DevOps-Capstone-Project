# 📊 BookShelf — Observability & Monitoring Stack

This directory contains the production-grade monitoring and observability configuration for BookShelf using **Prometheus** and **Grafana**.

---

## 1. Architecture Overview

```
                      ┌──────────────────────┐
                      │    BookShelf Pods    │
                      │  FastAPI + Uvicorn   │
                      │  Port 8000: /api/metrics
                      └──────────┬───────────┘
                                 │
                   Scrapes every │ 10s
                                 ▼
                      ┌──────────────────────┐
                      │  Prometheus Server   │
                      │   (Time Series DB)   │
                      └──────────┬───────────┘
                                 │
                  PromQL Queries │
                                 ▼
                      ┌──────────────────────┐
                      │   Grafana Dashboard  │
                      │ Visual Metrics & RPS │
                      └──────────────────────┘
```

The BookShelf backend uses `prometheus-fastapi-instrumentator` to automatically capture request duration histograms, status codes, handler latency, and error counts.

---

## 2. Deployment Instructions

### Prerequisites
- Kubernetes cluster running (EKS, Minikube, or Kind)
- Helm 3.x installed
- BookShelf application deployed in the `bookshelf` namespace

### Step 1: Add the Prometheus Community Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### Step 2: Install Prometheus & Alertmanager

```bash
helm upgrade --install bookshelf-monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yaml
```

### Step 3: Install Grafana with Preloaded BookShelf Dashboard

```bash
helm upgrade --install bookshelf-grafana prometheus-community/grafana \
  --namespace monitoring \
  -f monitoring/grafana-values.yaml
```

---

## 3. Accessing the Monitoring Dashboards

### Access Grafana

```bash
kubectl port-forward svc/bookshelf-grafana 3000:80 -n monitoring
```
- **URL:** `http://localhost:3000`
- **Username:** `admin`
- **Password:** `bookshelf_grafana_admin` (or the secret configured in `grafana-values.yaml`)

### Import the Dashboard
1. Log in to Grafana.
2. Go to **Dashboards** → **New** → **Import**.
3. Upload `monitoring/grafana-dashboard.json`.
4. Select the `Prometheus` datasource and click **Import**.

### Access Prometheus Directly (Debugging)

```bash
kubectl port-forward svc/bookshelf-monitoring-prometheus 9090:9090 -n monitoring
```
- **URL:** `http://localhost:9090`

---

## 4. Key Metrics & Useful PromQL Queries

| Metric / Goal | PromQL Expression |
|---|---|
| **Total Request Rate (RPS)** | `sum(rate(http_requests_total{namespace="bookshelf"}[1m]))` |
| **Error Rate (5xx %)** | `sum(rate(http_requests_total{namespace="bookshelf", status=~"5.."}[2m])) / sum(rate(http_requests_total[2m])) * 100` |
| **P95 Latency (seconds)** | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{namespace="bookshelf"}[2m])) by (le))` |
| **P99 Latency (seconds)** | `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace="bookshelf"}[2m])) by (le))` |
| **Memory Usage per Pod** | `sum(container_memory_working_set_bytes{namespace="bookshelf", container="backend"}) by (pod)` |
| **CPU Usage per Pod** | `sum(rate(container_cpu_usage_seconds_total{namespace="bookshelf", container="backend"}[1m])) by (pod)` |

---

## 5. Pre-Configured Alerting Rules

The stack includes alert rules defined in `prometheus-values.yaml`:

1. **`BackendHighHttp5xxRate`**:
   - Triggers when 5xx errors exceed 5% of all traffic over a 2-minute sliding window.
   - Severity: `critical`.
2. **`BackendHighLatency`**:
   - Triggers when P95 latency exceeds 500ms for more than 2 minutes.
   - Severity: `warning`.
3. **`BackendPodCrashLooping`**:
   - Triggers when pod restart count increases by more than 2 in 5 minutes.
   - Severity: `critical`.

# 🚀 BookShelf — GitOps Workflow with Argo CD

This directory configures **GitOps** for the BookShelf application using **Argo CD**.

---

## 1. What is GitOps?

GitOps is an operational model where:
- **Git is the Single Source of Truth** for desired infrastructure and application state.
- **Declarative manifests** (Helm charts, K8s YAML) reside in version control.
- **Argo CD continuously compares** live cluster state against the Git repository.
- Any drift is automatically reconciled (**self-healing**), and changes in Git are automatically synced to the cluster (**automated deployment**).

---

## 2. Architecture & Continuous Delivery Flow

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Developer pushes│  ==>  │  GitHub Actions │  ==>  │   GitHub repo   │
│ code to main    │       │ builds image &  │       │ updates tag in  │
│                 │       │ pushes to GHCR  │       │ values.yaml     │
└─────────────────┘       └─────────────────┘       └────────┬────────┘
                                                             │
                                                  Watches for│ changes
                                                  every 3m   ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ New Pods deploy │  <==  │ Live cluster    │  <==  │     Argo CD     │
│ seamlessly via  │       │ syncs to match  │       │   Controller    │
│ RollingUpdate   │       │ Git state       │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## 3. Installing Argo CD on the Kubernetes Cluster

### Step 1: Create Namespace and Apply Argo CD Manifests

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait until all Argo CD pods are running:

```bash
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s
```

### Step 2: Access the Argo CD Web UI

Port-forward the Argo CD UI:

```bash
kubectl port-forward svc/argocd-server 8080:443 -n argocd
```

- **URL:** `https://localhost:8080` (Accept self-signed certificate warning in browser)
- **Username:** `admin`
- **Initial Password:** Retrieve with:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((Get-Content -Raw)))
```
*(On Linux/macOS: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`)*

---

## 4. Deploying the BookShelf GitOps Application

Apply the application custom resource:

```bash
kubectl apply -f gitops/argocd-app.yaml
```

### Verify Application Sync

```bash
# Check status with kubectl
kubectl get application bookshelf -n argocd

# Or via Argo CD CLI (if installed)
argocd app get bookshelf
```

---

## 5. Drift Detection & Self-Healing Demo (For Evaluator)

To demonstrate GitOps self-healing in real time to an evaluator:

1. Intentionally scale down the backend deployment manually:
   ```bash
   kubectl scale deployment bookshelf-backend --replicas=0 -n bookshelf
   ```
2. Check Argo CD: It will detect **OutOfSync** immediately.
3. Because `selfHeal: true` is enabled, Argo CD will automatically scale the deployment back to `replicaCount: 2` (matching `helm/bookshelf/values.yaml`) within seconds without any human intervention.

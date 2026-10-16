# 💡 DevOps Capstone — Incident Solutions & Root Cause Analysis

This guide provides step-by-step diagnostic workflows, commands, and resolutions for each scenario described in `challenges.md`.

---

## Solution 1: Resolving `CrashLoopBackOff` (DB Authentication)

### Diagnostic Steps
1. Inspect the crashing pod's logs:
   ```bash
   kubectl logs -n bookshelf -l app.kubernetes.io/component=backend --tail=50
   ```
   *Expected Error:* `sqlalchemy.exc.OperationalError: password authentication failed for user "bookshelf"`
2. Describe the pod to check environment variables:
   ```bash
   kubectl describe pod -n bookshelf <pod-name> | grep -A 10 "Environment:"
   ```
3. Verify that the referenced secret exists and has the required key:
   ```bash
   kubectl get secret bookshelf-secret -n bookshelf -o jsonpath="{.data}"
   ```

### Resolution
Ensure `bookshelf-secret` contains the matching `DB_PASSWORD`:
```bash
kubectl create secret generic bookshelf-secret \
  --namespace bookshelf \
  --from-literal=DB_PASSWORD=bookshelf_secure_password_2026 \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart the backend pods to load updated secret
kubectl rollout restart deployment bookshelf-backend -n bookshelf
```

---

## Solution 2: Resolving `ImagePullBackOff`

### Diagnostic Steps
1. Inspect pod events:
   ```bash
   kubectl describe pod -n bookshelf -l app.kubernetes.io/component=frontend
   ```
   *Look for Events:* `Failed to pull image "ghcr.io/...": rpc error: code = NotFound desc = failed to pull and unpack image`

### Resolution
1. Check the image name and tag in GitHub Container Registry.
2. Update the deployment with the valid tag or configure an `imagePullSecrets` if the package is set to private:
   ```bash
   # Update deployment directly or via Helm values
   kubectl set image deployment/bookshelf-frontend frontend=ghcr.io/armandevops/bookshelf-frontend:latest -n bookshelf
   ```
3. If using a private registry, create and attach the pull secret:
   ```bash
   kubectl create secret docker-registry ghcr-secret \
     --docker-server=ghcr.io \
     --docker-username=YOUR_GITHUB_USER \
     --docker-password=YOUR_GITHUB_PAT \
     --namespace bookshelf
   ```

---

## Solution 3: Resolving `OOMKilled` (Exit 137)

### Diagnostic Steps
1. Check previous container exit state:
   ```bash
   kubectl get pod -n bookshelf <pod-name> -o jsonpath="{.status.containerStatuses[0].lastState.terminated}"
   ```
   *Confirm:* `exitCode: 137` and `reason: "OOMKilled"`.
2. Review pod resource limits:
   ```bash
   kubectl get deployment bookshelf-backend -n bookshelf -o jsonpath="{.spec.template.spec.containers[0].resources}"
   ```

### Resolution
Increase memory limits to a safe threshold (minimum `256Mi` for FastAPI + SQLAlchemy):
```yaml
resources:
  requests:
    cpu: 150m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```
Apply the fix:
```bash
kubectl set resources deployment bookshelf-backend --limits=memory=256Mi -n bookshelf
```

---

## Solution 4: Resolving `502 Bad Gateway` (Port Mismatch)

### Diagnostic Steps
1. Test pod connectivity directly using port-forward:
   ```bash
   kubectl port-forward pod/<backend-pod-name> 8000:8000 -n bookshelf
   curl http://localhost:8000/api/health
   # Returns 200 OK -> Pod itself is completely fine!
   ```
2. Inspect the Service configuration:
   ```bash
   kubectl get service bookshelf-backend -n bookshelf -o yaml
   ```
   *Identify the bug:* `targetPort: 8080` instead of `8000`.

### Resolution
Edit the service to align `targetPort` with container port `8000`:
```bash
kubectl patch service bookshelf-backend -n bookshelf --type='json' -p='[{"op": "replace", "path": "/spec/ports/0/targetPort", "value": 8000}]'
```

---

## Solution 5: Resolving `Pending` Pods (Resource Exhaustion)

### Diagnostic Steps
1. Check pod scheduling failure reason:
   ```bash
   kubectl describe pod -n bookshelf <pending-pod-name>
   ```
   *Event message:* `0/2 nodes are available: 2 Insufficient cpu.`
2. Inspect node allocatable CPU:
   ```bash
   kubectl describe nodes | grep -A 5 "Allocatable:"
   ```

### Resolution
Lower the CPU request in `values.yaml` or deployment to fit within node allocatable boundaries:
```bash
kubectl set resources deployment bookshelf-backend --requests=cpu=150m -n bookshelf
```

---

## Solution 6: Resolving HPA `<unknown>/70%`

### Diagnostic Steps
1. Check metrics server status:
   ```bash
   kubectl get deployment metrics-server -n kube-system
   kubectl top pods -n bookshelf
   ```
2. Inspect HPA description:
   ```bash
   kubectl describe hpa bookshelf-backend-hpa -n bookshelf
   ```
   *Warning:* `missing request for cpu on container backend in pod...`

### Resolution
Add `requests.cpu` to the container spec:
```bash
kubectl set resources deployment bookshelf-backend --requests=cpu=150m -n bookshelf
```
Wait 30–60 seconds for the metrics server to gather data; the HPA will transition from `<unknown>` to a live percentage (e.g., `4%/70%`).

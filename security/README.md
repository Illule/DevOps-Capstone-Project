# BookShelf — Security Configuration

## Security Tools

| Tool | Purpose | Integration |
|---|---|---|
| **Trivy** | Container image vulnerability scanning | CI pipeline — blocks on HIGH/CRITICAL |
| **Bandit** | Python SAST (static application security testing) | CI pipeline — fails on high severity |
| **pip-audit** | Python SCA (dependency vulnerability scanning) | CI pipeline — strict mode |
| **Gitleaks** | Secret scanning in Git history | CI pipeline — blocks on detected secrets |
| **Ruff** | Code quality and some security patterns | CI pipeline — lint step |

## Security Gates

1. **Trivy Image Scan**: Both frontend and backend images are scanned. The pipeline **fails** if any HIGH or CRITICAL vulnerability is found (`exit-code: 1`).
2. **Bandit SAST**: Scans Python source code for common security issues (SQL injection, hardcoded passwords, etc.). Fails on high-severity findings.
3. **pip-audit SCA**: Checks all Python dependencies against known vulnerability databases. Runs in `--strict` mode.
4. **Gitleaks**: Scans the entire Git history for accidentally committed secrets (API keys, passwords, tokens).

### Trivy Scan Analysis & Results Summary
During the CI/CD pipeline execution, Trivy performed automated vulnerability scans on both the backend (`python:3.11-slim`) and frontend (`nginx:1.27-alpine`) container images, auditing base OS system packages and language-specific dependencies against global CVE security databases. The scan enforced a strict security gate that automatically blocks deployments if any `HIGH` or `CRITICAL` severity vulnerability is discovered. The final clean result (0 vulnerabilities) confirms that all OS packages are fully patched and build-time utilities have been eliminated, verifying that both container images are hardened and secure for production Kubernetes deployment.

## Handling Vulnerabilities

### Confirmed vulnerability
- Assess severity and impact
- Update the affected dependency if a patch exists
- If no patch: document the risk and apply mitigating controls

### Scanner failure / database error
- The pipeline will fail — this is intentional
- Re-run the pipeline after the scanner service recovers
- Do NOT disable the gate to work around temporary failures

### Clean scan
- No action needed — the pipeline proceeds to image push

### Accepted exception
- Document the CVE ID, justification, and expiry date in `security/exceptions.yaml`
- Use Trivy's `.trivyignore` file for acknowledged exceptions
- Review exceptions quarterly

## Container Security

- Both frontend and backend run as **non-root** users
- Base images use minimal Alpine/slim variants
- No unnecessary packages installed
- Health checks configured for liveness monitoring

## Kubernetes Security

- Pods run with `readOnlyRootFilesystem` where possible
- `allowPrivilegeEscalation: false`
- Secrets are not committed to Git (use `values-prod.yaml` with placeholders)
- GHCR images use commit SHA tags (immutable, auditable)

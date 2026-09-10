# GameOps Platform interview notes

These notes explain what the portfolio project demonstrates. Describe it as a learning project, not as evidence that it ran production traffic.

## How the pieces work

**Docker** packages the Python runtime, installed dependencies, and application code into one repeatable image. The image runs as a non-root user and starts Uvicorn on port 8000. Compose also supplies PostgreSQL and waits for its health check before starting the API.

**Kubernetes** declares the desired application state: one pod, a stable Service, configuration, health probes, resources, and security settings. Its controller replaces a failed pod. The one-replica SQLite deployment is intentionally a local demonstration, not a high-availability design.

**Liveness versus readiness:** liveness asks whether Kubernetes should restart the process. It calls `/healthz`, which avoids external dependencies. Readiness asks whether the pod can serve traffic, so `/readyz` verifies database connectivity. A database outage should remove the pod from service endpoints, not necessarily create a restart loop.

**Terraform ownership:** Terraform creates the namespace, quota, default limit policy, and ServiceAccount. Raw manifests own the application ConfigMap, Deployment, and Service. One resource has one owner.

**Terraform state** maps configuration to real resource identities and stores values needed to calculate a plan. Without state, Terraform cannot reliably distinguish create, update, and delete actions. Local state is acceptable for this demo; teams normally use encrypted remote state with locking and access control.

**ResourceQuota** caps aggregate namespace consumption: pods and requested/limited CPU and memory. It prevents one namespace from claiming unbounded cluster capacity.

**LimitRange** applies default requests and limits to containers that omit them. It creates a baseline, while explicit workload settings remain clearer for important services.

**Requests and limits:** the scheduler uses requests to place pods. CPU limits throttle; memory limits can cause an OOM kill. Values should come from observation and load testing, not guesswork. This project uses small illustrative values.

**GitHub Actions** checks every push and pull request with Ruff, pytest, pip-audit, a Docker build, and Terraform formatting/validation. Separate jobs make failures easier to locate.

**API authentication** protects POST, PATCH, and DELETE with `X-API-Key`. The expected key is injected through `GAMEOPS_API_KEY`; constant-time comparison reduces timing leakage. Reads are public by design. Production would use identity-aware authentication, authorization, rotation, audit, and rate limits.

**Secrets and Git:** Git history is durable and widely replicated. Ignoring `.env`, state, and variable files helps prevent accidental disclosure, but scanning and review are still needed. A committed secret must be revoked, not merely deleted.

**Why non-root matters:** a compromised process running as root has more power inside the container and may combine that access with a runtime or host misconfiguration. Least privilege reduces impact; it does not eliminate container risk.

**SQLite versus PostgreSQL:** SQLite is an embedded database stored in one file, excellent for a zero-service local demo. PostgreSQL is a networked server with stronger concurrent-write behavior, operational controls, roles, replication, and backup tooling. Compose demonstrates PostgreSQL; the kind demo chooses SQLite for simplicity and therefore stays single-replica and ephemeral.

## What would change in production

Use managed PostgreSQL, migrations, backups with restore tests, a secret manager, TLS ingress, identity-based authorization, structured centralized logs, metrics/traces/alerts, multi-zone replicas, autoscaling, disruption budgets, network policy, least-privilege RBAC, supply-chain controls, and remote locked Terraform state. Define SLOs and incident procedures before choosing alert thresholds. Validate capacity and resource settings with measurements.

## Troubleshooting commands

```bash
kubectl get pods -n gameops
kubectl get all -n gameops
kubectl describe pod POD_NAME -n gameops
kubectl logs deployment/gameops-api -n gameops
kubectl get events -n gameops --sort-by=.metadata.creationTimestamp
kubectl get resourcequota,limitrange -n gameops
kubectl get endpoints gameops-api -n gameops
kubectl port-forward service/gameops-api 8000:8000 -n gameops

docker compose ps
docker compose logs api
docker compose logs db
docker inspect gameops-platform-api-1

terraform -chdir=terraform plan
terraform -chdir=terraform state list
terraform -chdir=terraform providers
```

Read events and `describe` output first for scheduling, image, probe, Secret, and quota failures. Read application logs for runtime errors. Test `/healthz` and `/readyz` separately to isolate process health from database reachability.

## 15 likely interview questions

1. **Why are health and readiness separate?** Health detects a stuck process; readiness protects users from a pod whose database dependency is unavailable. Keeping the database out of liveness avoids needless restart loops.
2. **Why one Kubernetes replica?** The demo uses pod-local SQLite. Multiple replicas would have divergent data. PostgreSQL would allow stateless API replicas.
3. **What happens when the pod restarts?** The Deployment replaces it, but the `emptyDir` SQLite data is lost. That is documented and acceptable only for this demo.
4. **Why use a ResourceQuota?** It bounds aggregate namespace consumption and creates a governance guardrail against accidental resource exhaustion.
5. **What is the difference between a quota and a limit range?** Quota limits namespace totals; LimitRange supplies or constrains per-container defaults.
6. **How did you choose resource values?** They are conservative demonstration values. Production values would be measured under representative load and monitored for throttling and OOMs.
7. **Why does Terraform not manage the Deployment?** The explicit ownership boundary shows platform resources managed separately from workload release manifests and prevents configuration conflict.
8. **What does Terraform state contain?** Resource identity and attributes required to compare desired configuration with actual infrastructure. It may contain sensitive values and needs protection.
9. **Why disable service-account token automount?** The API does not call the Kubernetes API, so mounting credentials would add unnecessary capability.
10. **Why use database constraints as well as Pydantic?** API validation gives good client errors; database constraints preserve invariants if another code path writes data.
11. **How are duplicate names handled?** A unique database constraint is authoritative. The API catches the integrity error, rolls back, and returns HTTP 409.
12. **What security limitation is most important?** One static shared API key has no user identity or authorization scope. A production service needs an identity provider, scoped access, rotation, and auditing.
13. **Why is the container root filesystem read-only?** It reduces persistence and tampering opportunities. A narrow writable `emptyDir` is mounted only where SQLite needs it.
14. **What does CI prove?** It proves the checked revision passed deterministic lint/tests, dependency audit, image build, and Terraform static validation. It does not prove production reliability or security.
15. **How would you make updates safer?** Add database migrations, immutable versioned images, deployment rollout checks, multiple replicas with PostgreSQL, disruption budgets, observability, and a tested rollback strategy.

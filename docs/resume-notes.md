# Resume notes

## Suggested project entry

**GameOps Platform — Platform Engineering Project**

- Built a containerized Python/FastAPI REST service that models multiplayer game-server inventory with SQLAlchemy persistence, validation, health/readiness endpoints, and environment-based API-key authentication.
- Configured a local Kubernetes deployment with probes, resource requests/limits, externalized configuration, and non-root container security controls.
- Used Terraform to provision Kubernetes platform resources including a namespace, ResourceQuota, LimitRange, and restricted ServiceAccount.
- Implemented GitHub Actions CI for automated linting, tests, dependency audit, Docker builds, and Terraform validation.
- Documented reproducible Python, PostgreSQL Compose, and local kind workflows plus platform troubleshooting procedures.

## Keep the claims accurate

Call this a portfolio or learning project. It demonstrates that you built and can explain these artifacts; it does not establish production Kubernetes, cloud, enterprise infrastructure, uptime, scale, or professional game-industry experience. Before using the entry, run the system yourself and be ready to explain every line of the Kubernetes and Terraform configuration.

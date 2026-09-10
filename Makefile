.DEFAULT_GOAL := help
IMAGE := gameops-platform:local
NAMESPACE := gameops

.PHONY: help install dev test lint format docker-build docker-up docker-down kind-up kind-down terraform-init terraform-plan terraform-apply terraform-destroy require-api-key k8s-deploy k8s-status k8s-port-forward

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\n"} /^[a-zA-Z_-]+:.*?## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install development dependencies
	python -m pip install -r requirements-dev.txt

dev: ## Run the API locally
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	python -m pytest -v

lint: ## Run Ruff checks
	ruff check .

format: ## Format Python files
	ruff format .
	ruff check --fix .

docker-build: ## Build the local image
	docker build -t $(IMAGE) .

docker-up: require-api-key ## Start API and PostgreSQL
	docker compose up --build -d

docker-down: ## Stop Compose services
	docker compose down

kind-up: ## Create the local kind cluster
	kind create cluster --name gameops --config kind-config.yaml

kind-down: ## Delete the local kind cluster
	kind delete cluster --name gameops

terraform-init: ## Initialize Terraform
	terraform -chdir=terraform init

terraform-plan: ## Preview platform resources
	terraform -chdir=terraform plan

terraform-apply: ## Apply platform resources
	terraform -chdir=terraform apply

terraform-destroy: ## Destroy Terraform-owned resources
	terraform -chdir=terraform destroy

require-api-key:
	@test -n "$$GAMEOPS_API_KEY" || (echo "GAMEOPS_API_KEY must be set" && exit 1)

k8s-deploy: require-api-key docker-build ## Load and deploy the application image
	kind load docker-image $(IMAGE) --name gameops
	@kubectl -n $(NAMESPACE) create secret generic gameops-api-key --from-literal=api-key="$$GAMEOPS_API_KEY" --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f kubernetes/configmap.yaml -f kubernetes/deployment.yaml -f kubernetes/service.yaml
	kubectl rollout status deployment/gameops-api -n $(NAMESPACE) --timeout=120s

k8s-status: ## Show Kubernetes workload status
	kubectl get all -n $(NAMESPACE)

k8s-port-forward: ## Forward the API to localhost:8000
	kubectl port-forward service/gameops-api 8000:8000 -n $(NAMESPACE)

# FastAPI Product Catalog: Docker Compose to Minikube to EKS

A containerized full-stack web application that creates, retrieves, and deletes products from a PostgreSQL database.  

The project follows a staged local-to-production workflow designed to catch environment-specific issues before AWS costs accumulate.

**Infrastructure repository:** [fastapi-aws-infra](https://github.com/escanut/fastapi-aws-infra)

---

## What the App Does

A lightweight product catalog with a browser-based frontend.  
The backend is a FastAPI service using async request handling and connection pooling. This avoids opening a new database connection per request and handles concurrent load more efficiently.

### Endpoints

- `GET /api/products` retrieves all products  
- `POST /api/products` creates a product  
- `DELETE /api/products/{id}` removes a product  
- `GET /health` reports API and database status and is used by the ALB health check  

---

## Development Workflow: Three Stages

The `dev/` folder contains local environments.  
The `prod/` folder holds production-ready code deployed to EKS via GitHub Actions.

---

### Stage 1: Docker Compose

**Purpose:** Fast feedback loop for code changes. No cluster overhead.

`docker-compose up`


The frontend is served by Nginx with a reverse proxy to the backend (`/api` routes to `backend:8000`).  

The backend reads database credentials directly from environment variables. A volume mount mirrors local code into the container so changes apply without rebuilding the image.

Secrets are intentionally kept as plain environment variables in this stage. That is acceptable for a local sandbox and deliberately different from production to highlight the security contrast.

---

### Stage 2: Minikube

**Purpose:** Validate Kubernetes behavior locally before using AWS. This reduces the risk of discovering cluster misconfigurations after infrastructure costs begin.


`minikube start`

Images are built within minikubes own docker environment using `eval $(minikube docker-env)`

Then nginx ingress is added with `minikube addons enable ingress`

Before applying with
`kubectl apply -f dev/k8s/`



Secrets are managed through Kubernetes `Secret` manifests (`dev/k8s/db-secrets.yaml`).  

Postgres runs as a pod with a `PersistentVolumeClaim`.  

Ingress routing mirrors the production ALB configuration so routing issues appear here instead of in EKS.

---

### Stage 3: Production on EKS

**Purpose:** Live deployment with managed infrastructure, automated CI/CD, and AWS Secrets Manager integration.

Key differences from Minikube:

- Database credentials are not stored in Kubernetes. They are pulled from AWS Secrets Manager at runtime using the External Secrets Operator.  
- Images are pulled from Amazon ECR.  
- The ALB is provisioned automatically by the AWS Load Balancer Controller when the Ingress resource is applied.  
- Deployments trigger on every push to `main` via GitHub Actions.  

---

## Production Deployment Pipeline

On push to `main`, the workflow:

1. Exchanges an OIDC token for temporary AWS credentials. No long-lived access keys are stored.  
2. Builds and pushes both Docker images to ECR, tagged with the commit SHA and `latest`.  
3. Updates kubeconfig for the EKS cluster.  
4. Applies Kubernetes manifests with environment-specific substitutions.  
5. Updates each deployment with the exact commit SHA tag.  
6. Waits for both deployments to reach a healthy rollout state.  

If a rollout fails, the GitHub Actions log shows the error before the workflow exits.

---

## Secrets Management by Stage

| Stage | Method |
|-------|--------|
| Docker Compose | Environment variables in `docker-compose.yaml` |
| Minikube | Kubernetes `Secret` manifest (base64 encoded) |
| EKS (prod) | AWS Secrets Manager via External Secrets Operator |

In production, the `ExternalSecret` resource syncs from Secrets Manager into a Kubernetes-native secret. The pod consumes that secret as environment variables.

The application code remains unchanged across environments. Only the secret delivery mechanism differs.

---

## Repository Structure

.
├── dev/
│   ├── backend/
│   ├── frontend/
│   ├── k8s/
│   ├── docker-compose.yaml
│   ├── init.sql
│   └── nginx.conf
├── prod/
│   ├── backend/
│   ├── frontend/
│   └── k8s/
└── .github/
    └── workflows/
        └── deploy.yaml




---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, asyncpg, connection pooling |
| Frontend | HTML, CSS, JavaScript |
| Container runtime | Docker, Nginx |
| Local orchestration | Docker Compose, Minikube |
| Production orchestration | AWS EKS |
| CI/CD | GitHub Actions with OIDC authentication |
| Secrets | AWS Secrets Manager and External Secrets Operator |
| Registry | Amazon ECR |

---

## Why This Workflow

This three-stage workflow exists for a measurable reason.

An EKS control plane costs $0.10 per hour based on AWS pricing. Configuration errors such as incorrect port bindings, broken ingress rules, or secret injection failures should not be discovered in a paid environment.

Validating locally in Minikube eliminates unnecessary cloud cost. Only code confirmed to work in Kubernetes reaches AWS.

---

## Contact

Victor Ogechukwu Ojeje  
Cloud Engineer 

- LinkedIn: https://www.linkedin.com/in/victorojeje/  
- GitHub: https://github.com/escanut  
- Email: ojejevictor@gmail.com

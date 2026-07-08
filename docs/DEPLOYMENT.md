# Deployment Guide

This guide covers two paths: running everything locally with Docker Compose
(for evaluation or development), and deploying the full stack to AWS with
Terraform (for a real, always-available, backed-up environment).

## 1. Local deployment (Docker Compose)

**Prerequisites**: Docker and Docker Compose.

```bash
git clone https://github.com/MrBoyard7/pulseboard.git
cd pulseboard

# Backend environment file
cp backend/.env.example backend/.env
# Edit backend/.env and set a real SECRET_KEY:
#   python3 -c "import secrets; print(secrets.token_urlsafe(64))"

docker compose -f infra/docker-compose.yml up --build
```

This starts three containers:

| Service | URL | Notes |
|---|---|---|
| `db` | Ã¢â‚¬â€ | PostgreSQL 16, data persisted in a named volume |
| `backend` | http://localhost:8080 | Runs migrations, seeds 120 demo projects, then serves the API. Interactive docs at `/docs`. |
| `frontend` | http://localhost:5173 | Static build served by nginx |

Sign in with the seeded demo account: **admin@pulseboard.dev / ChangeMe123!**

To stop everything: `docker compose -f infra/docker-compose.yml down` (add
`-v` to also drop the database volume).

## 2. Cloud deployment (AWS via Terraform)

**Prerequisites**: an AWS account, AWS CLI configured, Terraform >= 1.7,
Docker.

### Step 1 Ã¢â‚¬â€ Provision infrastructure

```bash
cd infra/terraform
terraform init
terraform apply \
  -var="secret_key=$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"
```

Review the plan before confirming. This creates the VPC, RDS instance, ECS
cluster/service behind an ALB, the ECR repository, and the S3/CloudFront
static hosting for the frontend. Full details in
[infra/terraform/README.md](../infra/terraform/README.md).

### Step 2 Ã¢â‚¬â€ Build and push the backend image

```bash
cd ../../backend
REPO_URL=$(cd ../infra/terraform && terraform output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "${REPO_URL%/*}"
docker build -t "$REPO_URL:latest" .
docker push "$REPO_URL:latest"
```

### Step 3 Ã¢â‚¬â€ Run the database migration and seed data once

Run this as a one-off ECS task (or temporarily from your machine against the
RDS endpoint via an SSH tunnel/bastion, since RDS sits in a private subnet):

```bash
aws ecs run-task \
  --cluster pulseboard-production-cluster \
  --task-definition pulseboard-production-backend \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<private-subnet-id>],securityGroups=[<ecs-sg-id>]}" \
  --overrides '{"containerOverrides":[{"name":"backend","command":["sh","-c","alembic upgrade head && python -m scripts.seed_data"]}]}'
```

Then force the service to pick up the freshly pushed image:

```bash
aws ecs update-service --cluster pulseboard-production-cluster \
  --service pulseboard-production-backend --force-new-deployment
```

### Step 4 Ã¢â‚¬â€ Build and publish the frontend

```bash
cd ../frontend
VITE_API_BASE_URL="$(cd ../infra/terraform && terraform output -raw backend_url)" npm run build
aws s3 sync dist/ "s3://$(cd ../infra/terraform && terraform output -raw frontend_bucket_name)" --delete
aws cloudfront create-invalidation \
  --distribution-id "$(cd ../infra/terraform && terraform output -raw cloudfront_distribution_id)" \
  --paths "/*"
```

### Step 5 Ã¢â‚¬â€ Verify

```bash
terraform output frontend_url
```

Open that URL, sign in with the demo account, and confirm the dashboard
loads and updates live (open it in two browser tabs and edit a task in one Ã¢â‚¬â€
the other should update within a second).

## Backups and availability

- RDS automated backups are enabled with a 7-day retention window
  (`backup_retention_period` in `rds.tf`); `multi_az` is turned on
  automatically for the `production` environment.
- ECS runs `backend_desired_count = 2` tasks by default across two
  availability zones behind the ALB, so a single task or AZ failure does not
  take the API down.
- CloudFront + S3 for the frontend is inherently highly available and
  globally distributed.

## Handing this over to your internal admin

A short walkthrough covering the following is enough for someone comfortable
with AWS basics to maintain this day to day:

1. **Where things live**: point them at this file, `infra/terraform/README.md`,
   and the AWS Console (ECS cluster, RDS instance, CloudFront distribution).
2. **Routine deploys**: re-run Steps 2Ã¢â‚¬â€œ4 above whenever there's a new
   backend or frontend release.
3. **Rolling back**: `aws ecs update-service --task-definition <previous-revision-arn>`
   for the backend; `aws s3 sync` an older `dist/` build (or re-run
   `npm run build` against a previous git tag) for the frontend.
4. **Where secrets live**: the JWT secret and DB credentials are in Secrets
   Manager (see `terraform output db_credentials_secret_arn`) Ã¢â‚¬â€ never in
   source control.
5. **Monitoring**: CloudWatch Logs group `/ecs/pulseboard-production-backend`
   for backend logs; ECS Container Insights (enabled in `ecs.tf`) for
   CPU/memory; the ALB target group health check hits `/health`.
6. **Adding a user**: `POST /api/users` as an admin (see the interactive API
   docs at `/docs`), or directly via the seed script pattern for bulk
   imports.

## Testing the deployment before going live

See the root [README.md](../README.md#testing) for the exact commands to run
the backend and frontend test suites, and the acceptance-criteria checklist
below.

| Acceptance criterion | How to verify |
|---|---|
| Dashboard loads in < 3s for 100+ active projects | Seed script creates 120 projects; open the dashboard and check the Network tab Ã¢â‚¬â€ `/api/dashboard/summary` should return in well under a second on the default RDS instance class, with the SPA rendering shortly after. |
| Role-based permissions block unauthorized edits | Run `pytest backend/tests/test_permissions.py` Ã¢â‚¬â€ it asserts members and executives receive `403` on out-of-scope writes. |
| Updates reflect without manual refresh | Open the dashboard in two tabs, edit a task's status in one, confirm the other updates within ~1 second (WebSocket broadcast). |
| Codebase passes linting/tests | `flake8`, `black --check`, `isort --check-only`, `mypy`, `pytest` (backend) and `eslint`, `vitest`, `tsc -b` (frontend) Ã¢â‚¬â€ see CI workflow at `.github/workflows/ci.yml`. |

# PulseBoard — Terraform (AWS)

This module provisions a production-shaped AWS environment for PulseBoard:

- **VPC** with public and private subnets across two availability zones, plus
  a NAT gateway for outbound access from private subnets.
- **RDS for PostgreSQL** (Multi-AZ in `production`) in private subnets,
  credentials generated and stored in **Secrets Manager**.
- **ECS Fargate** cluster running the backend API behind an **Application
  Load Balancer**.
- **ECR** repository to host backend container images.
- **S3 + CloudFront** static hosting for the built React frontend, with
  origin access control so the bucket itself stays private.

## Prerequisites

- Terraform >= 1.7
- An AWS account and credentials configured (`aws configure` or environment
  variables)
- Docker, to build and push the backend image to ECR

## Usage

```bash
cd infra/terraform
terraform init
terraform plan -var="secret_key=$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"
terraform apply -var="secret_key=..."
```

After the first `apply`, build and push the backend image, then force a new
deployment:

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin "$(terraform output -raw ecr_repository_url | cut -d/ -f1)"

docker build -t "$(terraform output -raw ecr_repository_url):latest" ../../backend
docker push "$(terraform output -raw ecr_repository_url):latest"

aws ecs update-service --cluster pulseboard-production-cluster \
  --service pulseboard-production-backend --force-new-deployment
```

Then build and publish the frontend:

```bash
cd ../../frontend
VITE_API_BASE_URL="$(cd ../infra/terraform && terraform output -raw backend_url)" npm run build
aws s3 sync dist/ "s3://$(cd ../infra/terraform && terraform output -raw frontend_bucket_name)" --delete
aws cloudfront create-invalidation \
  --distribution-id "$(cd ../infra/terraform && terraform output -raw cloudfront_distribution_id)" \
  --paths "/*"
```

## Notes on production-readiness

- Attach an ACM certificate to the ALB listener and to CloudFront for a
  custom domain and HTTPS end to end (both are stubbed for HTTP/the default
  certificate here to keep the module runnable out of the box).
- Enable the S3 remote backend block in `main.tf` before using this in a
  team setting, so state is shared and locked.
- Consider AWS RDS Proxy if you scale the backend beyond a handful of
  Fargate tasks, to avoid exhausting Postgres connections.
- Wire the WebSocket broadcast (`app/services/realtime.py`) to a Redis
  pub/sub channel (e.g. ElastiCache) before running more than one backend
  task, so a client connected to task A also receives events triggered on
  task B. This module already runs `backend_desired_count = 2` by default,
  so plan to add ElastiCache before going to production traffic.

## Cost note

This module is intentionally modest (t4g.micro RDS, small Fargate tasks) to
keep a demo environment cheap. Review `variables.tf` before pointing it at a
production workload.

output "backend_url" {
  description = "Public URL of the backend API (behind the ALB)."
  value       = "http://${aws_lb.main.dns_name}"
}

output "frontend_url" {
  description = "Public URL of the frontend (CloudFront distribution)."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "ecr_repository_url" {
  description = "Push backend images here before deploying a new task revision."
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_bucket_name" {
  description = "S3 bucket to sync the built frontend (`npm run build`) into."
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_distribution_id" {
  description = "Used to invalidate the CDN cache after deploying a new frontend build."
  value       = aws_cloudfront_distribution.frontend.id
}

output "db_endpoint" {
  description = "RDS PostgreSQL endpoint."
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "db_credentials_secret_arn" {
  description = "Secrets Manager ARN holding the generated database credentials."
  value       = aws_secretsmanager_secret.db_credentials.arn
}

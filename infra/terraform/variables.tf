variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. staging, production)."
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Short name used to prefix resource names."
  type        = string
  default     = "pulseboard"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to spread subnets across."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Name of the application database."
  type        = string
  default     = "pulseboard"
}

variable "db_username" {
  description = "Master username for the RDS instance."
  type        = string
  default     = "pulseboard"
  sensitive   = true
}

variable "backend_image" {
  description = "Container image URI for the backend API (defaults to the ECR repo created here)."
  type        = string
  default     = ""
}

variable "backend_container_port" {
  description = "Port the backend container listens on."
  type        = number
  default     = 8000
}

variable "backend_cpu" {
  description = "Fargate task CPU units for the backend service."
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Fargate task memory (MiB) for the backend service."
  type        = number
  default     = 1024
}

variable "backend_desired_count" {
  description = "Number of backend task replicas to run."
  type        = number
  default     = 2
}

variable "secret_key" {
  description = "Application JWT signing secret. Generate with `python -c \"import secrets; print(secrets.token_urlsafe(64))\"`."
  type        = string
  sensitive   = true
}

variable "allowed_frontend_origin" {
  description = "Origin allowed to call the API via CORS (your CloudFront domain)."
  type        = string
  default     = "*"
}

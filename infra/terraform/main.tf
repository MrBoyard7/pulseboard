terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Uncomment and configure once you have a state bucket; keeping Terraform
  # state in S3 with DynamoDB locking is strongly recommended for any
  # environment beyond a solo proof of concept.
  #
  # backend "s3" {
  #   bucket         = "pulseboard-terraform-state"
  #   key            = "pulseboard/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "pulseboard-terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "pulseboard"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

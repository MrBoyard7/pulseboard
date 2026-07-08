# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-04

### Added

- Initial release: FastAPI backend with JWT auth, role-based access control
  (admin / member / executive), and a normalized PostgreSQL schema for
  projects, tasks, blockers, and budget entries.
- Real-time dashboard updates over WebSocket, so writes from any client are
  reflected everywhere without a manual refresh.
- React + TypeScript dashboard: filterable project table, budget burn chart,
  timeline health breakdown, blockers panel, and a project drill-down view.
- Seed script generating a 120-project demo portfolio.
- Docker Compose setup for local development and Terraform module for AWS
  deployment (VPC, RDS, ECS Fargate, ALB, S3 + CloudFront).
- CI pipeline (lint, type-check, tests, coverage) for both backend and
  frontend.

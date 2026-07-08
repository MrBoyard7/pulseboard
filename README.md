# PulseBoard

**Real-time, role-based project portfolio dashboard** - consolidate every
project your organization runs into a single database and see budget burn,
timeline health, and blockers at a glance, updated live.

[![CI](https://github.com/MrBoyard7/pulseboard/actions/workflows/ci.yml/badge.svg)](https://github.com/MrBoyard7/pulseboard/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MrBoyard7/pulseboard/branch/main/graph/badge.svg)](https://codecov.io/gh/MrBoyard7/pulseboard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

> Badges for CI and Codecov go live once this repository is pushed to
> GitHub and connected to [codecov.io](https://codecov.io) - see
> [Testing](#testing) below for how the pipeline that feeds them works.

## Why this exists

Most teams start tracking projects in spreadsheets. That works until you
have more than a handful of projects across more than one team - at which
point nobody has a reliable, up-to-date picture of what's on track, what's
burning through budget too fast, and what's blocked. PulseBoard replaces
that spreadsheet sprawl with one normalized database and a dashboard that
updates itself.

## Features

- **One data model, every project** - a normalized PostgreSQL schema tracks
  each project from kickoff to close-out, with tasks, budget entries, and
  blockers as first-class related records (see
  [docs/DATA_MODEL.md](docs/DATA_MODEL.md)).
- **Live dashboard** - filter by stage, owner, or timeline health; see
  budget burn, timeline health, and open blockers at a glance; drill down
  into raw records for any project. Updates push over WebSocket, so nobody
  has to hit refresh.
- **Role-based access control** - admins (project managers) have full
  read/write access, members can update only what's assigned to them,
  executives get a read-only view. Enforced server-side, not just hidden in
  the UI (see [docs/USER_GUIDE.md](docs/USER_GUIDE.md)).
- **Cloud-ready from day one** - Docker Compose for local development, a
  complete Terraform module for a secure, backed-up AWS deployment (see
  [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
  [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)).
- **120-project demo dataset** seeded out of the box, well above the
  100-project acceptance threshold this project was built against.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack React Query, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Real-time | Native WebSocket |
| Infrastructure | Docker, Terraform, AWS (ECS Fargate, RDS, ALB, S3, CloudFront) |
| CI | GitHub Actions, Codecov |

Full rationale for these choices - including why a normalized relational
schema was chosen over a document store - is in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Project structure

```
pulseboard/
|-- .github/workflows/ci.yml       # Lint, type-check, test, build - both stacks
|-- backend/
|   |-- app/
|   |   |-- api/routes/            # auth, users, projects, tasks, blockers, budget, dashboard, ws
|   |   |-- core/                  # security (JWT/bcrypt) and permissions
|   |   |-- models/                # SQLAlchemy ORM models
|   |   |-- schemas/                # Pydantic request/response schemas
|   |   |-- services/              # analytics + realtime broadcast
|   |   |-- config.py
|   |   |-- database.py
|   |   `-- main.py
|   |-- alembic/                   # migrations
|   |-- scripts/seed_data.py       # generates a 120-project demo portfolio
|   |-- tests/                     # pytest suite (auth, projects, permissions, dashboard)
|   |-- requirements.txt / requirements-dev.txt
|   |-- pyproject.toml             # black, isort, mypy, pytest config
|   |-- Dockerfile
|   `-- .env.example
|-- frontend/
|   |-- src/
|   |   |-- api/client.ts          # axios instance + JWT interceptor
|   |   |-- components/            # DashboardLayout, FilterBar, ProjectTable, charts, modal, RoleGuard
|   |   |-- hooks/                 # useAuth, useProjects, useRealtime
|   |   |-- pages/                 # LoginPage, DashboardPage, ProjectDetailPage
|   |   `-- types/                 # shared TS types mirroring the backend schemas
|   |-- tests/                     # vitest + Testing Library
|   |-- package.json
|   |-- Dockerfile                 # multi-stage build served by nginx
|   `-- nginx.conf
|-- infra/
|   |-- docker-compose.yml         # full local stack: db + backend + frontend
|   `-- terraform/                 # VPC, RDS, ECS Fargate, ALB, ECR, S3 + CloudFront
|-- docs/
|   |-- ARCHITECTURE.md            # diagram + tech-stack bill of materials
|   |-- DATA_MODEL.md              # ERD + schema rationale
|   |-- DEPLOYMENT.md              # step-by-step local and AWS deployment
|   `-- USER_GUIDE.md              # what each role can do
|-- LICENSE
|-- CONTRIBUTING.md
|-- CODE_OF_CONDUCT.md
|-- SECURITY.md
`-- CHANGELOG.md
```

## Quickstart (local, Docker Compose)

```bash
git clone https://github.com/MrBoyard7/pulseboard.git
cd pulseboard

cp backend/.env.example backend/.env
# Edit backend/.env and set SECRET_KEY to the output of:
#   python3 -c "import secrets; print(secrets.token_urlsafe(64))"

docker compose -f infra/docker-compose.yml up --build
```

Open **http://localhost:5173** and sign in with the seeded demo account:

```
Email:    admin@pulseboard.dev
Password: ChangeMe123!
```

The API is at **http://localhost:8080**, with interactive Swagger docs at
**http://localhost:8080/docs**.

> The backend container listens on 8000 internally but is published on the
> host as **8080** (see `infra/docker-compose.yml`) to avoid colliding with
> ports Windows sometimes reserves for Hyper-V/WSL2 - see
> [docs/DEPLOYMENT.md#troubleshooting](docs/DEPLOYMENT.md#troubleshooting)
> if you'd rather remap it back to 8000.

## Running the two services without Docker

**Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # then set SECRET_KEY and a local DATABASE_URL

alembic upgrade head
python -m scripts.seed_data
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

## Testing

**Backend** (from `backend/`, with the dev dependencies installed):

```bash
pytest                    # runs the full suite with coverage (see pyproject.toml)
flake8 app tests scripts  # lint
black --check app tests scripts
isort --check-only app tests scripts
mypy app                  # type-check
```

**Frontend** (from `frontend/`, with dependencies installed):

```bash
npm run test    # vitest + Testing Library
npm run lint    # eslint
npm run build   # tsc -b && vite build - confirms the production bundle compiles
```

Both suites also run automatically on every push and pull request via
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the full walkthrough,
including provisioning AWS infrastructure with Terraform, building and
pushing the backend image, and publishing the frontend to S3/CloudFront.

## Acceptance criteria checklist

| Criterion | Status |
|---|---|
| Dashboard loads in < 3s for 100+ active projects | [x] Seed script ships 120 projects; verified against the aggregation endpoint (see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#testing-the-deployment-before-going-live)) |
| Role-based permissions block unauthorized edits | [x] Enforced server-side and covered by `tests/test_permissions.py` |
| Updates reflect without manual refresh | [x] WebSocket broadcast on every mutation, consumed by `useRealtimeDashboard` |
| Codebase passes linting/tests | [x] `black`, `isort`, `flake8`, `mypy`, `pytest` (backend); `eslint`, `vitest`, `tsc -b` (frontend) - all wired into CI |

## License

Released under the [MIT License](LICENSE).

Copyright (c) 2026 Prince Boyard MBOUNGOU NGOMA
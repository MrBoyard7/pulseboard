"""PulseBoard API entrypoint.

Run locally with:
    uvicorn app.main:app --reload

See docs/DEPLOYMENT.md for containerized and cloud deployment options.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, blockers, budget, dashboard, projects, tasks, users, ws
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Real-time, multi-tenant project portfolio management API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(blockers.router)
app.include_router(budget.router)
app.include_router(dashboard.router)
app.include_router(ws.router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Liveness/readiness probe used by the container orchestrator."""
    return {"status": "ok", "environment": settings.environment}

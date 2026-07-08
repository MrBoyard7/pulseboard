"""Shared pytest fixtures for the backend test suite.

Tests run against an in-memory SQLite database instead of PostgreSQL so
the suite is fast and has zero external dependencies in CI. SQLite is
close enough to Postgres for our ORM usage; anything Postgres-specific
would need a dedicated integration test against a real instance.
"""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.enums import UserRole
from app.models.project import Project
from app.models.user import User

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session):
    user = User(
        full_name="Ada Admin",
        email="admin@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def member_user(db_session):
    user = User(
        full_name="Milo Member",
        email="member@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def executive_user(db_session):
    user = User(
        full_name="Eve Executive",
        email="exec@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.EXECUTIVE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def sample_project(db_session, admin_user):
    project = Project(
        name="Checkout Redesign",
        description="Improve checkout conversion.",
        start_date=date.today() - timedelta(days=30),
        target_end_date=date.today() + timedelta(days=60),
        budget_total=100_000,
        owner_id=admin_user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


def auth_headers(client: TestClient, email: str, password: str = "password123") -> dict:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

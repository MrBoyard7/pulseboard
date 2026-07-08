"""Populate the database with realistic sample data.

Generates a portfolio of 120 projects (well above the 100-project
acceptance threshold) spread across every stage, complete with tasks,
budget entries, and blockers, so the dashboard can be evaluated
immediately after a fresh install.

Usage:
    python -m scripts.seed_data
"""
import random
from datetime import date, timedelta

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.blocker import Blocker
from app.models.budget_entry import BudgetEntry
from app.models.enums import BlockerSeverity, ProjectStage, TaskStatus, UserRole
from app.models.project import Project
from app.models.task import Task
from app.models.team import Team
from app.models.user import User

random.seed(42)  # deterministic output so re-running produces the same demo data

TEAM_NAMES = ["Platform", "Growth", "Data & Analytics", "Customer Success", "Mobile"]

FIRST_NAMES = [
    "Amara", "Liam", "Sofia", "Noah", "Yuki", "Elena", "Kwame", "Maria", "Ravi", "Chloe",
    "Diego", "Fatima", "Hana", "Lucas", "Nadia", "Omar", "Priya", "Sven", "Talia", "Victor",
]
LAST_NAMES = [
    "Nguyen", "Garcia", "Okafor", "Dubois", "Andersson", "Kowalski", "Silva", "Tanaka",
    "Haddad", "Petrov", "Rossi", "Kim", "Larsen", "Mensah", "Fischer",
]

PROJECT_THEMES = [
    "Checkout Redesign", "Data Warehouse Migration", "Mobile Onboarding Revamp",
    "Customer Portal", "Billing Platform Upgrade", "Search Relevance Overhaul",
    "Fraud Detection Engine", "Internal Analytics Hub", "API Gateway Modernization",
    "Localization Rollout", "Notification System", "Loyalty Program Launch",
    "Accessibility Audit", "Performance Optimization", "Vendor Integration",
    "Support Ticketing Revamp", "Marketing Site Relaunch", "Inventory Sync Service",
    "Identity & Access Overhaul", "Reporting Suite",
]

BLOCKER_TEMPLATES = [
    "Waiting on third-party API credentials",
    "Key reviewer unavailable until next sprint",
    "Staging environment configuration mismatch",
    "Dependency on another team's unreleased service",
    "Budget approval pending from finance",
    "Data migration validation failing intermittently",
    "Design assets not yet finalized",
    "Load testing uncovered a scalability issue",
]


def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Project).count() > 0:
            print("Database already contains projects; skipping seed.")
            return

        teams = [Team(name=name, description=f"{name} engineering team") for name in TEAM_NAMES]
        db.add_all(teams)
        db.flush()

        users: list[User] = [
            User(
                full_name="Prince Boyard MBOUNGOU NGOMA",
                email="admin@pulseboard.dev",
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.ADMIN,
                team_id=teams[0].id,
            )
        ]
        used_emails = {"admin@pulseboard.dev"}
        for _ in range(14):
            role = random.choices(
                [UserRole.MEMBER, UserRole.EXECUTIVE], weights=[0.8, 0.2], k=1
            )[0]
            while True:
                name = random_name()
                email = f"{name.lower().replace(' ', '.')}@pulseboard.dev"
                if email not in used_emails:
                    used_emails.add(email)
                    break
            users.append(
                User(
                    full_name=name,
                    email=email,
                    hashed_password=hash_password("ChangeMe123!"),
                    role=role,
                    team_id=random.choice(teams).id,
                )
            )
        db.add_all(users)
        db.flush()

        admins_and_members = [u for u in users if u.role in (UserRole.ADMIN, UserRole.MEMBER)]

        today = date.today()
        projects: list[Project] = []
        for i in range(120):
            theme = random.choice(PROJECT_THEMES)
            start_offset = random.randint(-400, 30)
            duration = random.randint(60, 270)
            start = today + timedelta(days=start_offset)
            target_end = start + timedelta(days=duration)
            stage = random.choices(
                list(ProjectStage),
                weights=[0.08, 0.12, 0.42, 0.08, 0.12, 0.18],
                k=1,
            )[0]
            budget_total = round(random.uniform(15_000, 450_000), 2)

            project = Project(
                name=f"{theme} #{i + 1}",
                description=f"Delivers the {theme.lower()} initiative for the organization.",
                stage=stage,
                start_date=start,
                target_end_date=target_end,
                actual_end_date=target_end if stage == ProjectStage.CLOSED else None,
                budget_total=budget_total,
                owner_id=random.choice(admins_and_members).id,
                team_id=random.choice(teams).id,
            )
            projects.append(project)
        db.add_all(projects)
        db.flush()

        for project in projects:
            burn_ratio = random.uniform(0.05, 1.05)
            spent_target = float(project.budget_total) * burn_ratio
            remaining = spent_target
            num_entries = random.randint(2, 8)
            for _ in range(num_entries):
                if remaining <= 0:
                    break
                amount = round(min(remaining, random.uniform(500, remaining)), 2)
                remaining -= amount
                db.add(
                    BudgetEntry(
                        project_id=project.id,
                        label=random.choice(
                            ["Contractor invoice", "Cloud infrastructure", "Software license",
                             "Vendor services", "Equipment", "Travel"]
                        ),
                        amount=amount,
                        incurred_on=project.start_date
                        + timedelta(days=random.randint(0, max((today - project.start_date).days, 1))),
                    )
                )

            # Tasks
            for t in range(random.randint(3, 10)):
                status = random.choices(list(TaskStatus), weights=[0.25, 0.35, 0.15, 0.25], k=1)[0]
                db.add(
                    Task(
                        project_id=project.id,
                        assignee_id=random.choice(admins_and_members).id,
                        title=f"{project.name} - task {t + 1}",
                        status=status,
                        due_date=project.target_end_date - timedelta(days=random.randint(0, 30)),
                    )
                )

            if stage in (ProjectStage.IN_PROGRESS, ProjectStage.ON_HOLD) and random.random() < 0.3:
                for _ in range(random.randint(1, 2)):
                    db.add(
                        Blocker(
                            project_id=project.id,
                            reported_by_id=random.choice(admins_and_members).id,
                            description=random.choice(BLOCKER_TEMPLATES),
                            severity=random.choices(
                                list(BlockerSeverity), weights=[0.2, 0.35, 0.3, 0.15], k=1
                            )[0],
                            resolved=random.random() < 0.4,
                        )
                    )

        db.commit()
        print(f"Seeded {len(teams)} teams, {len(users)} users, and {len(projects)} projects.")
        print("Demo login: admin@pulseboard.dev / ChangeMe123!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
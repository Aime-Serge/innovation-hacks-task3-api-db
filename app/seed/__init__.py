"""Seed data (FR-234). Dates are relative to today, so overdue, due-today and upcoming items exist.

The store is in memory, so a separate `python -m app.seed` process cannot fill a running
server. The server seeds itself at startup when SEED_PROFILE is set (never in production).
"""

import random
import secrets
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from app.domain.enums import (
    ActivityType,
    Priority,
    ProjectStatus,
    Role,
    TaskStatus,
    Theme,
)
from app.domain.models import Activity, Project, Task, User

if TYPE_CHECKING:
    from app.container import Container

PEOPLE = [
    ("Aime Serge UKOBIZABA", "aime.serge@example.com", Role.DEVELOPER),
    ("Amara Diallo", "amara.diallo@example.com", Role.LEAD),
    ("Kwame Mensah", "kwame.mensah@example.com", Role.DEVELOPER),
    ("Sofia Alvarez", "sofia.alvarez@example.com", Role.DEVELOPER),
]
PROJECT_NAMES = [
    "Atlas API Gateway",
    "Beacon Notifications",
    "Cairn Design System",
    "Delta Data Pipeline",
    "Ember Mobile App",
    "Flint Auth Service",
    "Grove Analytics",
    "Harbor Billing",
]
VERBS = ["Add", "Fix", "Refactor", "Document", "Test", "Profile", "Review", "Migrate"]
NOUNS = [
    "rate limit config",
    "retry queue",
    "load balancer",
    "audit log",
    "build cache",
    "email templates",
    "search index",
    "session store",
]


@dataclass(frozen=True)
class SeedResult:
    users: int
    projects: int
    tasks: int
    activity: int
    password: str | None


def _pick_status(rng: random.Random) -> TaskStatus:
    return rng.choices(list(TaskStatus), weights=[3, 3, 2, 3])[0]


async def seed(container: "Container", profile: str, password: str) -> SeedResult:
    """Fill the repositories directly, so any status and date can be set for realism."""
    if container.settings.is_production:
        raise RuntimeError("Seeding is refused when APP_ENV=production.")
    # Deterministic demo data, not a security use of random.
    rng = random.Random(42)  # noqa: S311  # nosec B311
    now, today = container.clock.now(), container.clock.today()
    hashed = await container.hasher.hash(password)
    users: list[User] = []
    for name, email, role in PEOPLE:
        user = User(container.ids.new_id(), name, email, hashed, role, None, Theme.SYSTEM, now, now)
        users.append(await container.users_repo.add(user))
    if profile == "empty":
        return SeedResult(len(users), 0, 0, 0, password)
    project_count, task_count = (40, 500) if profile == "large" else (8, 60)
    projects = await _projects(container, users, project_count, today, rng)
    tasks = await _tasks(container, users, projects, task_count, today, rng)
    activity = await _activity(container, users, tasks, 40, rng)
    return SeedResult(len(users), len(projects), len(tasks), activity, password)


async def _projects(
    container: "Container", users: list[User], count: int, today: date, rng: random.Random
) -> list[Project]:
    now = container.clock.now()
    projects: list[Project] = []
    for index in range(count):
        status = ProjectStatus.ACTIVE
        if index == 6 % count:
            status = ProjectStatus.COMPLETED
        elif index == 5 % count:
            status = ProjectStatus.ON_HOLD
        elif index % 5 == 4:
            status = ProjectStatus.PLANNED
        base = PROJECT_NAMES[index % len(PROJECT_NAMES)]
        name = base if index < len(PROJECT_NAMES) else f"{base} {index // len(PROJECT_NAMES) + 1}"
        project = Project(
            container.ids.new_id(),
            name,
            f"{base} keeps the team's work in one place.",
            status,
            today + timedelta(days=rng.randint(-10, 60)),
            users[index % len(users)].id,
            now,
            now,
        )
        projects.append(await container.projects_repo.add(project))
    return projects


async def _tasks(
    container: "Container",
    users: list[User],
    projects: list[Project],
    count: int,
    today: date,
    rng: random.Random,
) -> list[Task]:
    now = container.clock.now()
    # The last project stays empty (a "no tasks yet" case) when there are enough projects.
    fillable = projects[:-1] if len(projects) > 1 else projects
    tasks: list[Task] = []
    for index in range(count):
        project = fillable[index % len(fillable)]
        status = _pick_status(rng)
        due = today + timedelta(days=rng.randint(-8, 14)) if rng.random() < 0.9 else None
        label = f"{project.name.split()[0]} {index // len(fillable) + 1}"
        title = f"{rng.choice(VERBS)} {rng.choice(NOUNS)} ({label})"
        task = Task(
            id=container.ids.new_id(),
            project_id=project.id,
            title=title,
            description=f"Work item {index + 1} for {project.name}.",
            status=status,
            priority=rng.choice(list(Priority)),
            due_date=due,
            assignee_id=rng.choice(users).id if rng.random() < 0.85 else None,
            completed_at=now if status is TaskStatus.DONE else None,
            created_at=now,
            updated_at=now,
        )
        tasks.append(await container.tasks_repo.add(task))
    return tasks


async def _activity(
    container: "Container", users: list[User], tasks: list[Task], count: int, rng: random.Random
) -> int:
    now = container.clock.now()
    kinds = list(ActivityType)
    for index in range(count):
        task = tasks[index % len(tasks)]
        activity = Activity(
            container.ids.new_id(),
            rng.choice(users).id,
            task.project_id,
            task.id,
            rng.choice(kinds),
            now - timedelta(minutes=index * 37),
        )
        await container.activity_repo.add(activity)
    return count


async def apply_seed_profile(container: "Container") -> SeedResult | None:
    """Called at startup: SEED_PROFILE=default|empty|large loads the dataset (development only)."""
    profile = container.settings.seed_profile
    if profile == "none":
        return None
    if container.settings.is_production:
        raise SystemExit("SEED_PROFILE cannot be used when APP_ENV=production.")
    given = container.settings.seed_password
    password = given.get_secret_value() if given else secrets.token_urlsafe(16)
    result = await seed(container, profile, password)
    if given is None:
        print(f"Seeded accounts use this one-time password: {password}")
    return result


__all__ = ["UUID", "SeedResult", "apply_seed_profile", "seed"]

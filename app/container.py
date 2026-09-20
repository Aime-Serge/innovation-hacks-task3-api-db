"""Builds the object graph once per app. Nothing here is module-level state (section 7)."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from app.core.clock import Clock, IdFactory, SystemClock, UuidFactory
from app.core.config import Settings
from app.core.ratelimit import RateLimiter
from app.core.security import PasswordHasher, TokenCodec
from app.repositories.base import (
    ActivityRepository,
    ProjectRepository,
    TaskRepository,
    UserRepository,
)
from app.repositories.memory import (
    MemoryActivityRepository,
    MemoryProjectRepository,
    MemoryTaskRepository,
    MemoryUserRepository,
)
from app.services.activity import ActivityService
from app.services.auth import AuthService
from app.services.dashboard import DashboardService
from app.services.projects import ProjectService
from app.services.tasks import TaskService
from app.services.users import UserService


@dataclass
class Container:
    settings: Settings
    clock: Clock
    ids: IdFactory
    hasher: PasswordHasher
    limiter: RateLimiter
    users_repo: UserRepository
    projects_repo: ProjectRepository
    tasks_repo: TaskRepository
    activity_repo: ActivityRepository
    auth: AuthService
    users: UserService
    projects: ProjectService
    tasks: TaskService
    activity: ActivityService
    dashboard: DashboardService
    readiness_checks: list[Callable[[], Awaitable[bool]]] = field(default_factory=list)

    async def is_ready(self) -> bool:
        """FR-233: every dependency answers. In memory that means the repositories respond."""
        try:
            return all([await check() for check in self.readiness_checks])
        except Exception:
            return False


def build_container(
    settings: Settings, clock: Clock | None = None, ids: IdFactory | None = None
) -> Container:
    clock = clock or SystemClock()
    ids = ids or UuidFactory()
    hasher = PasswordHasher(settings.argon2_time_cost, settings.argon2_memory_kib)
    tokens = TokenCodec(
        settings.secret_key.get_secret_value(),
        settings.jwt_issuer,
        settings.jwt_audience,
        settings.access_token_ttl_seconds,
    )
    users_repo = MemoryUserRepository()
    projects_repo = MemoryProjectRepository()
    tasks_repo = MemoryTaskRepository()
    activity_repo = MemoryActivityRepository()
    activity = ActivityService(activity_repo, clock, ids)
    projects = ProjectService(projects_repo, tasks_repo, activity, clock, ids)

    async def repositories_respond() -> bool:
        await users_repo.count_leads()
        return True

    return Container(
        settings=settings,
        clock=clock,
        ids=ids,
        hasher=hasher,
        limiter=RateLimiter(
            clock, settings.rate_limit_attempts, settings.rate_limit_window_seconds
        ),
        users_repo=users_repo,
        projects_repo=projects_repo,
        tasks_repo=tasks_repo,
        activity_repo=activity_repo,
        auth=AuthService(users_repo, hasher, tokens, clock),
        users=UserService(users_repo, projects_repo, tasks_repo, hasher, clock, ids),
        projects=projects,
        tasks=TaskService(tasks_repo, projects, users_repo, activity, clock, ids),
        activity=activity,
        dashboard=DashboardService(projects_repo, tasks_repo, clock),
        readiness_checks=[repositories_respond],
    )

from dataclasses import dataclass
from datetime import timedelta

from app.core.clock import Clock
from app.domain.enums import ProjectStatus, TaskStatus
from app.domain.models import Task
from app.repositories.base import ProjectQuery, ProjectRepository, TaskQuery, TaskRepository

OPEN_STATUSES = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW]
UPCOMING_DAYS = 7


@dataclass(frozen=True)
class DashboardSummary:
    active_projects: int
    open_tasks: int
    overdue_tasks: int
    completion_rate: int
    upcoming_deadlines: list[Task]


class DashboardService:
    def __init__(self, projects: ProjectRepository, tasks: TaskRepository, clock: Clock) -> None:
        self._projects = projects
        self._tasks = tasks
        self._clock = clock

    async def summary(self) -> DashboardSummary:
        today = self._clock.today()
        active = await self._projects.list(
            ProjectQuery(statuses=[ProjectStatus.ACTIVE], page_size=1)
        )
        everything = await self._tasks.list(TaskQuery(page_size=1))
        done = await self._tasks.list(TaskQuery(statuses=[TaskStatus.DONE], page_size=1))
        open_tasks = await self._tasks.list(TaskQuery(statuses=OPEN_STATUSES, page_size=1))
        overdue = await self._tasks.list(TaskQuery(overdue=True, today=today, page_size=1))
        upcoming = await self._tasks.list(
            TaskQuery(
                statuses=OPEN_STATUSES,
                due_after=today,
                due_before=today + timedelta(days=UPCOMING_DAYS),
                sort="dueDate",
                page_size=50,
            )
        )
        rate = 0 if everything.total == 0 else round(done.total / everything.total * 100)
        return DashboardSummary(active.total, open_tasks.total, overdue.total, rate, upcoming.items)

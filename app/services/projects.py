from dataclasses import dataclass, replace
from datetime import date
from uuid import UUID

from app.core.clock import Clock, IdFactory
from app.core.errors import ErrorDetail, NotFound, ProjectNotEmpty, ValidationFailed
from app.domain.enums import ActivityType, ProjectStatus
from app.domain.models import Progress, Project
from app.domain.unset import UNSET, Unset
from app.repositories.base import Page, ProjectQuery, ProjectRepository, TaskRepository
from app.services.activity import ActivityService
from app.services.authz import Actor, require_project_manager


@dataclass(frozen=True)
class ProjectView:
    project: Project
    progress: Progress


@dataclass(frozen=True)
class ProjectChanges:
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    status: ProjectStatus | Unset = UNSET
    due_date: date | Unset | None = UNSET


class ProjectService:
    def __init__(
        self,
        projects: ProjectRepository,
        tasks: TaskRepository,
        activity: ActivityService,
        clock: Clock,
        ids: IdFactory,
    ) -> None:
        self._projects = projects
        self._tasks = tasks
        self._activity = activity
        self._clock = clock
        self._ids = ids

    async def create(
        self,
        actor: Actor,
        name: str,
        description: str,
        status: ProjectStatus,
        due_date: date | None,
    ) -> ProjectView:
        now = self._clock.now()
        project = await self._projects.add(
            Project(self._ids.new_id(), name, description, status, due_date, actor.id, now, now)
        )
        await self._activity.record(actor.id, project.id, ActivityType.CREATED)
        return await self._view(project)

    async def get(self, project_id: UUID) -> ProjectView:
        return await self._view(await self.require(project_id))

    async def require(self, project_id: UUID) -> Project:
        project = await self._projects.get(project_id)
        if project is None:
            raise NotFound("The project was not found.")
        return project

    async def require_or_invalid(self, project_id: UUID) -> Project:
        """For a body field that names a project: unknown means 422 on that field (FR-214)."""
        project = await self._projects.get(project_id)
        if project is None:
            raise ValidationFailed(
                "One or more fields are invalid.",
                [ErrorDetail("projectId", "The project does not exist.")],
            )
        return project

    async def list(self, query: ProjectQuery) -> Page[ProjectView]:
        page = await self._projects.list(query)
        views = [await self._view(project) for project in page.items]
        return Page(views, page.page, page.page_size, page.total)

    async def update(self, actor: Actor, project_id: UUID, changes: ProjectChanges) -> ProjectView:
        project = await self.require(project_id)
        require_project_manager(actor, project)
        updated = replace(
            project,
            name=project.name if isinstance(changes.name, Unset) else changes.name,
            description=project.description
            if isinstance(changes.description, Unset)
            else changes.description,
            status=project.status if isinstance(changes.status, Unset) else changes.status,
            due_date=project.due_date if isinstance(changes.due_date, Unset) else changes.due_date,
            updated_at=self._clock.now(),
        )
        return await self._view(await self._projects.update(updated))

    async def delete(self, actor: Actor, project_id: UUID) -> None:
        project = await self.require(project_id)
        require_project_manager(actor, project)
        if (await self._tasks.progress_for(project_id)).total_tasks > 0:
            raise ProjectNotEmpty("The project still has tasks and cannot be deleted.")  # BR-206
        await self._projects.delete(project_id)

    async def _view(self, project: Project) -> ProjectView:
        return ProjectView(project, await self._tasks.progress_for(project.id))

from datetime import datetime
from uuid import UUID

from app.core.clock import Clock, IdFactory
from app.domain.enums import ActivityType
from app.domain.models import Activity
from app.repositories.base import ActivityQuery, ActivityRepository, Page


class ActivityService:
    def __init__(self, repository: ActivityRepository, clock: Clock, ids: IdFactory) -> None:
        self._repository = repository
        self._clock = clock
        self._ids = ids

    async def record(
        self, actor_id: UUID, project_id: UUID, kind: ActivityType, task_id: UUID | None = None
    ) -> Activity:
        now: datetime = self._clock.now()
        return await self._repository.add(
            Activity(self._ids.new_id(), actor_id, project_id, task_id, kind, now)
        )

    async def list(self, query: ActivityQuery) -> Page[Activity]:
        return await self._repository.list(query)

from uuid import UUID

from app.domain.models import Activity
from app.repositories.base import ActivityQuery, Page
from app.repositories.memory.common import Store, order, slice_page


class MemoryActivityRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Activity] = {}
        self._store = Store()

    async def add(self, activity: Activity) -> Activity:
        async with self._store.lock:
            self._items[activity.id] = activity
        return activity

    async def list(self, query: ActivityQuery) -> Page[Activity]:
        """Newest first."""
        items = list(self._items.values())
        ordered = order(items, lambda item: item.at, lambda item: item.id, descending=True)
        return Page(
            slice_page(ordered, query.page, query.page_size),
            query.page,
            query.page_size,
            len(items),
        )

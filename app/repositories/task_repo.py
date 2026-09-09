from uuid import UUID

from app.models.task import TaskInDB, TaskStatus


class TaskRepository:
    """In-memory store for Task 2, swappable for a SQLAlchemy-backed
    implementation in Task 3 behind the same method signatures."""

    def __init__(self) -> None:
        self._tasks: dict[UUID, TaskInDB] = {}

    def list(
        self, project_id: UUID | None = None, status: TaskStatus | None = None
    ) -> list[TaskInDB]:
        tasks = list(self._tasks.values())
        if project_id is not None:
            tasks = [t for t in tasks if t.project_id == project_id]
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def get(self, task_id: UUID) -> TaskInDB | None:
        return self._tasks.get(task_id)

    def create(self, task: TaskInDB) -> TaskInDB:
        self._tasks[task.id] = task
        return task

    def update(self, task: TaskInDB) -> TaskInDB:
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: UUID) -> None:
        self._tasks.pop(task_id, None)


task_repository = TaskRepository()

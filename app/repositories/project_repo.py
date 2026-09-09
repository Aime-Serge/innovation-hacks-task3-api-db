from uuid import UUID

from app.models.project import ProjectInDB


class ProjectRepository:
    """In-memory store for Task 2, swappable for a SQLAlchemy-backed
    implementation in Task 3 behind the same method signatures."""

    def __init__(self) -> None:
        self._projects: dict[UUID, ProjectInDB] = {}

    def list(self, owner_id: UUID | None = None) -> list[ProjectInDB]:
        projects = list(self._projects.values())
        if owner_id is not None:
            projects = [p for p in projects if p.owner_id == owner_id]
        return projects

    def get(self, project_id: UUID) -> ProjectInDB | None:
        return self._projects.get(project_id)

    def create(self, project: ProjectInDB) -> ProjectInDB:
        self._projects[project.id] = project
        return project


project_repository = ProjectRepository()

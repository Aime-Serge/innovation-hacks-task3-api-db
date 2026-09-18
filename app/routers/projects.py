from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy.exc import IntegrityError

from app.exceptions import NotFoundError
from app.models.project import ProjectCreate, ProjectInDB, ProjectOut, ProjectUpdate
from app.repositories.project_repo import project_repository
from app.repositories.user_repo import user_repository

router = APIRouter(prefix="/projects", tags=["projects"], dependencies=[])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate) -> ProjectOut:
    if user_repository.get(payload.owner_id) is None:
        raise NotFoundError(f"Owner user '{payload.owner_id}' not found.")
    project = ProjectInDB(
        name=payload.name,
        description=payload.description,
        owner_id=payload.owner_id,
    )
    try:
        return project_repository.create(project).to_out()
    except IntegrityError:
        # The owner existed moments ago in the check above but was
        # deleted before this insert ran — the FK constraint is the real
        # source of truth; translate its rejection to the same 404 the
        # pre-check would have raised, instead of an uncaught 500.
        raise NotFoundError(f"Owner user '{payload.owner_id}' not found.")


@router.get("", response_model=list[ProjectOut])
def list_projects(owner_id: UUID | None = None) -> list[ProjectOut]:
    return [project.to_out() for project in project_repository.list(owner_id=owner_id)]


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: UUID) -> ProjectOut:
    project = project_repository.get(project_id)
    if project is None:
        raise NotFoundError(f"Project '{project_id}' not found.")
    return project.to_out()


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: UUID, payload: ProjectUpdate) -> ProjectOut:
    project = project_repository.get(project_id)
    if project is None:
        raise NotFoundError(f"Project '{project_id}' not found.")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    updated = project_repository.update(project)
    if updated is None:
        raise NotFoundError(f"Project '{project_id}' not found.")
    return updated.to_out()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID) -> None:
    project = project_repository.get(project_id)
    if project is None:
        raise NotFoundError(f"Project '{project_id}' not found.")
    # Cascades to this project's own tasks via the tasks.project_id FK's
    # ON DELETE CASCADE (see app/db/models.py) — no application-level
    # cleanup needed, same as DELETE /users/{id} relying on the same
    # mechanism for a user's owned projects.
    project_repository.delete(project_id)

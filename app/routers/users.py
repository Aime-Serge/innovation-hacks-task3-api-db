from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.models.user import UserCreate, UserInDB, UserOut, UserUpdate
from app.repositories.user_repo import user_repository
from app.security import hash_password

# `dependencies=[]` is deliberate: Task 4 adds an auth dependency here
# without touching any handler below.
router = APIRouter(prefix="/users", tags=["users"], dependencies=[])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> UserOut:
    if user_repository.get_by_email(payload.email):
        raise ConflictError(f"A user with email '{payload.email}' already exists.")
    user = UserInDB(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    try:
        return user_repository.create(user).to_out()
    except IntegrityError:
        # Another request created the same email between the check above
        # and this insert — the DB's unique constraint is the real
        # source of truth here; translate its rejection to the same 409
        # the pre-check would have raised, instead of an uncaught 500.
        raise ConflictError(f"A user with email '{payload.email}' already exists.")


@router.get("", response_model=list[UserOut])
def list_users() -> list[UserOut]:
    return [user.to_out() for user in user_repository.list()]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: UUID) -> UserOut:
    user = user_repository.get(user_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' not found.")
    return user.to_out()


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: UUID, payload: UserUpdate) -> UserOut:
    user = user_repository.get(user_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' not found.")

    if payload.email is not None and payload.email.lower() != user.email.lower():
        existing = user_repository.get_by_email(payload.email)
        if existing is not None:
            raise ConflictError(f"A user with email '{payload.email}' already exists.")
        user.email = payload.email

    if payload.name is not None:
        user.name = payload.name
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    try:
        updated = user_repository.update(user)
    except IntegrityError:
        raise ConflictError(f"A user with email '{payload.email}' already exists.")
    if updated is None:
        raise NotFoundError(f"User '{user_id}' not found.")
    return updated.to_out()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID) -> None:
    user = user_repository.get(user_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' not found.")
    user_repository.delete(user_id)

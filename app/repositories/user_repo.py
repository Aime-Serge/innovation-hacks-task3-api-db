from uuid import UUID

from app.models.user import UserInDB


class UserRepository:
    """In-memory store for Task 2. Task 3 swaps this for a SQLAlchemy-backed
    implementation exposing the same method signatures — routers never
    touch storage directly, so that swap won't require route changes."""

    def __init__(self) -> None:
        self._users: dict[UUID, UserInDB] = {}

    def list(self) -> list[UserInDB]:
        return list(self._users.values())

    def get(self, user_id: UUID) -> UserInDB | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> UserInDB | None:
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def create(self, user: UserInDB) -> UserInDB:
        self._users[user.id] = user
        return user

    def update(self, user: UserInDB) -> UserInDB:
        self._users[user.id] = user
        return user

    def delete(self, user_id: UUID) -> None:
        self._users.pop(user_id, None)


user_repository = UserRepository()

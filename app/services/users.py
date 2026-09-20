from dataclasses import dataclass, replace
from uuid import UUID

from app.core.clock import Clock, IdFactory
from app.core.errors import (
    EmailAlreadyExists,
    ErrorDetail,
    LastLead,
    NotFound,
    UserOwnsProjects,
    ValidationFailed,
)
from app.core.security import PasswordHasher
from app.domain.enums import Role, Theme
from app.domain.models import User
from app.domain.unset import UNSET, Unset
from app.repositories.base import (
    Page,
    ProjectRepository,
    TaskRepository,
    UserQuery,
    UserRepository,
)
from app.services.authz import Actor, require_lead, require_self_or_lead


@dataclass(frozen=True)
class UserChanges:
    name: str | Unset = UNSET
    avatar_url: str | Unset | None = UNSET
    theme: Theme | Unset = UNSET
    role: Role | Unset = UNSET


class UserService:
    def __init__(
        self,
        users: UserRepository,
        projects: ProjectRepository,
        tasks: TaskRepository,
        hasher: PasswordHasher,
        clock: Clock,
        ids: IdFactory,
    ) -> None:
        self._users = users
        self._projects = projects
        self._tasks = tasks
        self._hasher = hasher
        self._clock = clock
        self._ids = ids

    async def register(
        self,
        name: str,
        email: str,
        password: str,
        avatar_url: str | None = None,
        theme: Theme = Theme.SYSTEM,
        role: Role = Role.DEVELOPER,
    ) -> User:
        """BR-201, BR-209 and FR-202. `role` is only ever set by the seed command."""
        normalised = email.strip().lower()
        if password == email or password.lower() == normalised:
            raise ValidationFailed(
                "One or more fields are invalid.",
                [ErrorDetail("password", "Must not be the same as the email address.")],
            )
        if await self._users.get_by_email(normalised) is not None:
            raise EmailAlreadyExists("An account with this email already exists.")
        now = self._clock.now()
        user = User(
            id=self._ids.new_id(),
            name=name,
            email=normalised,
            password_hash=await self._hasher.hash(password),
            role=role,
            avatar_url=avatar_url,
            theme=theme,
            created_at=now,
            updated_at=now,
        )
        return await self._users.add(user)

    async def list(self, query: UserQuery) -> Page[User]:
        return await self._users.list(query)

    async def get(self, user_id: UUID) -> User:
        user = await self._users.get(user_id)
        if user is None:
            raise NotFound("The user was not found.")
        return user

    async def update(self, actor: Actor, user_id: UUID, changes: UserChanges) -> User:
        require_self_or_lead(actor, user_id)
        target = await self.get(user_id)
        if not isinstance(changes.role, Unset):
            require_lead(actor)  # BR-209
            await self._check_demotion(target, changes.role)
        updated = replace(
            target,
            name=target.name if isinstance(changes.name, Unset) else changes.name,
            avatar_url=target.avatar_url
            if isinstance(changes.avatar_url, Unset)
            else changes.avatar_url,
            theme=target.theme if isinstance(changes.theme, Unset) else changes.theme,
            role=target.role if isinstance(changes.role, Unset) else changes.role,
            updated_at=self._clock.now(),
        )
        return await self._users.update(updated)

    async def delete(self, actor: Actor, user_id: UUID) -> None:
        require_lead(actor)
        target = await self.get(user_id)
        if await self._projects.count_by_owner(user_id) > 0:
            raise UserOwnsProjects("This user owns projects and cannot be deleted.")  # BR-207
        if target.role is Role.LEAD and await self._users.count_leads() <= 1:
            raise LastLead("The last remaining lead cannot be deleted.")  # BR-208
        await self._tasks.unassign_user(user_id)
        await self._users.delete(user_id)

    async def _check_demotion(self, target: User, new_role: Role) -> None:
        demoting = target.role is Role.LEAD and new_role is not Role.LEAD
        if demoting and await self._users.count_leads() <= 1:
            raise LastLead("The last remaining lead cannot be demoted.")  # BR-208

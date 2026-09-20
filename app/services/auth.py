from app.core.clock import Clock
from app.core.errors import InvalidCredentials, Unauthenticated
from app.core.security import IssuedToken, PasswordHasher, TokenCodec
from app.domain.models import User
from app.repositories.base import UserRepository


class AuthService:
    def __init__(
        self, users: UserRepository, hasher: PasswordHasher, tokens: TokenCodec, clock: Clock
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._clock = clock

    async def login(self, email: str, password: str) -> IssuedToken:
        """Unknown email and wrong password are indistinguishable (FR-203, TH-203)."""
        user = await self._users.get_by_email(email)
        if user is None:
            await self._hasher.verify_dummy(password)
            raise InvalidCredentials("The email or password is incorrect.")
        if not await self._hasher.verify(user.password_hash, password):
            raise InvalidCredentials("The email or password is incorrect.")
        return self._tokens.issue(user.id, user.role.value, self._clock.now())

    async def authenticate(self, token: str) -> User:
        """The role is read from the store, so a demotion applies immediately (section 9)."""
        user = await self._users.get(self._tokens.subject(token, self._clock.now()))
        if user is None:
            raise Unauthenticated("The access token is missing, invalid or expired.")
        return user

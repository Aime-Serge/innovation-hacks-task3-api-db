"""Validated settings: a missing or invalid variable stops the app and names it (FR-227)."""

from typing import Annotated, Literal

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", case_sensitive=False, env_ignore_empty=True
    )

    app_env: Literal["development", "test", "production"] = "development"
    host: str = "127.0.0.1"  # the container command binds 0.0.0.0 explicitly; see Dockerfile
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    secret_key: SecretStr
    jwt_issuer: str = "devdash-api"
    jwt_audience: str = "devdash-clients"
    access_token_ttl_seconds: int = Field(default=900, ge=60, le=86_400)
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    docs_enabled: bool | None = None
    max_body_bytes: int = Field(default=1_048_576, ge=1_024)
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    rate_limit_attempts: int = Field(default=5, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    argon2_time_cost: int = Field(default=3, ge=1)
    argon2_memory_kib: int = Field(default=65_536, ge=8)
    seed_password: SecretStr | None = None
    seed_profile: Literal["none", "default", "empty", "large"] = "none"

    @field_validator("secret_key")
    @classmethod
    def _secret_is_long_enough(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode()) < 32:
            raise ValueError("must be at least 32 bytes long")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_origins")
    @classmethod
    def _no_wildcard(cls, value: list[str]) -> list[str]:
        if any(origin == "*" for origin in value):
            raise ValueError("a wildcard origin is not allowed; list explicit origins")
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def docs_on(self) -> bool:
        """Swagger UI and ReDoc: on in development, off in production unless set."""
        return (not self.is_production) if self.docs_enabled is None else self.docs_enabled


def load_settings() -> Settings:
    """Read settings from the environment or exit with a message naming each bad variable."""
    try:
        return Settings()
    except ValidationError as error:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in item['loc']).upper()}: {item['msg']}"
            for item in error.errors()
        )
        raise SystemExit(f"Invalid configuration. {problems}") from None

"""Shared fixtures: a real app, a controllable clock, fast hashing and seeded accounts."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from pydantic import SecretStr

from app.container import Container
from app.core.config import Settings
from app.main import create_app
from app.seed import seed
from tests.coverage_gate import gaps, recorder

PASSWORD = "Seeded-Password-123"  # a test fixture, never a real credential
SECRET = "test-only-secret-key-that-is-long-enough-0123456789"
NOW = datetime(2026, 9, 20, 12, 0, tzinfo=UTC)

LEAD = "amara.diallo@example.com"
DEV = "aime.serge@example.com"
OTHER = "kwame.mensah@example.com"


class FakeClock:
    def __init__(self, now: datetime = NOW) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def today(self) -> Any:
        return self._now.date()

    def advance(self, **delta: float) -> None:
        self._now += timedelta(**delta)


def make_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": "test",
        "secret_key": SecretStr(SECRET),
        "argon2_time_cost": 1,
        "argon2_memory_kib": 8,
        "rate_limit_attempts": 1000,
        "log_level": "error",
        "docs_enabled": True,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


@dataclass
class Env:
    app: FastAPI
    container: Container
    clock: FakeClock
    client: httpx.AsyncClient
    tokens: dict[str, str]

    def auth(self, who: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.tokens[who]}"}

    async def login(self, email: str, password: str = PASSWORD) -> httpx.Response:
        return await self.client.post(
            "/api/v1/auth/login", json={"email": email, "password": password}
        )


async def build_env(profile: str | None = "empty", **settings: Any) -> AsyncIterator[Env]:
    clock = FakeClock()
    app = create_app(make_settings(**settings), clock=clock)
    container: Container = app.state.container
    if profile is not None:
        await seed(container, profile, PASSWORD)
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        event_hooks={"response": [recorder(app.openapi())]},
    ) as client:
        env = Env(app, container, clock, client, {})
        for email in (LEAD, DEV, OTHER) if profile is not None else ():
            response = await env.login(email)
            env.tokens[email] = response.json()["accessToken"]
        yield env


@pytest.fixture
async def env() -> AsyncIterator[Env]:
    async for value in build_env("empty"):
        yield value


@pytest.fixture
async def seeded() -> AsyncIterator[Env]:
    async for value in build_env("default"):
        yield value


async def make_project(env: Env, who: str = DEV, **body: Any) -> dict[str, Any]:
    payload = {"name": "Atlas", **body}
    response = await env.client.post("/api/v1/projects", json=payload, headers=env.auth(who))
    assert response.status_code == 201, response.text
    result: dict[str, Any] = response.json()
    return result


async def make_task(env: Env, project_id: str, who: str = DEV, **body: Any) -> dict[str, Any]:
    payload = {"projectId": project_id, "title": "Write docs", **body}
    response = await env.client.post("/api/v1/tasks", json=payload, headers=env.auth(who))
    assert response.status_code == 201, response.text
    result: dict[str, Any] = response.json()
    return result


def error_code(response: httpx.Response) -> str:
    code: str = response.json()["error"]["code"]
    return code


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """On a full, green run, fail the session when an operation lacks a success or failure test."""
    config = session.config
    partial = config.option.keyword or config.option.markexpr or session.testsfailed
    if partial or any(a not in ("tests", "tests/") for a in config.args if not a.startswith("-")):
        return
    checked, missing = gaps(create_app(make_settings()).openapi())
    reporter = config.pluginmanager.get_plugin("terminalreporter")
    if reporter:
        reporter.write_line(f"endpoint coverage: {checked} operations, {len(missing)} gaps")
        for line in sorted(missing):
            reporter.write_line(f"  {line}")
    if missing:
        session.exitstatus = 1

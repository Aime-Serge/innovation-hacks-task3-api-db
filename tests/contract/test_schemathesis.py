"""TC-250 to TC-253: property-based contract testing of every operation with Schemathesis.

The app is seeded, so ids exist and the generated calls reach real code paths. Every
response must match the documented schema, status code and content type, and none may be a 5xx.
"""

import asyncio
from typing import Any

import pytest
import schemathesis
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.container import Container
from app.main import create_app
from app.seed import seed
from tests.conftest import LEAD, PASSWORD, make_settings

pytestmark = pytest.mark.contract


def build() -> tuple[FastAPI, str, str]:
    app = create_app(make_settings(rate_limit_attempts=1_000_000))
    container: Container = app.state.container
    asyncio.run(seed(container, "default", PASSWORD))
    with TestClient(app) as client:
        token: str = client.post(
            "/api/v1/auth/login", json={"email": LEAD, "password": PASSWORD}
        ).json()["accessToken"]
        headers = {"Authorization": f"Bearer {token}"}
        project_id: str = client.get("/api/v1/projects?pageSize=1", headers=headers).json()[
            "items"
        ][0]["id"]
    return app, token, project_id


APP, TOKEN, PROJECT_ID = build()
schema = schemathesis.openapi.from_asgi("/openapi.json", APP)
schema.config.generation.update(max_examples=25, database=None)


@schema.auth()
class BearerAuth:
    """Schemathesis' auth provider: it can still send no token or a bad one to prove the 401."""

    def get(self, case: Any, context: Any) -> str:
        return TOKEN

    def set(self, case: Any, data: str, context: Any) -> None:
        case.headers = case.headers or {}
        case.headers["Authorization"] = f"Bearer {data}"


def is_positive(case: Any) -> bool:
    generation = getattr(case.meta, "generation", None)
    return generation is None or "positive" in str(generation.mode).lower()


@schema.parametrize()
def test_tc250_every_operation_conforms_to_its_documented_contract(case: Any) -> None:
    body = case.body if isinstance(case.body, dict) else {}
    if is_positive(case) and case.path == "/api/v1/tasks" and case.method == "POST":
        # A random projectId never exists, and "unknown reference" is a documented 422 (FR-214).
        # Point it at a real one so the schema-valid case is exercised end to end.
        body["projectId"] = PROJECT_ID
    if is_positive(case) and "assigneeId" in body:
        body["assigneeId"] = None
    case.call_and_validate()

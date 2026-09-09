import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.project_repo import project_repository
from app.repositories.task_repo import task_repository
from app.repositories.user_repo import user_repository


@pytest.fixture(autouse=True)
def reset_repositories():
    user_repository._users.clear()
    project_repository._projects.clear()
    task_repository._tasks.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user(client):
    return client.post(
        "/users",
        json={"name": "Ada Lovelace", "email": "ada@example.com", "password": "supersecret"},
    ).json()


@pytest.fixture
def project(client, user):
    return client.post(
        "/projects",
        json={"name": "Analytical Engine", "description": "A project", "owner_id": user["id"]},
    ).json()

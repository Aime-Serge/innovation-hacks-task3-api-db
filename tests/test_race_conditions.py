"""Every write route does a "check the referenced/target row exists,
then act on it" in two separate transactions (session_scope() opens and
closes once per repository call, not once per request) — a real window
for another request to invalidate that check before the follow-up call
runs. These tests simulate that window by monkeypatching the pre-check
to lie about the database's real state, then confirm the database's own
constraints (unique email, FK) are what correctly turn the request into
a clean 4xx instead of an uncaught 500.
"""

from uuid import UUID

from app.db.models import ProjectModel, UserModel
from app.db.session import session_scope
from app.models.user import UserInDB
from app.repositories.project_repo import project_repository
from app.repositories.user_repo import user_repository


def test_create_user_duplicate_email_race_returns_409_not_500(client, monkeypatch):
    monkeypatch.setattr(user_repository, "get_by_email", lambda email: None)

    payload = {"name": "Ada", "email": "ada-race@example.com", "password": "supersecret"}
    r1 = client.post("/users", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/users", json=payload)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "conflict"


def test_update_user_email_race_returns_409_not_500(client, user, monkeypatch):
    other = client.post(
        "/users",
        json={"name": "Bob", "email": "bob-race@example.com", "password": "supersecret"},
    ).json()

    monkeypatch.setattr(user_repository, "get_by_email", lambda email: None)

    r = client.patch(f"/users/{other['id']}", json={"email": user["email"]})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "conflict"


def test_update_user_deleted_between_check_and_update_returns_404_not_500(
    client, user, monkeypatch
):
    real_user_id = UUID(user["id"])
    with session_scope() as session:
        row = session.get(UserModel, real_user_id)
        session.delete(row)

    stale = UserInDB(
        id=real_user_id, name=user["name"], email=user["email"], password_hash="irrelevant"
    )
    monkeypatch.setattr(user_repository, "get", lambda uid: stale)

    r = client.patch(f"/users/{user['id']}", json={"name": "New Name"})
    assert r.status_code == 404


def test_create_project_owner_deleted_between_check_and_insert_returns_404_not_500(
    client, user, monkeypatch
):
    with session_scope() as session:
        row = session.get(UserModel, UUID(user["id"]))
        session.delete(row)

    # The pre-check just needs a truthy value here.
    monkeypatch.setattr(user_repository, "get", lambda uid: object())

    r = client.post(
        "/projects", json={"name": "P", "description": None, "owner_id": user["id"]}
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_create_task_project_deleted_between_check_and_insert_returns_404_not_500(
    client, project, monkeypatch
):
    with session_scope() as session:
        row = session.get(ProjectModel, UUID(project["id"]))
        session.delete(row)

    monkeypatch.setattr(project_repository, "get", lambda pid: object())

    r = client.post("/tasks", json={"title": "T", "project_id": project["id"]})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"

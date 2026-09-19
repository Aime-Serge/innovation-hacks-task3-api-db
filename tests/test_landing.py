from app.main import TASK_REQUIREMENTS


def test_root_serves_html_landing_page_not_an_error(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "Users, Projects &amp; Tasks API" in r.text


def test_landing_page_maps_every_task_requirement_and_offers_live_checks(client):
    body = client.get("/").text
    assert 'id="run"' in body and "Live verification" in body
    for requirement, _how in TASK_REQUIREMENTS:
        assert requirement in body


def test_landing_page_lists_the_project_update_and_delete_routes(client):
    body = client.get("/").text
    assert "/projects/{project_id}" in body and 'href="/docs"' in body


def test_landing_page_leaves_no_unfilled_template_tokens(client):
    assert "__" not in client.get("/").text.replace("__init__", "")


def test_landing_page_is_not_in_the_openapi_schema(client):
    assert "/" not in client.get("/openapi.json").json()["paths"]


def test_unknown_routes_still_use_the_error_contract(client):
    r = client.get("/nope")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"


def test_public_base_url_forces_https_for_non_local_hosts():
    from app.landing import public_base_url
    assert public_base_url("ih-task3-api.onrender.com", "http") == "https://ih-task3-api.onrender.com"
    assert public_base_url("localhost:8000", "http") == "http://localhost:8000"

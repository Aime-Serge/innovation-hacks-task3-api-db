def test_unmatched_route_returns_wrapped_error_shape_not_default_detail(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json() == {
        "error": {"code": "not_found", "message": "Not Found", "details": None}
    }


def test_wrong_http_method_returns_wrapped_error_shape_not_default_detail(client, user):
    # POST /users/{id} isn't a route — only GET/PATCH/DELETE are — so this
    # exercises Starlette's own 405, not an application-raised AppError.
    r = client.post(f"/users/{user['id']}", json={})
    assert r.status_code == 405
    assert r.json()["error"]["code"] == "method_not_allowed"
    assert "detail" not in r.json()

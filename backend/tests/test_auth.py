def test_login_invalid_credentials(client):
    resp = client.post("/api/auth/login", json={"email": "wrong@x.dev", "password": "wrong"})
    assert resp.status_code == 401


def test_login_valid(client):
    resp = client.post("/api/auth/login", json={"email": "editor@semyainfo.dev", "password": "editor123"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_role(client, editor_token):
    resp = client.get("/api/auth/me", headers=auth(editor_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "editor"
    assert body["email"] == "editor@semyainfo.dev"


def test_profile_update(client, editor_token):
    resp = client.patch("/api/auth/me", headers=auth(editor_token), json={"first_name": "НовоеИмя"})
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "НовоеИмя"


def test_change_password_flow(client, editor_token):
    resp = client.post(
        "/api/auth/change-password",
        headers=auth(editor_token),
        json={"current_password": "editor123", "new_password": "newpass123"},
    )
    assert resp.status_code == 200
    # revert
    client.post(
        "/api/auth/change-password",
        headers=auth(editor_token),
        json={"current_password": "newpass123", "new_password": "editor123"},
    )


def auth(token):
    return {"Authorization": f"Bearer {token}"}
def test_admin_creates_editor(client, admin_token):
    resp = client.post(
        "/api/admin/editors",
        headers=auth(admin_token),
        json={
            "first_name": "Новый",
            "last_name": "Редактор",
            "email": "novyy@semyainfo.dev",
            "password": "secret123",
            "role": "editor",
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "editor"
    return resp.json()


def test_admin_lists_editors(client, admin_token):
    resp = client.get("/api/admin/editors", headers=auth(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_logs(client, admin_token):
    resp = client.get("/api/admin/logs", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_admin_deactivates_editor(client, admin_token):
    import uuid

    email = f"deact-{uuid.uuid4().hex[:8]}@semyainfo.dev"
    created = client.post(
        "/api/admin/editors",
        headers=auth(admin_token),
        json={
            "first_name": "Дел",
            "last_name": "Редактор",
            "email": email,
            "password": "secret123",
            "role": "editor",
        },
    ).json()
    resp = client.delete(f"/api/admin/editors/{created['id']}", headers=auth(admin_token))
    assert resp.status_code == 200
    login = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    assert login.status_code == 403


def test_ai_settings_access(client, admin_token, editor_token):
    resp = client.get("/api/admin/ai/settings", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["model"]
    patch = client.patch(
        "/api/admin/ai/settings",
        headers=auth(admin_token),
        json={"temperature": 0.9},
    )
    assert patch.status_code == 200
    assert patch.json()["temperature"] == 0.9
    # editor forbidden
    assert client.get("/api/admin/ai/settings", headers=auth(editor_token)).status_code == 403


def auth(token):
    return {"Authorization": f"Bearer {token}"}
def _create_article(client, token):
    resp = client.post(
        "/api/editor/articles",
        headers=auth(token),
        json={
            "title": "Тестовая статья для покрытия",
            "summary": "Краткое описание тестовой статьи",
            "content": "Полное содержание статьи",
            "category": "Тест",
            "status": "draft",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_editor_can_create(client, editor_token):
    created = _create_article(client, editor_token)
    assert created["slug"]
    assert created["status"] == "draft"


def test_editor_can_update(client, editor_token):
    created = _create_article(client, editor_token)
    resp = client.patch(
        f"/api/editor/articles/{created['id']}",
        headers=auth(editor_token),
        json={"title": "Обновлённый заголовок"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Обновлённый заголовок"


def test_editor_can_publish_and_delete(client, editor_token):
    created = _create_article(client, editor_token)
    pub = client.post(f"/api/editor/articles/{created['id']}/publish", headers=auth(editor_token))
    assert pub.status_code == 200
    assert pub.json()["status"] == "published"
    # article now visible publicly
    resp = client.get("/api/articles", params={"q": "Тестовая статья"})
    assert resp.json()["total"] >= 1
    # delete
    dele = client.delete(f"/api/editor/articles/{created['id']}", headers=auth(editor_token))
    assert dele.status_code == 200


def test_role_enforcement(client, editor_token):
    # editor cannot access admin endpoints
    resp = client.get("/api/admin/editors", headers=auth(editor_token))
    assert resp.status_code == 403


def test_anonymous_cannot_create(client):
    assert client.post("/api/editor/articles", json={"title": "x"}).status_code == 401


def auth(token):
    return {"Authorization": f"Bearer {token}"}
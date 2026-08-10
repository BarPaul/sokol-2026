def test_create_chat(client):
    resp = client.post("/api/assistant/chats", json={"title": "Тестовый чат"})
    assert resp.status_code == 200, resp.text
    chat = resp.json()
    assert chat["session_id"]
    return chat


def test_list_chats(client):
    test_create_chat(client)
    resp = client.get("/api/assistant/chats")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_messages(client):
    chat = test_create_chat(client)
    resp = client.get(f"/api/assistant/chats/{chat['id']}/messages")
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_chat(client):
    chat = test_create_chat(client)
    resp = client.delete(f"/api/assistant/chats/{chat['id']}")
    assert resp.status_code == 200
    assert client.get(f"/api/assistant/chats/{chat['id']}").status_code == 404
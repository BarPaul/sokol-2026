def test_list_published_articles(client):
    resp = client.get("/api/articles")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 5
    for item in body["items"]:
        assert item.get("slug")


def test_get_article_by_slug(client):
    resp = client.get("/api/articles/posobie-studencheskim-semyam")
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"]


def test_get_article_404(client):
    assert client.get("/api/articles/ne-suschestvuet").status_code == 404


def test_categories(client):
    resp = client.get("/api/articles/categories")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_search(client):
    resp = client.get("/api/articles/search", params={"q": "пособие"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_search_empty(client):
    resp = client.get("/api/articles/search", params={"q": "zzzz-not-exists"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_search_rejects_nonsense(client):
    resp = client.get("/api/articles/search", params={"q": "абсолютный бред"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_search_typo_tolerant(client):
    resp = client.get("/api/articles/search", params={"q": "пасабие"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
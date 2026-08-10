from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.article import Article
from app.services.articles.article_service import serialize_article
from app.services.knowledge.knowledge_service import KnowledgeService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(
    db: Annotated[Session, Depends(get_db)],
    category: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Поисковый запрос"),
    sort: str = Query(default="updated", pattern="^(updated|created|title)$"),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Article).where(Article.status == "published")
    count_stmt = select(func.count(Article.id)).where(Article.status == "published")
    if category:
        stmt = stmt.where(Article.category == category)
        count_stmt = count_stmt.where(Article.category == category)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            Article.title.ilike(like)
            | Article.summary.ilike(like)
            | Article.content.ilike(like)
        )
        count_stmt = count_stmt.where(
            Article.title.ilike(like)
            | Article.summary.ilike(like)
            | Article.content.ilike(like)
        )
    if sort == "title":
        stmt = stmt.order_by(Article.title.asc())
    elif sort == "created":
        stmt = stmt.order_by(Article.created_at.desc())
    else:
        stmt = stmt.order_by(Article.updated_at.desc())
    total = db.scalar(count_stmt) or 0
    items = list(db.scalars(stmt.offset(offset).limit(limit)))
    return {
        "items": [_card(a) for a in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def _card(a: Article) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "slug": a.slug,
        "summary": a.summary,
        "category": a.category,
        "updated_at": a.updated_at,
    }


@router.get("/categories")
def list_categories(db: Annotated[Session, Depends(get_db)]):
    rows = db.execute(
        select(Article.category, func.count(Article.id))
        .where(Article.status == "published")
        .group_by(Article.category)
    ).all()
    return [
        {"name": name or "Без категории", "count": count}
        for name, count in rows if name
    ]


@router.get("/search")
def search_articles(
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(default="", min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Text search across articles. Falls back to LIKE when FTS unavailable."""
    q = q.strip()
    if not q:
        return {"items": [], "total": 0}
    hits = KnowledgeService(db).search(q)
    result = []
    seen: set[int] = set()
    for h in hits:
        if h.get("doc_type") == "article":
            article = db.scalar(select(Article).where(Article.id == h["doc_id"]))
            if article and article.id not in seen:
                result.append(_card(article))
                seen.add(article.id)
        if len(result) >= limit:
            break
    if not result:
        like = f"%{q}%"
        stmt = (
            select(Article)
            .where(
                Article.status == "published",
                Article.title.ilike(like)
                | Article.summary.ilike(like)
                | Article.content.ilike(like),
            )
            .order_by(Article.updated_at.desc())
            .limit(limit)
        )
        result = [_card(a) for a in db.scalars(stmt)]
    return {"items": result, "total": len(result)}


@router.get("/{slug}")
def get_article(slug: str, db: Annotated[Session, Depends(get_db)]):
    article = db.scalar(select(Article).where(Article.slug == slug, Article.status == "published"))
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    related = list(
        db.scalars(
            select(Article)
            .where(
                Article.status == "published",
                Article.category == article.category,
                Article.id != article.id,
            )
            .order_by(Article.updated_at.desc())
            .limit(3)
        )
    )
    return {**serialize_article(article), "related": [_card(a) for a in related]}
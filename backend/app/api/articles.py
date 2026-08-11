from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.article import Article
from app.models.category import Category
from app.services.articles.article_service import reading_minutes, serialize_article
from app.services.knowledge.knowledge_service import KnowledgeService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(
    db: Annotated[Session, Depends(get_db)],
    category: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Поисковый запрос"),
    sort: str = Query(default="updated", pattern="^(updated|created|title)$"),
    period: str | None = Query(default=None, pattern="^(week|month|3months|year)$"),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    import datetime as dt

    from app.services.articles.article_service import _norm_contains, article_search_text

    stmt = select(Article).where(Article.status == "published")
    count_stmt = select(func.count(Article.id)).where(Article.status == "published")
    if category:
        stmt = stmt.where(Article.category == category)
        count_stmt = count_stmt.where(Article.category == category)
    if period:
        days = {"week": 7, "month": 30, "3months": 90, "year": 365}[period]
        since = dt.datetime.now(dt.timezone.utc).astimezone().replace(tzinfo=None) - dt.timedelta(days=days)
        stmt = stmt.where(Article.updated_at >= since)
        count_stmt = count_stmt.where(Article.updated_at >= since)
    if q:
        # SQLite ilike/lower не работают с кириллицей — фильтруем регистронезависимо в Python.
        all_matching = [
            a for a in db.scalars(stmt)
            if _norm_contains(q, article_search_text(a))
        ]
        if sort == "title":
            all_matching.sort(key=lambda a: (a.title or "").lower())
        elif sort == "created":
            all_matching.sort(key=lambda a: a.created_at, reverse=True)
        elif sort == "views":
            all_matching.sort(key=lambda a: (a.views or 0), reverse=True)
        else:
            all_matching.sort(key=lambda a: a.updated_at, reverse=True)
        total = len(all_matching)
        items = all_matching[offset : offset + limit]
        return {
            "items": [_card(a) for a in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    if sort == "title":
        stmt = stmt.order_by(Article.title.asc())
    elif sort == "created":
        stmt = stmt.order_by(Article.created_at.desc())
    elif sort == "views":
        stmt = stmt.order_by(Article.views.desc())
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
        "published_at": a.published_at,
        "views": a.views,
        "reading_minutes": reading_minutes(a),
    }


@router.get("/categories")
def list_categories(db: Annotated[Session, Depends(get_db)]):
    """Категории из справочника (заполняет администратор)."""
    cats = db.scalars(
        select(Category).order_by(Category.sort_order, Category.name)
    ).all()
    counts = dict(
        db.execute(
            select(Article.category, func.count(Article.id))
            .where(Article.status == "published")
            .group_by(Article.category)
        ).all()
    )
    result = [
        {"name": c.name, "count": counts.get(c.name, 0)} for c in cats
    ]
    # fallback: категории, которые ещё не заведены в справочнике
    known = {c.name for c in cats}
    for name, count in db.execute(
        select(Article.category, func.count(Article.id))
        .where(Article.status == "published")
        .group_by(Article.category)
    ).all():
        if name and name not in known:
            result.append({"name": name, "count": count})
    return result


@router.get("/search")
def search_articles(
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(default="", min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Text search across articles (content + typos tolerated)."""
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
    if result:
        from app.services.articles.article_service import fuzzy_score

        ordered = {a["id"]: fuzzy_score(q, f"{a['title']} {a['summary']}") for a in result}
        result.sort(key=lambda a: ordered[a["id"]], reverse=True)
        return {"items": result, "total": len(result)}
    # FTS не нашёл — пробуем устойчивый к опечаткам поиск по публичным статьям
    from app.services.articles.article_service import fuzzy_match_articles

    items = fuzzy_match_articles(db, q, published_only=True, limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/{slug}")
def get_article(slug: str, db: Annotated[Session, Depends(get_db)]):
    article = db.scalar(select(Article).where(Article.slug == slug, Article.status == "published"))
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    article.views = (article.views or 0) + 1
    db.commit()
    db.refresh(article)
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
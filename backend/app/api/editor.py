from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_account, require_role
from app.db.session import get_db
from app.models.account import Account
from app.models.article import Article
from app.schemas.article import (
    ArticleCreate,
    ArticleOut,
    ArticleUpdate,
    CoauthorAdd,
)
from app.services.articles.article_service import ArticleService, serialize_article
from app.services.knowledge.knowledge_service import KnowledgeService

router = APIRouter(prefix="/editor/articles", tags=["editor"])
editor_only = require_role("editor", "moderator")


@router.get("")
def list_editor_articles(
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    if account.role.name == "moderator":
        stmt = select(Article)
    else:
        stmt = select(Article).where(
            or_(Article.author_id == account.id, Article.coauthors.any(id=account.id))
        )
    sub = stmt.subquery()
    count_stmt = select(func.count()).select_from(sub)
    if status:
        stmt = stmt.where(Article.status == status)
    if category:
        stmt = stmt.where(Article.category == category)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(Article.title.ilike(like) | Article.summary.ilike(like))
    items = list(db.scalars(stmt.order_by(Article.updated_at.desc()).offset(offset).limit(limit)))
    total = db.scalar(count_stmt) or 0
    return {"items": [serialize_article(a) for a in items], "total": total}


@router.post("", response_model=ArticleOut)
def create_editor_article(
    payload: ArticleCreate,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.create(account, payload)
    if article.status == "published":
        KnowledgeService(db).sync_article(
            article.id, article.title, f"{article.summary}\n{article.audience}\n{article.documents}\n{article.content}", article.category
        )
    return serialize_article(article)


@router.get("/{article_id}", response_model=ArticleOut)
def get_editor_article(
    article_id: int,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.get_editorial(account, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return serialize_article(article)


@router.patch("/{article_id}", response_model=ArticleOut)
def update_editor_article(
    article_id: int,
    payload: ArticleUpdate,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.get_editorial(account, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    updated = service.update(account, article_id, payload)
    knowledge = KnowledgeService(db)
    if updated.status == "published":
        knowledge.sync_article(
            updated.id, updated.title, f"{updated.summary}\n{updated.audience}\n{updated.documents}\n{updated.content}", updated.category
        )
    else:
        knowledge.remove_article(updated.id)
    return serialize_article(updated)


@router.post("/{article_id}/publish", response_model=ArticleOut)
def publish_editor_article(
    article_id: int,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.get_editorial(account, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    published = service.publish(account, article_id)
    KnowledgeService(db).sync_article(
        published.id, published.title, f"{published.summary}\n{published.audience}\n{published.documents}\n{published.content}", published.category
    )
    return serialize_article(published)


@router.delete("/{article_id}")
def delete_editor_article(
    article_id: int,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.get_editorial(account, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    service.delete(account, article_id)
    KnowledgeService(db).remove_article(article_id)
    return {"status": "ok"}


@router.post("/{article_id}/coauthors", response_model=ArticleOut)
def add_coauthor(
    article_id: int,
    payload: CoauthorAdd,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.get_editorial(account, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    updated = service.add_coauthor(account, article_id, payload.account_id)
    return serialize_article(updated)


@router.delete("/{article_id}/coauthors/{coauthor_id}", response_model=ArticleOut)
def remove_coauthor(
    article_id: int,
    coauthor_id: int,
    account: Annotated[Account, Depends(editor_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = ArticleService(db)
    article = service.get_editorial(account, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    updated = service.remove_coauthor(account, article_id, coauthor_id)
    return serialize_article(updated)
import datetime as dt
import re
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.article import Article
from app.models.log import Log
from app.schemas.article import ArticleCreate, ArticleUpdate


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-zа-яё0-9\s-]", "", slug, flags=re.IGNORECASE)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "article"


def ensure_unique_slug(db: Session, title: str, exclude_id: int | None = None) -> str:
    base = slugify(title)
    candidate = base
    n = 1
    while True:
        stmt = select(Article).where(Article.slug == candidate)
        if exclude_id is not None:
            stmt = stmt.where(Article.id != exclude_id)
        if db.scalar(stmt) is None:
            return candidate
        n += 1
        candidate = f"{base}-{n}"


def serialize_article(article: Article) -> dict[str, Any]:
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "content": article.content,
        "audience": article.audience,
        "documents": article.documents,
        "category": article.category,
        "region": article.region,
        "official_source": article.official_source,
        "restrictions": article.restrictions,
        "status": article.status,
        "author_id": article.author_id,
        "author_name": f"{article.author.first_name} {article.author.last_name}",
        "created_at": article.created_at,
        "updated_at": article.updated_at,
        "published_at": article.published_at,
        "coauthors": [
            {
                "id": a.id,
                "first_name": a.first_name,
                "last_name": a.last_name,
                "email": a.email,
            }
            for a in article.coauthors
        ],
    }


def to_card(article: Article) -> dict[str, Any]:
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "category": article.category,
        "updated_at": article.updated_at,
    }


class ArticleService:
    def __init__(self, db: Session):
        self.db = db

    def log(self, account: Account, action: str, entity: str, entity_id: int | None, description: str = "", **meta) -> None:
        self.db.add(
            Log(
                account_id=account.id,
                action=action,
                entity_type=entity,
                entity_id=entity_id,
                description=description,
                metadata=meta,
            )
        )
        self.db.commit()

    def create(self, account: Account, payload: ArticleCreate) -> Article:
        article = Article(
            title=payload.title.strip(),
            slug=ensure_unique_slug(self.db, payload.title),
            summary=payload.summary,
            content=payload.content,
            audience=payload.audience,
            documents=payload.documents,
            category=payload.category,
            region=payload.region,
            official_source=payload.official_source,
            restrictions=payload.restrictions,
            status=payload.status,
            author_id=account.id,
            published_at=dt.datetime.utcnow() if payload.status == "published" else None,
        )
        self.db.add(article)
        self.db.flush()
        self.log(account, "article.created", "article", article.id, f"Статья создана: {article.title}")
        self.db.commit()
        self.db.refresh(article)
        return article

    def get_editorial(self, account: Account, article_id: int) -> Article | None:
        article = self.db.get(Article, article_id)
        if article is None:
            return None
        if account.role.name == "moderator":
            return article
        if article.author_id == account.id:
            return article
        if account in article.coauthors:
            return article
        return None

    def update(self, account: Account, article_id: int, payload: ArticleUpdate) -> Article | None:
        article = self.db.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Статья не найдена")
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            return article
        if "title" in changes:
            article.title = changes["title"].strip()
            article.slug = ensure_unique_slug(self.db, article.title, exclude_id=article.id)
        for field in ("summary", "content", "audience", "documents", "category", "region", "official_source", "restrictions"):
            if field in changes:
                setattr(article, field, changes[field])
        old_status = article.status
        new_status = changes.get("status", old_status)
        if new_status == "published" and old_status != "published":
            article.published_at = dt.datetime.utcnow()
        if new_status != old_status:
            article.status = new_status
        self.log(account, "article.updated", "article", article.id, f"Статья обновлена: {article.title}")
        self.db.commit()
        self.db.refresh(article)
        return article

    def publish(self, account: Account, article_id: int) -> Article | None:
        article = self.db.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Статья не найдена")
        article.status = "published"
        if article.published_at is None:
            article.published_at = dt.datetime.utcnow()
        self.log(account, "article.published", "article", article.id, f"Статья опубликована: {article.title}")
        self.db.commit()
        self.db.refresh(article)
        return article

    def delete(self, account: Account, article_id: int) -> None:
        article = self.db.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Статья не найдена")
        title = article.title
        self.db.delete(article)
        self.log(account, "article.deleted", "article", article_id, f"Статья удалена: {title}")
        self.db.commit()

    def add_coauthor(self, account: Account, article_id: int, coauthor_id: int) -> Article:
        article = self.db.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Статья не найдена")
        if article.author_id == coauthor_id:
            raise HTTPException(status_code=400, detail="Автор уже является основным автором")
        coauthor = self.db.get(Account, coauthor_id)
        if coauthor is None:
            raise HTTPException(status_code=404, detail="Редактор не найден")
        if coauthor.role.name != "editor":
            raise HTTPException(status_code=400, detail="Соавтором может быть только редактор")
        if coauthor not in article.coauthors:
            article.coauthors.append(coauthor)
            self.log(
                account,
                "coauthor.added",
                "article",
                article.id,
                f"Добавлен соавтор: {coauthor.email}",
                coauthor_id=coauthor.id,
            )
            self.db.commit()
            self.db.refresh(article)
        return article

    def remove_coauthor(self, account: Account, article_id: int, coauthor_id: int) -> Article:
        article = self.db.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Статья не найдена")
        coauthor = next((a for a in article.coauthors if a.id == coauthor_id), None)
        if coauthor is None:
            raise HTTPException(status_code=404, detail="Соавтор не найден")
        article.coauthors.remove(coauthor)
        self.log(
            account,
            "coauthor.removed",
            "article",
            article.id,
            f"Удалён соавтор: {coauthor.email}",
            coauthor_id=coauthor.id,
        )
        self.db.commit()
        self.db.refresh(article)
        return article
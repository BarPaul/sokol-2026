import datetime as dt
import re

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate

FTS_CREATE = """
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_search USING fts5(
    doc_id UNINDEXED,
    doc_type UNINDEXED,
    title,
    content,
    category,
    tokenize = 'unicode61 remove_diacritics 2'
)
"""

FTS_T_AI = """
CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge_documents BEGIN
    INSERT INTO knowledge_search(doc_id, doc_type, title, content, category)
    VALUES (new.id, 'knowledge', new.title, new.content, new.category);
END;
"""

FTS_T_AD = """
CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge_documents BEGIN
    INSERT INTO knowledge_search(knowledge_search, doc_id, doc_type, title, content, category)
    VALUES ('delete', old.id, 'knowledge', old.title, old.content, old.category);
END;
"""

FTS_T_AU = """
CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge_documents BEGIN
    INSERT INTO knowledge_search(knowledge_search, doc_id, doc_type, title, content, category)
    VALUES ('delete', old.id, 'knowledge', old.title, old.content, old.category);
    INSERT INTO knowledge_search(doc_id, doc_type, title, content, category)
    VALUES (new.id, 'knowledge', new.title, new.content, new.category);
END;
"""


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db

    def ensure_fts(self) -> None:
        self.db.execute(text(FTS_CREATE))
        for trigger in (FTS_T_AI, FTS_T_AD, FTS_T_AU):
            self.db.execute(text(trigger))
        self.db.commit()

    def list_active(self) -> list[KnowledgeDocument]:
        return list(
            self.db.scalars(
                select(KnowledgeDocument).where(KnowledgeDocument.is_active == True)  # noqa: E712
            )
        )

    def list_all(self, search: str = "") -> list[KnowledgeDocument]:
        stmt = select(KnowledgeDocument).order_by(KnowledgeDocument.updated_at.desc())
        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                KnowledgeDocument.title.ilike(like)
                | KnowledgeDocument.content.ilike(like)
                | KnowledgeDocument.category.ilike(like)
            )
        return list(self.db.scalars(stmt))

    def get(self, doc_id: int) -> KnowledgeDocument:
        doc = self.db.get(KnowledgeDocument, doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Документ не найден")
        return doc

    def create(self, payload: KnowledgeCreate) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            title=payload.title.strip(),
            content=payload.content,
            source=payload.source,
            category=payload.category,
            is_active=payload.is_active,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def update(self, doc_id: int, payload: KnowledgeUpdate) -> KnowledgeDocument:
        doc = self.get(doc_id)
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            if field == "title" and value is not None:
                value = value.strip()
            setattr(doc, field, value)
        doc.updated_at = dt.datetime.utcnow()
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete(self, doc_id: int) -> None:
        doc = self.get(doc_id)
        self.db.delete(doc)
        self.db.commit()

    def sync_article(self, article_id: int, title: str, content: str, category: str) -> None:
        """Индексирует опубликованную статью в FTS (upsert по doc_id/doc_type)."""
        self.db.execute(text("DELETE FROM knowledge_search WHERE doc_id = :id AND doc_type = 'article'"), {"id": article_id})
        self.db.execute(
            text(
                "INSERT INTO knowledge_search(doc_id, doc_type, title, content, category) "
                "VALUES (:id, 'article', :title, :content, :category)"
            ),
            {"id": article_id, "title": title, "content": content, "category": category},
        )
        self.db.commit()

    def remove_article(self, article_id: int) -> None:
        self.db.execute(text("DELETE FROM knowledge_search WHERE doc_id = :id AND doc_type = 'article'"), {"id": article_id})
        self.db.commit()

    def reindex(self) -> int:
        """Полная перестройка FTS-индекса из активных документов и опубликованных статей."""
        self.db.execute(text("DELETE FROM knowledge_search"))
        count = 0
        for doc in self.list_active():
            self.db.execute(
                text(
                    "INSERT INTO knowledge_search(doc_id, doc_type, title, content, category) "
                    "VALUES (:id, 'knowledge', :title, :content, :category)"
                ),
                {"id": doc.id, "title": doc.title, "content": doc.content, "category": doc.category},
            )
            count += 1
        from app.models.article import Article

        articles = list(
            self.db.scalars(select(Article).where(Article.status == "published"))
        )
        for article in articles:
            self.db.execute(
                text(
                    "INSERT INTO knowledge_search(doc_id, doc_type, title, content, category) "
                    "VALUES (:id, 'article', :title, :content, :category)"
                ),
                {
                    "id": article.id,
                    "title": article.title,
                    "content": f"{article.summary}\n{article.content}",
                    "category": article.category,
                },
            )
            count += 1
        self.db.commit()
        return count

    def search(self, query: str) -> list[dict]:
        """Поиск по FTS5 по документам и опубликованным статьям."""
        if not query.strip():
            return []
        q = query.strip()
        rows = self._fts_search(q)
        if rows:
            return rows
        tokens = [t for t in re.split(r"[^\wа-яё]+", q, flags=re.IGNORECASE) if len(t) >= 3]
        if not tokens:
            return []
        or_query = " OR ".join(f'"{t}"' for t in tokens)
        return self._fts_search(or_query)

    def _fts_search(self, q: str) -> list[dict]:
        try:
            rows = self.db.execute(
                text(
                    "SELECT doc_id, doc_type, title, content, category "
                    "FROM knowledge_search WHERE knowledge_search MATCH :q "
                    "ORDER BY bm25(knowledge_search) LIMIT :limit"
                ),
                {"q": q, "limit": settings.ai_knowledge_top_k},
            ).mappings()
            return [dict(r) for r in rows]
        except Exception:
            return []
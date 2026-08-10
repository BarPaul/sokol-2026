"""AssistantService: builds context, calls AI, persists messages, returns recommended articles."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.article import Article
from app.models.chat import Chat
from app.models.knowledge import AISettings
from app.models.message import Message
from app.services.ai.provider import get_provider
from app.services.knowledge.knowledge_service import KnowledgeService

DEFAULT_SYSTEM_PROMPT = """Ты — справочный AI-ассистент проекта СтудСемья.

Отвечай на основании предоставленной базы знаний.
Не придумывай льготы, суммы, сроки или нормативные положения.
Если в базе знаний недостаточно информации, явно сообщи об этом.
Не выдавай себя за юриста.
В конце ответа рекомендуй релевантные материалы, если они найдены."""


class AssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.knowledge = KnowledgeService(db)

    def _settings(self) -> AISettings:
        row = self.db.scalar(select(AISettings).limit(1))
        if row is None:
            row = AISettings(system_prompt=DEFAULT_SYSTEM_PROMPT)
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
        return row

    def create_chat(self, session_id: str, title: str = "Новый диалог") -> Chat:
        chat = Chat(session_id=session_id, title=title)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def list_chats(self, session_id: str) -> list[Chat]:
        return list(
            self.db.scalars(
                select(Chat)
                .where(Chat.session_id == session_id)
                .order_by(Chat.updated_at.desc())
            )
        )

    def get_chat(self, session_id: str, chat_id: int) -> Chat:
        chat = self.db.get(Chat, chat_id)
        if chat is None or chat.session_id != session_id:
            raise HTTPException(status_code=404, detail="Диалог не найден")
        return chat

    def delete_chat(self, session_id: str, chat_id: int) -> None:
        chat = self.get_chat(session_id, chat_id)
        self.db.delete(chat)
        self.db.commit()

    def messages(self, chat_id: int) -> list[Message]:
        return list(
            self.db.scalars(
                select(Message).where(Message.chat_id == chat_id).order_by(Message.id)
            )
        )

    def ask(self, session_id: str, chat_id: int, content: str) -> tuple[Message, list[Article]]:
        chat = self.get_chat(session_id, chat_id)
        user_msg = Message(chat_id=chat.id, role="user", content=content)
        self.db.add(user_msg)
        self.db.commit()
        self.db.refresh(user_msg)

        st = self._settings()
        history = self.messages(chat.id)
        knowledge_enabled = st.knowledge_enabled and bool(settings.opencode_config_ready)

        context_blocks: list[str] = []
        if knowledge_enabled:
            hits = self.knowledge.search(content)
            for h in hits:
                context_blocks.append(f"[{h['doc_type']}] {h['title']}:\n{h['content'][:2000]}")

        messages = [{"role": "system", "content": st.system_prompt or DEFAULT_SYSTEM_PROMPT}]
        if context_blocks:
            messages.append(
                {
                    "role": "system",
                    "content": "База знаний:\n" + "\n\n---\n\n".join(context_blocks),
                }
            )
        for m in history[-12:]:
            messages.append({"role": m.role, "content": m.content})

        if not settings.opencode_config_ready:
            raise HTTPException(
                status_code=503,
                detail="AI-помощник временно недоступен. Проверьте настройки AI (OPENCODE_API_KEY / OPENCODE_BASE_URL).",
            )

        try:
            provider = get_provider()
            reply = provider.generate(
                messages,
                model=st.model,
                temperature=st.temperature,
                max_tokens=st.max_tokens,
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail="AI-помощник временно недоступен.") from exc

        assistant_msg = Message(chat_id=chat.id, role="assistant", content=reply)
        self.db.add(assistant_msg)
        chat.title = content[:60] if len(chat.title) < 5 or chat.title == "Новый диалог" else chat.title
        self.db.commit()
        self.db.refresh(assistant_msg)

        recommended: list[Article] = []
        hits = self.knowledge.search(content)
        seen: set[str] = set()
        for h in hits:
            if h["doc_type"] == "article":
                slug = h.get("title", "").strip()
                if slug and slug not in seen:
                    article = self.db.scalar(select(Article).where(Article.slug == slug))
                    if article and article.status == "published":
                        recommended.append(article)
                        seen.add(slug)
            if len(recommended) >= 3:
                break
        return assistant_msg, recommended
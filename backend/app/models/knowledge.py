import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(500), default="")
    category: Mapped[str] = mapped_column(String(100), default="", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )


class AISettings(Base):
    __tablename__ = "ai_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str] = mapped_column(String(100), default="Deepseek-v4-flash")
    temperature: Mapped[float] = mapped_column(Float, default=0.2)
    max_tokens: Mapped[int] = mapped_column(Integer, default=1024)
    knowledge_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )
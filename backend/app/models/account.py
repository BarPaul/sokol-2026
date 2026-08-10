from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.log import Log
    from app.models.article import Article


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    accounts: Mapped[list["Account"]] = relationship(back_populates="role")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | inactive
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped[Role] = relationship(back_populates="accounts")
    logs: Mapped[list["Log"]] = relationship(back_populates="account")

    authored_articles: Mapped[list["Article"]] = relationship(
        back_populates="author", foreign_keys="Article.author_id"
    )
    coauthored_articles: Mapped[list["Article"]] = relationship(
        secondary="article_authors",
        back_populates="coauthors",
    )
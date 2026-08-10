import datetime as dt
import json
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(100), default="", index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result: Mapped[str] = mapped_column(String(20), default="success")
    description: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, index=True)

    account: Mapped["Account | None"] = relationship(back_populates="logs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_name": f"{self.account.first_name} {self.account.last_name}" if self.account else "Аноним",
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "result": self.result,
            "description": self.description,
            "metadata": self.data,
            "created_at": self.created_at,
        }
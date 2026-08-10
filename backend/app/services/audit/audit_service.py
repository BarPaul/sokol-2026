from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.log import Log


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        account_id: int | None,
        action: str,
        entity_type: str = "",
        entity_id: int | None = None,
        result: str = "success",
        description: str = "",
        metadata: dict | None = None,
    ) -> Log:
        entry = Log(
            account_id=account_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            result=result,
            description=description,
            data=metadata or {},
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_logs(
        self,
        account_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str = "",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Log], int]:
        stmt = select(Log)
        count_stmt = select(func.count(Log.id))
        clauses = []
        if account_id is not None:
            clauses.append(Log.account_id == account_id)
        if action:
            clauses.append(Log.action == action)
        if entity_type:
            clauses.append(Log.entity_type == entity_type)
        if date_from:
            clauses.append(Log.created_at >= date_from)
        if date_to:
            clauses.append(Log.created_at <= date_to)
        if search:
            like = f"%{search}%"
            clauses.append(
                Log.description.ilike(like) | Log.action.ilike(like)
            )
        for clause in clauses:
            stmt = stmt.where(clause)
            count_stmt = count_stmt.where(clause)
        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Log.created_at.desc()).offset(offset).limit(limit)
            )
        )
        return items, total

    def get(self, log_id: int) -> Log | None:
        return self.db.get(Log, log_id)
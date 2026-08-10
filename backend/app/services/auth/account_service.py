import datetime as dt

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.account import Account
from app.models.log import Log
from app.schemas.auth import AccountCreate


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def list_editors(self, search: str = "") -> list[Account]:
        stmt = (
            select(Account)
            .options(selectinload(Account.role))
            .where(Account.role.has(name="editor"))
            .order_by(Account.created_at.desc())
        )
        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                Account.first_name.ilike(like)
                | Account.last_name.ilike(like)
                | Account.email.ilike(like)
            )
        return list(self.db.scalars(stmt))

    def get(self, account_id: int) -> Account:
        account = self.db.get(Account, account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Редактор не найден")
        return account

    def set_status(self, account_id: int, status: str) -> Account:
        account = self.get(account_id)
        account.status = status
        account.is_active = status == "active"
        self.db.commit()
        self.db.refresh(account)
        return account

    def count(self) -> int:
        return len(self.list_editors())
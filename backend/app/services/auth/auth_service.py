import datetime as dt
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.account import Account, Role
from app.schemas.auth import AccountCreate

pwd_context = None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


class AuthService:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def _get_role(self, name: str) -> Role:
        role = self.db.scalar(select(Role).where(Role.name == name))
        if role is None:
            raise HTTPException(status_code=500, detail="Роль не настроена в базе")
        return role

    def authenticate(self, email: str, password: str) -> Account:
        account = self.db.scalar(select(Account).where(Account.email == email.lower().strip()))
        if account is None or not verify_password(password, account.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )
        if not account.is_active or account.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт деактивирован",
            )
        account.last_login_at = dt.datetime.utcnow()
        self.db.commit()
        return account

    def login(self, email: str, password: str) -> str:
        account = self.authenticate(email, password)
        return create_access_token(subject=str(account.id), role=account.role.name)

    def create_account(self, payload: AccountCreate) -> Account:
        if self.db.scalar(select(Account).where(Account.email == payload.email.lower().strip())):
            raise HTTPException(status_code=409, detail="Аккаунт с таким email уже существует")
        account = Account(
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=payload.email.lower().strip(),
            password_hash=hash_password(payload.password),
            role_id=self._get_role(payload.role).id,
            status="active",
            is_active=True,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update_password(self, account: Account, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, account.password_hash):
            raise HTTPException(status_code=400, detail="Текущий пароль указан неверно")
        account.password_hash = hash_password(new_password)
        self.db.commit()

    def update_profile(self, account: Account, **changes) -> Account:
        for field, value in changes.items():
            if value is not None:
                if field == "email":
                    value = value.lower().strip()
                setattr(account, field, value)
        self.db.commit()
        self.db.refresh(account)
        return account
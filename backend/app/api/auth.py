from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_account
from app.db.session import get_db
from app.models.account import Account
from app.schemas.auth import (
    AccountOut,
    LoginRequest,
    PasswordChange,
    PasswordRecoveryRequest,
    ProfileUpdate,
    TokenResponse,
)
from app.services.audit.audit_service import AuditService
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _account_out(account: Account) -> AccountOut:
    return AccountOut(
        id=account.id,
        first_name=account.first_name,
        last_name=account.last_name,
        email=account.email,
        role=account.role.name,
        status=account.status,
        created_at=account.created_at,
        last_login_at=account.last_login_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    service = AuthService(db)
    account = service.authenticate(payload.email, payload.password)
    AuditService(db).log(account.id, "login", "account", account.id, description=f"Вход: {account.email}")
    return TokenResponse(access_token=service.login(payload.email, payload.password))


@router.post("/logout")
def logout(account: Annotated[Account, Depends(get_current_account)], db: Annotated[Session, Depends(get_db)]):
    AuditService(db).log(account.id, "logout", "account", account.id, description="Выход")
    return {"status": "ok"}


@router.get("/me", response_model=AccountOut)
def me(account: Annotated[Account, Depends(get_current_account)]):
    return _account_out(account)


@router.patch("/me", response_model=AccountOut)
def update_profile(
    payload: ProfileUpdate,
    account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[Session, Depends(get_db)],
):
    service = AuthService(db)
    updated = service.update_profile(
        account,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
    )
    return _account_out(updated)


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[Session, Depends(get_db)],
):
    AuthService(db).update_password(account, payload.current_password, payload.new_password)
    return {"status": "ok"}


@router.post("/password-recovery")
def password_recovery(payload: PasswordRecoveryRequest, db: Annotated[Session, Depends(get_db)]):
    # MVP: письма не отправляются, только подтверждаем обработку.
    return {"status": "ok", "message": "Инструкции отправлены, если аккаунт существует"}
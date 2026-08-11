from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.account import Account
from app.schemas.auth import AccountCreate, AccountOut, AccountUpdate
from app.schemas.knowledge import (
    AISettingsOut,
    AISettingsUpdate,
    KnowledgeCreate,
    KnowledgeOut,
    KnowledgeUpdate,
    ReindexResponse,
)
from app.schemas.log import LogOut
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.audit.audit_service import AuditService
from app.services.categories.category_service import CategoryService
from app.services.auth.account_service import AccountService
from app.services.auth.auth_service import AuthService
from app.services.knowledge.knowledge_service import KnowledgeService

router = APIRouter(prefix="/admin", tags=["admin"])
admin_only = require_role("moderator")


def _account_out(a: Account, db: Session | None = None) -> AccountOut:
    articles_count = 0
    if db is not None:
        from sqlalchemy import func, or_, select as sa_select

        from app.models.article import Article

        articles_count = db.scalar(
            sa_select(func.count(Article.id)).where(
                or_(Article.author_id == a.id, Article.coauthors.any(id=a.id))
            )
        ) or 0
    return AccountOut(
        id=a.id,
        first_name=a.first_name,
        last_name=a.last_name,
        email=a.email,
        role=a.role.name if a.role else "",
        status=a.status,
        created_at=a.created_at,
        last_login_at=a.last_login_at,
        articles_count=articles_count,
    )


# ---------- Editors ----------

@router.get("/editors", response_model=list[AccountOut])
def list_editors(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None),
):
    service = AccountService(db)
    editors = service.list_editors(search=q or "")
    return [_account_out(e, db) for e in editors]


@router.post("/editors", response_model=AccountOut)
def create_editor(
    payload: AccountCreate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = AuthService(db)
    editor = service.create_account(payload)
    AuditService(db).log(
        account.id,
        "account.created",
        "account",
        editor.id,
        description=f"Создан редактор: {editor.email}",
    )
    return _account_out(editor)


@router.get("/editors/{editor_id}", response_model=AccountOut)
def get_editor(
    editor_id: int,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    editor = AccountService(db).get(editor_id)
    return _account_out(editor, db)


@router.patch("/editors/{editor_id}", response_model=AccountOut)
def update_editor(
    editor_id: int,
    payload: AccountUpdate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    editor = AccountService(db).get(editor_id)
    auth = AuthService(db)
    if payload.email and payload.email != editor.email:
        payload.email = payload.email.lower().strip()
    if payload.password:
        editor = auth.update_profile(editor, first_name=editor.first_name)
        from app.services.auth.auth_service import hash_password

        editor.password_hash = hash_password(payload.password)
        db.commit()
    if payload.status:
        editor.status = payload.status
        editor.is_active = payload.status == "active"
    editor = auth.update_profile(
        editor,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
    )
    AuditService(db).log(
        account.id,
        "account.updated",
        "account",
        editor.id,
        description=f"Обновлён редактор: {editor.email}",
    )
    db.refresh(editor)
    return _account_out(editor)


@router.delete("/editors/{editor_id}")
def delete_editor(
    editor_id: int,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = AccountService(db)
    editor = service.get(editor_id)
    if editor.id == account.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить собственный аккаунт")
    audit = AuditService(db)
    email = editor.email
    result = service.set_status(editor_id, "inactive")
    audit.log(
        account.id,
        "account.deactivated",
        "account",
        editor_id,
        result="success" if not result.is_active else "error",
        description=f"Деактивирован редактор: {email}",
    )
    return {"status": "ok", "message": "Аккаунт деактивирован"}


# ---------- Logs ----------

@router.get("/logs", response_model=dict)
def list_logs(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None),
    action: str | None = Query(default=None),
    account_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items, total = AuditService(db).list_logs(
        action=action,
        account_id=account_id,
        search=q or "",
        limit=limit,
        offset=offset,
    )
    return {"items": [LogOut(**x.to_dict()) for x in items], "total": total}


@router.get("/logs/{log_id}", response_model=LogOut)
def get_log(
    log_id: int,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    item = AuditService(db).get(log_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return LogOut(**item.to_dict())


# ---------- AI settings ----------

@router.get("/ai/settings", response_model=AISettingsOut)
def get_ai_settings(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    from app.services.ai.assistant_service import AssistantService

    st = AssistantService(db)._settings()
    return AISettingsOut(
        id=st.id,
        system_prompt=st.system_prompt,
        model=st.model,
        temperature=st.temperature,
        max_tokens=st.max_tokens,
        knowledge_enabled=st.knowledge_enabled,
        updated_at=st.updated_at,
    )


@router.patch("/ai/settings", response_model=AISettingsOut)
def update_ai_settings(
    payload: AISettingsUpdate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    from app.services.ai.assistant_service import AssistantService

    st = AssistantService(db)._settings()
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(st, field, value)
    db.commit()
    db.refresh(st)
    AuditService(db).log(account.id, "ai.settings.updated", "ai_settings", st.id, description="Обновлены настройки AI")
    return AISettingsOut(
        id=st.id,
        system_prompt=st.system_prompt,
        model=st.model,
        temperature=st.temperature,
        max_tokens=st.max_tokens,
        knowledge_enabled=st.knowledge_enabled,
        updated_at=st.updated_at,
    )


# ---------- Knowledge base ----------

@router.get("/knowledge", response_model=list[KnowledgeOut])
def list_knowledge(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None),
):
    docs = KnowledgeService(db).list_all(search=q or "")
    return docs


@router.post("/knowledge", response_model=KnowledgeOut)
def create_knowledge(
    payload: KnowledgeCreate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = KnowledgeService(db)
    service.ensure_fts()
    doc = service.create(payload)
    AuditService(db).log(account.id, "knowledge.created", "knowledge", doc.id, description=f"Создан документ: {doc.title}")
    return doc


@router.get("/knowledge/{doc_id}", response_model=KnowledgeOut)
def get_knowledge(
    doc_id: int,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    return KnowledgeService(db).get(doc_id)


@router.patch("/knowledge/{doc_id}", response_model=KnowledgeOut)
def update_knowledge(
    doc_id: int,
    payload: KnowledgeUpdate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    doc = KnowledgeService(db).update(doc_id, payload)
    AuditService(db).log(account.id, "knowledge.updated", "knowledge", doc.id, description=f"Обновлён документ: {doc.title}")
    return doc


@router.delete("/knowledge/{doc_id}")
def delete_knowledge(
    doc_id: int,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = KnowledgeService(db)
    doc = service.get(doc_id)
    service.delete(doc_id)
    AuditService(db).log(account.id, "knowledge.deleted", "knowledge", doc_id, description=f"Удалён документ: {doc.title}")
    return {"status": "ok"}


@router.post("/knowledge/reindex", response_model=ReindexResponse)
def reindex_knowledge(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    count = KnowledgeService(db).reindex()
    AuditService(db).log(account.id, "knowledge.reindexed", "knowledge", None, description=f"Переиндексация: {count} документов")
    return ReindexResponse(status="ok", documents=count)


# ---------- Articles (all, for admin) ----------

@router.get("/articles")
def list_all_articles(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    from sqlalchemy import func, select as sa_select

    from app.models.article import Article
    from app.services.articles.article_service import _norm_contains, article_search_text, serialize_article

    stmt = sa_select(Article)
    count_stmt = sa_select(func.count(Article.id))
    if status:
        stmt = stmt.where(Article.status == status)
        count_stmt = count_stmt.where(Article.status == status)
    if q:
        # кириллица не поддерживается ilike/lower в SQLite — фильтруем в Python.
        rows = list(db.scalars(stmt))
        q_filtered = [a for a in rows if _norm_contains(q, article_search_text(a))]
        total = len(q_filtered)
        items = q_filtered[offset : offset + limit]
        return {"items": [serialize_article(a) for a in items], "total": total}
    total = db.scalar(count_stmt) or 0
    items = list(
        db.scalars(stmt.order_by(Article.updated_at.desc()).offset(offset).limit(limit))
    )
    return {"items": [serialize_article(a) for a in items], "total": total}


# ---------- Categories ----------

@router.get("/categories", response_model=list[dict])
def list_categories(
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
    q: str | None = Query(default=None),
):
    return CategoryService(db).list_all(search=q or "")


@router.post("/categories", response_model=CategoryOut)
def create_category(
    payload: CategoryCreate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    cat = CategoryService(db).create(payload)
    AuditService(db).log(account.id, "category.created", "category", cat.id, description=f"Создана категория: {cat.name}")
    return cat


@router.patch("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    cat = CategoryService(db).update(category_id, payload)
    AuditService(db).log(account.id, "category.updated", "category", cat.id, description=f"Обновлена категория: {cat.name}")
    return cat


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    account: Annotated[Account, Depends(admin_only)],
    db: Annotated[Session, Depends(get_db)],
):
    service = CategoryService(db)
    cat = service.get(category_id)
    service.delete(category_id)
    AuditService(db).log(account.id, "category.deleted", "category", category_id, description=f"Удалена категория: {cat.name}")
    return {"status": "ok"}
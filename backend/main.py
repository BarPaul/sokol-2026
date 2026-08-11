from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api import articles, assistant, admin, auth, editor
from app.api.editor import editors_search

from app.db.base import Base
from app.db.session import engine, SessionLocal


def init_db():
    Base.metadata.create_all(bind=engine)
    from app.services.knowledge.knowledge_service import KnowledgeService

    db = SessionLocal()
    try:
        KnowledgeService(db).ensure_fts()
    finally:
        db.close()


def seed():
    """Create roles, default accounts and demo articles if missing."""
    from sqlalchemy import select

    from seed import DEMO_ARTICLES, DEMO_DOCUMENTS

    from app.models.account import Account, Role
    from app.models.article import Article
    from app.models.category import Category
    from app.models.knowledge import KnowledgeDocument
    from app.services.auth.auth_service import hash_password

    db = SessionLocal()
    try:
        roles = {}
        for name in ("moderator", "editor"):
            role = db.scalar(select(Role).where(Role.name == name))
            if role is None:
                role = Role(name=name)
                db.add(role)
                db.flush()
            roles[name] = role
        db.commit()

        if db.scalar(select(Category).limit(1)) is None:
            for i, name in enumerate(
                ["Выплаты и льготы", "Жильё", "Права и консультации", "Обучение", "Здоровье"]
            ):
                db.add(Category(name=name, sort_order=i))
            db.commit()

        defaults = [
            (settings.seed_admin_email, settings.seed_admin_password, "Администратор", "Системы", "moderator"),
            (settings.seed_editor_email, settings.seed_editor_password, "Редактор", "СтудСемья", "editor"),
        ]
        for email, password, first, last, role_name in defaults:
            if db.scalar(select(Account).where(Account.email == email)) is None:
                db.add(
                    Account(
                        first_name=first,
                        last_name=last,
                        email=email,
                        password_hash=hash_password(password),
                        role_id=roles[role_name].id,
                        status="active",
                        is_active=True,
                    )
                )
        db.commit()

        if db.scalar(select(Article).limit(1)) is None:
            editor = db.scalar(select(Account).where(Account.role.has(name="editor")))
            if editor is None:
                editor = db.scalar(select(Account).limit(1))
            for item in DEMO_ARTICLES:
                db.add(
                    Article(
                        title=item["title"],
                        slug=item["slug"],
                        summary=item["summary"],
                        content=item["content"],
                        category=item["category"],
                        region=item["region"],
                        official_source=item["official_source"],
                        restrictions=item["restrictions"],
                        status="published",
                        author_id=editor.id if editor else 1,
                    )
                )
            db.commit()

        if db.scalar(select(KnowledgeDocument).limit(1)) is None:
            for item in DEMO_DOCUMENTS:
                db.add(KnowledgeDocument(**item))
            db.commit()

        from app.services.knowledge.knowledge_service import KnowledgeService

        KnowledgeService(db).reindex()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (auth, articles, assistant, editor, admin):
    app.include_router(module.router, prefix=settings.api_prefix)
app.include_router(editors_search, prefix=settings.api_prefix)

uploads_dir = Path(settings.sqlite_path).parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=uploads_dir), name="uploads")
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.article import Article
from app.schemas.chat import (
    AssistantResponseOut,
    ChatCreate,
    ChatOut,
    MessageCreate,
    MessageOut,
    RecommendedArticleOut,
)
from app.services.ai.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _session_id(request: Request) -> str:
    """Anonymous session identifier from cookie; create one if missing."""
    sid = request.cookies.get("semyainfo_session")
    if not sid:
        import uuid

        sid = uuid.uuid4().hex
    return sid


def _set_session_cookie(request: Request, response, sid: str):
    from datetime import timedelta

    response.set_cookie(
        key="semyainfo_session",
        value=sid,
        max_age=int(timedelta(days=365).total_seconds()),
        httponly=True,
        samesite="lax",
    )


def _to_article_meta(a: Article) -> RecommendedArticleOut:
    return RecommendedArticleOut(
        id=a.id,
        title=a.title,
        slug=a.slug,
        summary=a.summary,
        category=a.category,
    )


@router.post("/chats", response_model=ChatOut)
def create_chat(
    payload: ChatCreate | None = None,
    db: Annotated[Session, Depends(get_db)] = None,
    request: Request = None,
    response: Response = None,
):
    sid = _session_id(request)
    _set_session_cookie(request, response, sid)
    chat = AssistantService(db).create_chat(sid, title=(payload.title if payload else "Новый диалог"))
    return chat


@router.get("/chats", response_model=list[ChatOut])
def list_chats(db: Annotated[Session, Depends(get_db)], request: Request):
    sid = _session_id(request)
    return AssistantService(db).list_chats(sid)


@router.get("/chats/{chat_id}", response_model=ChatOut)
def get_chat(chat_id: int, db: Annotated[Session, Depends(get_db)], request: Request):
    return AssistantService(db).get_chat(_session_id(request), chat_id)


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, db: Annotated[Session, Depends(get_db)], request: Request):
    AssistantService(db).delete_chat(_session_id(request), chat_id)
    return {"status": "ok"}


@router.get("/chats/{chat_id}/messages", response_model=list[MessageOut])
def get_messages(chat_id: int, db: Annotated[Session, Depends(get_db)], request: Request):
    service = AssistantService(db)
    service.get_chat(_session_id(request), chat_id)
    return service.messages(chat_id)


@router.post("/chats/{chat_id}/messages", response_model=AssistantResponseOut)
def send_message(
    chat_id: int,
    payload: MessageCreate,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    service = AssistantService(db)
    sid = _session_id(request)
    assistant_msg, recommended = service.ask(sid, chat_id, payload.content)
    return AssistantResponseOut(
        message=MessageOut(
            id=assistant_msg.id,
            chat_id=assistant_msg.chat_id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            created_at=assistant_msg.created_at,
        ),
        articles=[_to_article_meta(a) for a in recommended],
    )
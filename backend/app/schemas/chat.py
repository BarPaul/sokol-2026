import datetime as dt

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    title: str = "Новый диалог"


class ChatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    title: str
    created_at: dt.datetime
    updated_at: dt.datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    role: str
    content: str
    created_at: dt.datetime


class MessageCreate(BaseModel):
    content: str


class RecommendedArticleOut(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    category: str


class AssistantResponseOut(BaseModel):
    message: MessageOut
    articles: list[RecommendedArticleOut] = []
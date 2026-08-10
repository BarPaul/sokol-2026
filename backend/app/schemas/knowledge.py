import datetime as dt

from pydantic import BaseModel, ConfigDict


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    source: str = ""
    category: str = ""
    is_active: bool = True


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    source: str | None = None
    category: str | None = None
    is_active: bool | None = None


class KnowledgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    category: str
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime


class AISettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_prompt: str
    model: str
    temperature: float
    max_tokens: int
    knowledge_enabled: bool
    updated_at: dt.datetime | None = None


class AISettingsUpdate(BaseModel):
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    knowledge_enabled: bool | None = None


class ReindexResponse(BaseModel):
    status: str
    documents: int
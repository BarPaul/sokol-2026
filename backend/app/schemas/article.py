import datetime as dt
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str = ""
    content: str = ""
    audience: str = ""
    documents: str = ""
    category: str = ""
    region: str = ""
    official_source: str = ""
    restrictions: str = ""


class ArticleCreate(ArticleBase):
    status: Literal["draft", "published"] = "draft"


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    summary: Optional[str] = None
    content: Optional[str] = None
    audience: Optional[str] = None
    documents: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    official_source: Optional[str] = None
    restrictions: Optional[str] = None
    status: Optional[Literal["draft", "published", "archived"]] = None


class CoauthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str


class ArticleListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str
    category: str
    status: str
    author_id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    published_at: dt.datetime | None = None


class ArticleOut(ArticleListOut):
    content: str
    audience: str
    documents: str
    region: str
    official_source: str
    restrictions: str
    author_name: str = ""
    coauthors: list[CoauthorOut] = []


class ArticleCardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str
    category: str
    updated_at: dt.datetime


class CoauthorAdd(BaseModel):
    account_id: int


class PublishResponse(BaseModel):
    id: int
    status: str
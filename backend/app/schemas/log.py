import datetime as dt

from pydantic import BaseModel


class LogOut(BaseModel):
    id: int
    account_id: int | None
    account_name: str
    action: str
    entity_type: str
    entity_id: int | None
    result: str
    description: str
    metadata: dict
    created_at: dt.datetime
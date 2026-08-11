import datetime as dt

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


import app.models.account  # noqa: E402,F401
import app.models.article  # noqa: E402,F401
import app.models.category  # noqa: E402,F401
import app.models.chat  # noqa: E402,F401
import app.models.knowledge  # noqa: E402,F401
import app.models.log  # noqa: E402,F401
import app.models.message  # noqa: E402,F401
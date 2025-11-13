from typing import Any

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


ORM_OBJ = Any
ORM_CLS = Any


class Base(AsyncAttrs, DeclarativeBase):
    pass

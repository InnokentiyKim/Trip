from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.domain.models import async_session_maker
from fastapi import Depends


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import session_maker


@asynccontextmanager
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session

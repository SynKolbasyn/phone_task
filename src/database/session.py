from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import session_maker


@asynccontextmanager
async def async_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session, session.begin():
        yield session


async def provide_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session

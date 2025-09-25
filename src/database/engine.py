from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import Settings

engine = create_async_engine(Settings().database_url)
session_maker = async_sessionmaker(engine, expire_on_commit=False)

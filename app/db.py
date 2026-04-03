from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

_engine = None
_AsyncSessionLocal = None

def _init():
    global _engine, _AsyncSessionLocal
    if _engine is None:
        url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@my-postgres:5432/mydb")
        _engine = create_async_engine(url, echo=True)
        _AsyncSessionLocal = sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)
    return _AsyncSessionLocal

async def get_db() -> AsyncSession:
    factory = _init()
    async with factory() as session:
        yield session

def get_engine():
    _init()
    return _engine

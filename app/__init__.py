from app.db import get_engine
from app.models import Base

async def init_db():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

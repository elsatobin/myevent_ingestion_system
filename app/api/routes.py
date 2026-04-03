from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Event
from app.ingestion import async_session

router = APIRouter()


@router.get("/events")
async def list_events():
    async with async_session() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()
    return events
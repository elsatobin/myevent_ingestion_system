from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import Event, Entity

router = APIRouter()


@router.get("/events")
async def get_events(
    entity_id: str = Query(None),
    event_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Event).order_by(Event.timepoint)
    if entity_id:
        stmt = stmt.where(Event.entity_id == entity_id)
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entity).where(Entity.entity_id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

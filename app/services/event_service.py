from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from app.models import Event, Entity


async def process_event(db: AsyncSession, event_data: dict) -> bool:
    """
    Returns True if the event was processed, False if it was a duplicate.

    Idempotency: uses INSERT ... ON CONFLICT DO NOTHING — atomic, no race condition.
    Out-of-order: raw event is always stored; entity state only updated if timepoint is newer.
    """

    # Step 1: Atomic idempotent insert — duplicate IDs are silently ignored
    stmt = insert(Event).values(
        id=event_data["id"],
        entity_id=event_data["entity_id"],
        event_type=event_data["event_type"],
        payload=event_data["payload"],
        timepoint=event_data["timepoint"],
    ).on_conflict_do_nothing(index_elements=["id"])

    result = await db.execute(stmt)
    if result.rowcount == 0:
        # Duplicate — nothing to do
        return False

    # Step 2: Get or create entity
    result = await db.execute(select(Entity).where(Entity.entity_id == event_data["entity_id"]))
    entity = result.scalar_one_or_none()

    if not entity:
        entity = Entity(
            entity_id=event_data["entity_id"],
            data={},
            last_timepoint=None,
        )
        db.add(entity)

    # Step 3: Out-of-order guard — event stored, but skip stale entity update
    if entity.last_timepoint and event_data["timepoint"] < entity.last_timepoint:
        await db.commit()
        return True

    # Step 4: Apply event to entity state
    if event_data["event_type"] == "created":
        entity.data = event_data["payload"]
    elif event_data["event_type"] == "updated":
        entity.data = {**(entity.data or {}), **event_data["payload"]}
    elif event_data["event_type"] == "deleted":
        entity.data = {}

    entity.last_timepoint = event_data["timepoint"]

    await db.commit()
    return True

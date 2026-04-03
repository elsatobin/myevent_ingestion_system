import asyncio
from app.db import AsyncSessionLocal
from app.models import Event, Checkpoint

async def get_last_checkpoint(session: AsyncSessionLocal) -> int:
    # Get the last checkpoint from the database
    result = await session.get(Checkpoint, "main")
    return result.last_event_id if result else 0

async def update_checkpoint(session: AsyncSessionLocal, last_id: int):
    # Update checkpoint in the database
    cp = await session.get(Checkpoint, "main")
    if not cp:
        cp = Checkpoint(id="main", last_event_id=last_id)
        session.add(cp)
    else:
        cp.last_event_id = last_id
    await session.commit()

async def consume_stream():
    # Consume events from a stream
    async with AsyncSessionLocal() as session:
        last_id = await get_last_checkpoint(session)
        print(f"Starting from last_event_id={last_id}")

        while True:
            # Example: generate new event
            last_id += 1
            event = Event(data=f"event-{last_id}")
            session.add(event)
            await session.commit()
            await update_checkpoint(session, last_id)

            # Wait before next event
            await asyncio.sleep(1)
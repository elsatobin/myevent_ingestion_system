import asyncio
import json
import logging
import os

import httpx
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

from app.db import get_db
from app.models import Checkpoint
from app.services.event_service import process_event

logger = logging.getLogger(__name__)

STREAM_URL = os.getenv("STREAM_URL", "http://stream-container:8001/stream")
RETRY_DELAY = 5  # seconds between reconnect attempts


async def get_checkpoint() -> str | None:
    async for db in get_db():
        result = await db.execute(select(Checkpoint).where(Checkpoint.id == "main"))
        cp = result.scalar_one_or_none()
        return cp.last_timepoint if cp else None


async def consume_stream():
    while True:
        try:
            last_timepoint = await get_checkpoint()

            url = STREAM_URL
            if last_timepoint:
                url = f"{url}?from_timepoint={last_timepoint}"
                logger.info(f"Resuming stream from {last_timepoint}")
            else:
                logger.info("Starting stream from beginning")

            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            logger.warning(f"Skipping invalid JSON line: {line}")
                            continue

                        async for db in get_db():
                            processed = await process_event(db, event)
                            if processed:
                                # Update checkpoint in the same session
                                stmt = insert(Checkpoint).values(
                                    id="main", last_timepoint=event["timepoint"]
                                ).on_conflict_do_update(
                                    index_elements=["id"],
                                    set_={"last_timepoint": event["timepoint"]},
                                )
                                await db.execute(stmt)
                                await db.commit()

        except Exception as e:
            logger.error(f"Stream error: {e}. Reconnecting in {RETRY_DELAY}s...")
            await asyncio.sleep(RETRY_DELAY)

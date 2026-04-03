import asyncio
import json
import random
from datetime import datetime, timedelta

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

app = FastAPI()


async def generate_events(start_time: datetime):
    current_time = start_time
    history = []

    while True:
        current_time += timedelta(seconds=1)

        event = {
            "id": f"evt_{random.randint(1, 10)}",
            "entity_id": f"org_{random.randint(1, 3)}",
            "event_type": random.choice(["created", "updated", "deleted"]),
            "payload": {"value": random.randint(1, 100)},
            "timepoint": current_time.isoformat() + "Z",
        }

        history.append(event)

        # ~20% chance: emit a duplicate
        if random.random() < 0.2 and history:
            yield json.dumps(random.choice(history)) + "\n"
            await asyncio.sleep(0.5)
            continue

        # ~20% chance: emit an out-of-order (older) event
        if random.random() < 0.2 and len(history) > 3:
            yield json.dumps(history[-3]) + "\n"
            await asyncio.sleep(0.5)
            continue

        yield json.dumps(event) + "\n"
        await asyncio.sleep(0.5)


@app.get("/stream")
async def stream(from_timepoint: str = Query(None)):
    if from_timepoint:
        start_time = datetime.fromisoformat(from_timepoint.replace("Z", ""))
    else:
        start_time = datetime.utcnow()

    return StreamingResponse(generate_events(start_time), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import json
import time
import random
from datetime import datetime, timedelta

app = FastAPI()


def generate_events(start_time: datetime):
    """
    Generator that simulates:
    - continuous stream
    - duplicates
    - out-of-order events
    """

    current_time = start_time

    history = []  # store some past events for duplication

    while True:
        # simulate time progression
        current_time += timedelta(seconds=1)

        event = {
            "id": f"evt_{random.randint(1, 5)}",  # small range → duplicates 발생
            "entity_id": f"org_{random.randint(1, 3)}",
            "event_type": random.choice(["created", "updated", "deleted"]),
            "payload": {"value": random.randint(1, 100)},
            "timepoint": current_time.isoformat() + "Z"
        }

        history.append(event)

        # --- occasionally emit duplicate ---
        if random.random() < 0.2 and history:
            yield json.dumps(random.choice(history)) + "\n"
            time.sleep(0.5)
            continue

        # --- occasionally emit out-of-order ---
        if random.random() < 0.2 and len(history) > 3:
            yield json.dumps(history[-3]) + "\n"
            time.sleep(0.5)
            continue

        yield json.dumps(event) + "\n"

        time.sleep(0.5)


@app.get("/stream")
def stream(from_timepoint: str = Query(None)):
    """
    Streaming endpoint with resume support
    """

    if from_timepoint:
        start_time = datetime.fromisoformat(from_timepoint.replace("Z", ""))
    else:
        start_time = datetime.utcnow()

    return StreamingResponse(
        generate_events(start_time),
        media_type="text/plain"
    )
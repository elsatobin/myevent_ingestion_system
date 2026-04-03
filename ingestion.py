import requests
import time
from app.db import SessionLocal
from app.services.event_service import process_event

STREAM_URL = "https://example.com/stream"


def consume_stream():
    """
    Continuously consumes event stream with retry + resume logic
    """

    # --- STEP 1: load checkpoint from DB ---
    db = SessionLocal()

    try:
        last_timepoint = get_last_checkpoint(db)
        # last_timepoint can be None if first run
    finally:
        db.close()

    # --- STEP 2: start consuming loop ---
    while True:
        try:
            params = {}

            if last_timepoint:
                # Resume from last processed point
                params["from_timepoint"] = last_timepoint

            response = requests.get(STREAM_URL, params=params, stream=True)

            for line in response.iter_lines():
                if not line:
                    continue

                event = parse_event(line)

                db = SessionLocal()

                try:
                    process_event(db, event)

                    # --- STEP 3: update checkpoint AFTER success ---
                    update_checkpoint(db, event["timepoint"])

                    # keep local variable in sync
                    last_timepoint = event["timepoint"]

                finally:
                    db.close()

        except Exception as e:
            print(f"Error consuming stream: {e}")
            time.sleep(5)

def parse_event(raw_line):
    """
    Converts raw stream line into dict
    """
    import json
    return json.loads(raw_line)


def get_last_checkpoint(db):
    """
    Load last processed timepoint from DB
    """
    cp = db.query(Checkpoint).filter_by(id="main").first()
    return cp.last_timepoint if cp else None


def update_checkpoint(db, timepoint):
    """
    Save last processed timepoint to DB
    """
    cp = db.query(Checkpoint).filter_by(id="main").first()

    if not cp:
        cp = Checkpoint(id="main", last_timepoint=timepoint)
        db.add(cp)
    else:
        cp.last_timepoint = timepoint

    db.commit()
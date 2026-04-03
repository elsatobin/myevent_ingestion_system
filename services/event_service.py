from sqlalchemy.orm import Session
from app.models import Event, Entity


def process_event(db: Session, event_data: dict):
    """
    Core logic:
    - Ensure idempotency (ignore duplicates)
    - Handle out-of-order events
    - Update entity state
    """

    # --- Step 1: Check duplicate ---
    existing_event = db.query(Event).filter(Event.id == event_data["id"]).first()
    if existing_event:
        # Duplicate event → ignore safely
        return

    # --- Step 2: Save raw event ---
    event = Event(**event_data)
    db.add(event)

    # --- Step 3: Get or create entity ---
    entity = db.query(Entity).filter(Entity.entity_id == event_data["entity_id"]).first()

    if not entity:
        # First time seeing this entity
        entity = Entity(
            entity_id=event_data["entity_id"],
            data={},
            last_timepoint=event_data["timepoint"]
        )
        db.add(entity)

    # --- Step 4: Handle out-of-order events ---
    if entity.last_timepoint and event_data["timepoint"] < entity.last_timepoint:
        # Older event → ignore state update (but event still stored)
        db.commit()
        return

    # --- Step 5: Apply event ---
    if event_data["event_type"] == "created":
        entity.data = event_data["payload"]

    elif event_data["event_type"] == "updated":
        # Merge payload into existing data
        entity.data = {**entity.data, **event_data["payload"]}

    elif event_data["event_type"] == "deleted":
        entity.data = {}

    # --- Step 6: Update checkpoint ---
    entity.last_timepoint = event_data["timepoint"]

    db.commit()
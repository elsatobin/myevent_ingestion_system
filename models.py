from sqlalchemy import Column, String, JSON, DateTime
from app.db import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    # Unique ID ensures idempotency (duplicate protection)

    entity_id = Column(String, index=True)
    event_type = Column(String)

    payload = Column(JSON)

    timepoint = Column(DateTime, index=True)


class Entity(Base):
    __tablename__ = "entities"

    entity_id = Column(String, primary_key=True)

    data = Column(JSON)
    # Represents latest state of entity

    last_timepoint = Column(DateTime)
    # Used to handle out-of-order events
class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(String, primary_key=True)
    # identifier for the consumer (e.g. "main")

    last_timepoint = Column(DateTime)
    # last successfully processed event
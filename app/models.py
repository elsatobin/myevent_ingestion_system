from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase
import datetime


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    entity_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    timepoint = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class Entity(Base):
    __tablename__ = "entities"

    entity_id = Column(String, primary_key=True, index=True)
    data = Column(JSON, nullable=True, default=dict)
    last_timepoint = Column(String, nullable=True)


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(String, primary_key=True, index=True)
    last_timepoint = Column(String, nullable=True)

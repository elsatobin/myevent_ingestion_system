from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(String, primary_key=True, default="main")
    last_event_id = Column(Integer, default=0)
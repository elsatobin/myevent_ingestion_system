from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Event, Entity

router = APIRouter()


@router.get("/events")
def get_events(db: Session = Depends(get_db)):
    """
    Fetch all events
    """
    return db.query(Event).all()


@router.get("/entities/{entity_id}")
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    """
    Fetch current state of entity
    """
    return db.query(Entity).filter(Entity.entity_id == entity_id).first()
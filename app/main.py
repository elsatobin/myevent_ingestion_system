from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal, engine, Base
from app.models import Event
from app.ingestion import consume_stream
import asyncio

app = FastAPI()

async def get_session() -> AsyncSession:
    # Provide a database session
    async with AsyncSessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup_event():
    # Create tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Start background stream consumer
    asyncio.create_task(consume_stream())

@app.get("/")
async def read_root():
    # Root endpoint
    return {"message": "API is running!"}

@app.get("/events")
async def read_events(session: AsyncSession = Depends(get_session)):
    # Get all events from database
    result = await session.execute(
        "SELECT id, data, timestamp FROM events ORDER BY id"
    )
    events = result.fetchall()
    return [{"id": e.id, "data": e.data, "timestamp": str(e.timestamp)} for e in events]
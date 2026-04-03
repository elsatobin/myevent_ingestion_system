import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import init_db
from app.api.routes import router
from app.ingestion import consume_stream

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(consume_stream())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "API is running"}

from fastapi import FastAPI
from threading import Thread
from app.ingestion import consume_stream
from app.api.routes import router

app = FastAPI()

# Include API routes
app.include_router(router)


@app.on_event("startup")
def start_consumer():
    """
    Start ingestion in background thread
    """
    thread = Thread(target=consume_stream, daemon=True)
    thread.start()

@app.get("/")
def read_root():
    return {"message": "API is running!"}
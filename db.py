from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Using PostgreSQL (can switch to SQLite for local testing)
DATABASE_URL = "postgresql://user:password@localhost:5432/events_db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
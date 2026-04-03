# app/init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@my-postgres:5432/mydb")

# Strip asyncpg scheme if passed via env (async URL → sync URL)
if DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)

# create engine and session
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    
    print("Database initialized")
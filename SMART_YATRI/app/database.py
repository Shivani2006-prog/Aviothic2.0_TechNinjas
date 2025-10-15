"""
Smart Yatri Database Setup
Author: Abhay Tripathi
Project: Smart Yatri
Description: SQLAlchemy database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ----------------------
# Environment variables (can also use .env)
# ----------------------
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "smart_yatri")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ----------------------
# SQLAlchemy setup
# ----------------------
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ----------------------
# Dependency for FastAPI routes
# ----------------------
def get_db():
    """
    Yield a database session for FastAPI dependency injection.
    Closes session automatically after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

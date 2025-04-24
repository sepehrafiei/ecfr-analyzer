"""
Database module for the eCFR Analyzer.
Defines SQLAlchemy models and database connection setup.
Manages agency metrics storage and retrieval.

Author: Sepehr Rafiei
"""

import os
import time
from sqlalchemy import Column, Integer, String, JSON, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.exc import OperationalError

Base = declarative_base()

class AgencyMetrics(Base):
    __tablename__ = 'agency_metrics'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    scope = Column(JSON)
    section_count = Column(Integer)
    word_count = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Use environment variable for database URL, fallback to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/ecfr.db")

# Handle Render's PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_engine(max_retries=5, retry_delay=2):
    """Create database engine with retry logic."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Database connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)

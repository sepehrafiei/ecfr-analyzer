"""
Database module for the eCFR Analyzer.
Defines SQLAlchemy models and database connection setup.
Manages agency metrics storage and retrieval.

Author: Sepehr Rafiei
"""

import os
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

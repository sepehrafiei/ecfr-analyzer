"""
Main FastAPI application for the eCFR Analyzer.
Handles API endpoints, database initialization, and scheduled data refreshes.
Provides endpoints for agency metrics, health checks, and manual data refresh.

Author: Sepehr Rafiei
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime
from pathlib import Path
import os

from .db import SessionLocal, Base, engine, AgencyMetrics
from .analyzer import get_top_agencies_by_word_count, get_agency_summary
from .ingest import run_ingestion, refresh_all_data
from .config import HEADERS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="eCFR Analyzer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Dependency for DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database and load initial data if needed."""
    try:
        # Create database tables
        Base.metadata.create_all(engine)
        
        # Check if we need to load initial data or force refresh
        db = SessionLocal()
        agency_count = db.query(AgencyMetrics).count()
        db.close()
        
        force_refresh = os.getenv("FORCE_REFRESH", "false").lower() == "true"
        
        if agency_count == 0 or force_refresh:
            logger.info("Starting data load...")
            try:
                # Run initial data load in a separate task
                await refresh_data_task()
                logger.info("Initial data load completed successfully")
            except Exception as e:
                logger.error(f"Error during initial data load: {str(e)}")
                # Continue startup even if initial load fails
                pass
        
        # Schedule daily updates at 2 AM UTC
        scheduler.add_job(
            refresh_data_task,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_refresh",
            name="Daily data refresh",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduled daily data refresh for 2 AM UTC")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't raise the exception, allow the app to start
        pass

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    scheduler.shutdown()

async def refresh_data_task():
    """Task to refresh data with logging."""
    try:
        logger.info("Starting data refresh...")
        start_time = datetime.now()
        
        refresh_all_data()
        
        duration = datetime.now() - start_time
        logger.info(f"Data refresh completed successfully in {duration}")
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        raise

# Health check endpoint
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# GET all agency data
@app.get("/api/agencies")
def api_agencies():
    db = SessionLocal()
    try:
        agencies = db.query(AgencyMetrics).all()
        return [
            {
                "name": a.name,
                "section_count": a.section_count,
                "word_count": a.word_count,
                "scope": a.scope,
                "updated_at": a.updated_at.isoformat()
            }
            for a in agencies
        ]
    finally:
        db.close()

# GET top N agencies by word count
@app.get("/api/top-agencies")
def api_top_agencies(limit: int = 10):
    db = SessionLocal()
    try:
        top = get_top_agencies_by_word_count(db, limit)
        return [{"name": a.name, "word_count": a.word_count} for a in top]
    finally:
        db.close()

# GET single agency metrics
@app.get("/api/agency/{agency_name}")
def api_agency_detail(agency_name: str):
    db = SessionLocal()
    try:
        agency = get_agency_summary(db, agency_name)
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        return {
            "name": agency.name,
            "word_count": agency.word_count,
            "section_count": agency.section_count,
            "scope": agency.scope,
            "updated_at": agency.updated_at.isoformat()
        }
    finally:
        db.close()

# POST to refresh data manually
@app.post("/api/refresh")
async def api_refresh_data():
    """Manually trigger data refresh."""
    try:
        await refresh_data_task()
        return {"status": "success", "message": "Data refreshed and stored in DB."}
    except Exception as e:
        logger.error(f"Error in manual refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

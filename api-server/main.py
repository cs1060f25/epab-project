"""
FastAPI application for Cybersecurity & Fraud Detection Platform
"""

import os
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from database import get_db, test_db_connection, Event, Alert, AuditLog
from models import (
    HealthResponse, EventCreate, EventResponse, EventsResponse,
    AlertResponse, AlertsResponse, AlertEventsResponse,
    ErrorResponse, ValidationErrorResponse
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cybersecurity & Fraud Detection Platform API",
    description="API for SOC analysts to investigate security incidents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now(timezone.utc)
    response = await call_next(request)
    process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    logger.info(
        f"{start_time.isoformat()} - {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {process_time:.3f}s"
    )
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": None}
    )


# Startup event to verify database connection
@app.on_event("startup")
async def startup_event():
    logger.info("Starting FastAPI application...")
    if not test_db_connection():
        logger.error("Database connection failed during startup")
        raise Exception("Database connection failed")
    logger.info("Application started successfully")


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - verifies API and database connectivity
    """
    try:
        # Test database connection with a simple query
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        database=db_status
    )


# Get events endpoint
@app.get("/api/events", response_model=EventsResponse)
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve events with optional filtering
    """
    try:
        query = db.query(Event)
        
        # Apply filters
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if user_id:
            query = query.filter(Event.user_id == user_id)
        if start_date:
            query = query.filter(Event.timestamp >= start_date)
        if end_date:
            query = query.filter(Event.timestamp <= end_date)
        
        # Get total count before applying limit
        total = query.count()
        
        # Apply ordering and limit
        events = query.order_by(Event.timestamp.desc()).limit(limit).all()
        
        return EventsResponse(
            events=[EventResponse.model_validate(event) for event in events],
            total=total
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# Create event endpoint
@app.post("/api/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new security event
    """
    try:
        # Create new event with current timestamp
        new_event = Event(
            event_type=event_data.event_type,
            source_system=event_data.source_system,
            timestamp=datetime.now(timezone.utc),
            user_id=event_data.user_id,
            device_id=event_data.device_id,
            event_data=event_data.event_data,
            severity=event_data.severity,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        logger.info(f"Created new event: {new_event.id}")
        return EventResponse.model_validate(new_event)
        
    except SQLAlchemyError as e:
        logger.error(f"Database error creating event: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )


# Get alerts endpoint
@app.get("/api/alerts", response_model=AlertsResponse)
async def get_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by alert status"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve alerts with optional status filtering
    """
    try:
        query = db.query(Alert)
        
        # Apply status filter
        if status_filter:
            query = query.filter(Alert.status == status_filter)
        
        # Get total count before applying limit
        total = query.count()
        
        # Apply ordering and limit
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
        
        # Add event count for each alert
        alert_responses = []
        for alert in alerts:
            event_count = 0
            if alert.related_event_ids:
                # Count events that match the related_event_ids
                event_count = db.query(Event).filter(
                    Event.id.in_([uuid.UUID(eid) for eid in alert.related_event_ids])
                ).count()
            
            alert_response = AlertResponse.model_validate(alert)
            alert_response.event_count = event_count
            alert_responses.append(alert_response)
        
        return AlertsResponse(
            alerts=alert_responses,
            total=total
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# Get alert events endpoint
@app.get("/api/alerts/{alert_id}/events", response_model=AlertEventsResponse)
async def get_alert_events(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve all events linked to a specific alert
    """
    try:
        # Find the alert
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Get related events
        events = []
        total = 0
        
        if alert.related_event_ids:
            try:
                # Convert string IDs to UUIDs
                event_uuids = [uuid.UUID(eid) for eid in alert.related_event_ids]
                events = db.query(Event).filter(
                    Event.id.in_(event_uuids)
                ).order_by(Event.timestamp.asc()).all()
                total = len(events)
            except ValueError as e:
                logger.warning(f"Invalid UUID in alert {alert_id} related_event_ids: {e}")
        
        return AlertEventsResponse(
            alert_id=alert_id,
            events=[EventResponse.model_validate(event) for event in events],
            total=total
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving alert events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
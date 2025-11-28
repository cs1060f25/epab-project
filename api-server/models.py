"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid


# Health check models
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    database: str = Field(..., description="Database connection status")


# Event models
class EventCreate(BaseModel):
    event_type: str = Field(..., description="Type of event", regex="^(security|identity|financial|endpoint|email)$")
    source_system: str = Field(..., description="System that generated the event")
    user_id: Optional[str] = Field(None, description="User ID associated with the event")
    device_id: Optional[str] = Field(None, description="Device ID associated with the event")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Additional event data as JSON")
    severity: str = Field(..., description="Event severity level", regex="^(info|low|medium|high|critical)$")


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of event")
    source_system: str = Field(..., description="System that generated the event")
    timestamp: datetime = Field(..., description="When the event occurred")
    user_id: Optional[str] = Field(None, description="User ID associated with the event")
    device_id: Optional[str] = Field(None, description="Device ID associated with the event")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Additional event data as JSON")
    severity: str = Field(..., description="Event severity level")
    created_at: datetime = Field(..., description="When the event was created in the system")


class EventsResponse(BaseModel):
    events: List[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")


# Alert models
class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="Unique alert identifier")
    title: str = Field(..., description="Alert title")
    status: str = Field(..., description="Alert status")
    confidence_score: Optional[Decimal] = Field(None, description="Confidence score (0-100)")
    created_at: datetime = Field(..., description="When the alert was created")
    event_count: int = Field(..., description="Number of related events")


class AlertsResponse(BaseModel):
    alerts: List[AlertResponse] = Field(..., description="List of alerts")
    total: int = Field(..., description="Total number of alerts")


class AlertEventsResponse(BaseModel):
    alert_id: uuid.UUID = Field(..., description="Alert identifier")
    events: List[EventResponse] = Field(..., description="Events related to this alert")
    total: int = Field(..., description="Total number of related events")


# Query parameter models
class EventQueryParams(BaseModel):
    event_type: Optional[str] = Field(None, description="Filter by event type")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    start_date: Optional[datetime] = Field(None, description="Filter events after this date")
    end_date: Optional[datetime] = Field(None, description="Filter events before this date")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of events to return")


class AlertQueryParams(BaseModel):
    status: Optional[str] = Field(None, description="Filter by alert status", regex="^(open|investigating|resolved)$")
    limit: int = Field(50, ge=1, le=500, description="Maximum number of alerts to return")


# Error response models
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


class ValidationErrorResponse(BaseModel):
    error: str = Field(..., description="Validation error message")
    detail: List[Dict[str, Any]] = Field(..., description="Field validation errors")
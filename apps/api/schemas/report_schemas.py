from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class ReportCreateRequest(BaseModel):
    raw_description: str = Field(..., min_length=5, description="Citizen description of the incident")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    user_category: Optional[str] = Field(None, description="Category selected by citizen")
    formatted_address: Optional[str] = Field(None, description="Optional street address")

class ReportCreateResponse(BaseModel):
    id: str
    tracking_id: str
    created_at: str
    lifecycle_status: str
    message: str

class ReportTrackResponse(BaseModel):
    tracking_id: str
    lifecycle_status: str
    user_category: Optional[str] = None
    verified_category: str
    concise_summary: Optional[str] = None
    created_at: str
    formatted_address: Optional[str] = None
    is_duplicate: bool = False
    master_ticket_id: Optional[str] = None
    priority_rank: str
    priority_score: float
    priority_rationale: Optional[str] = None
    assigned_department: Optional[str] = None
    resolution_notes: Optional[str] = None

class ReportDetailResponse(ReportTrackResponse):
    id: str
    raw_description: str
    media_url: Optional[str] = None
    latitude: float
    longitude: float
    duplicate_count: int = 1
    updated_at: str
    is_manually_overridden: bool = False
    override_reason: Optional[str] = None


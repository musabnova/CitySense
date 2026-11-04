from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ReportCreateRequest(BaseModel):
    raw_description: str = Field(..., min_length=5, description="Citizen description of the incident")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    user_category: Optional[str] = Field(None, description="Category selected by citizen")
    formatted_address: Optional[str] = Field(None, description="Optional street address")
    media_url: Optional[str] = Field(None, description="Optional media URL or preview")

class ReportCreateResponse(BaseModel):
    id: str
    tracking_id: str
    created_at: str
    lifecycle_status: str
    priority_rank: Optional[str] = None
    verified_category: Optional[str] = None
    concise_summary: Optional[str] = None
    message: str = "Incident report submitted successfully."
    ai_pipeline: Optional[Any] = None

class ReportTrackResponse(BaseModel):
    tracking_id: str
    lifecycle_status: str
    user_category: Optional[str] = None
    verified_category: str
    concise_summary: Optional[str] = None
    created_at: Optional[str] = None
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

class AssignWorkOrderRequest(BaseModel):
    department_name: str = Field(..., min_length=1, description="Assigned municipal department")
    justification: Optional[str] = Field("Dispatched work order", description="Dispatch rationale")

class OverrideReportRequest(BaseModel):
    action: str = Field(..., description="Override action type (e.g. SET_PRIORITY, UNLINK_DUPLICATE)")
    justification: str = Field(..., description="Administrative override justification")
    new_priority: Optional[str] = Field(None, description="New priority rank if SET_PRIORITY")

class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Target lifecycle status")
    justification: Optional[str] = Field("Status progression", description="Status transition justification")

class ResolveJobRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=1, description="Mandatory field work resolution notes")
    evidence_photo_url: Optional[str] = Field(None, description="Optional evidence photo URL")
    justification: Optional[str] = Field("Field crew marked job as resolved via Field Portal", description="Resolution justification")

class FieldTaskItem(BaseModel):
    id: str
    tracking_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw_description: str
    verified_category: str
    concise_summary: Optional[str] = None
    formatted_address: Optional[str] = None
    latitude: float
    longitude: float
    priority_rank: str
    priority_score: float
    priority_rationale: Optional[str] = None
    lifecycle_status: str
    assigned_department: Optional[str] = None
    dispatch_timestamp: Optional[str] = None
    duplicate_count: int = 1
    is_duplicate: bool = False
    media_url: Optional[str] = None
    resolution_notes: Optional[str] = None

class FieldTaskListResponse(BaseModel):
    department: str
    role: str
    total: int
    tasks: List[FieldTaskItem]



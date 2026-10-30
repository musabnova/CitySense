import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.models import Report
from apps.api.schemas.report_schemas import (
    ReportCreateResponse,
    ReportTrackResponse,
    ReportDetailResponse
)
from apps.api.services.tracking_service import issue_unique_tracking_id
from apps.api.services.storage_service import storage_service
from apps.api.services.geocoding_service import normalize_address
from apps.api.services.workflow_service import (
    transition_lifecycle_status,
    assign_work_order,
    override_report
)
from apps.api.services.audit_service import get_report_audit_trail

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.post("", response_model=ReportCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_report(
    raw_description: str = Form(..., min_length=5),
    latitude: float = Form(..., ge=-90.0, le=90.0),
    longitude: float = Form(..., ge=-180.0, le=180.0),
    user_category: Optional[str] = Form(None),
    formatted_address: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Public report submission endpoint (Stage 1: Capture).
    Executes under 600ms, strips EXIF, generates unique Tracking ID, and persists report.
    """
    # 1. Media handling & EXIF stripping
    media_url = None
    if photo and photo.filename:
        file_bytes = await photo.read()
        media_url = storage_service.store_incident_media(file_bytes, photo.filename)

    # 2. Address normalization
    resolved_address = normalize_address(latitude, longitude, formatted_address)

    # 3. Tracking ID generation
    tracking_id = issue_unique_tracking_id(db)

    # 4. Verified category default
    default_category = user_category or "Waterlogging & Drainage"

    new_report = Report(
        id=str(uuid.uuid4()),
        tracking_id=tracking_id,
        created_at=datetime.now(timezone.utc),
        raw_description=raw_description.strip(),
        user_category=user_category,
        verified_category=default_category,
        media_url=media_url,
        latitude=latitude,
        longitude=longitude,
        formatted_address=resolved_address,
        concise_summary=raw_description[:100],
        is_duplicate=False,
        master_ticket_id=None,
        duplicate_count=1,
        priority_rank="Priority 3",
        priority_score=40.0,
        priority_rationale="Initial ingestion state; queued for automated multi-factor AI triage.",
        lifecycle_status="Submitted"
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return ReportCreateResponse(
        id=new_report.id,
        tracking_id=new_report.tracking_id,
        created_at=new_report.created_at.isoformat(),
        lifecycle_status=new_report.lifecycle_status,
        message="Incident report submitted successfully."
    )


@router.get("/track/{tracking_id}", response_model=ReportTrackResponse)
def track_report(tracking_id: str, db: Session = Depends(get_db)):
    """Public tracking lookup endpoint via Tracking ID."""
    report = db.query(Report).filter(Report.tracking_id == tracking_id.strip()).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with tracking ID '{tracking_id}' not found."
        )

    return ReportTrackResponse(
        tracking_id=report.tracking_id,
        lifecycle_status=report.lifecycle_status,
        user_category=report.user_category,
        verified_category=report.verified_category,
        concise_summary=report.concise_summary,
        created_at=report.created_at.isoformat() if report.created_at else None,
        formatted_address=report.formatted_address,
        is_duplicate=report.is_duplicate,
        master_ticket_id=report.master_ticket_id,
        priority_rank=report.priority_rank,
        priority_score=float(report.priority_score) if report.priority_score is not None else 0.0,
        priority_rationale=report.priority_rationale,
        assigned_department=report.assigned_department,
        resolution_notes=report.resolution_notes
    )


@router.get("", response_model=List[ReportDetailResponse])
def list_reports(
    lifecycle_status: Optional[str] = Query(None),
    priority_rank: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Administrative listing endpoint with query filters."""
    query = db.query(Report)
    if lifecycle_status:
        query = query.filter(Report.lifecycle_status == lifecycle_status)
    if priority_rank:
        query = query.filter(Report.priority_rank == priority_rank)
    if category:
        query = query.filter(Report.verified_category == category)

    reports = query.order_by(Report.created_at.desc()).all()
    return [
        ReportDetailResponse(
            id=r.id,
            tracking_id=r.tracking_id,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat(),
            raw_description=r.raw_description,
            user_category=r.user_category,
            verified_category=r.verified_category,
            media_url=r.media_url,
            latitude=r.latitude,
            longitude=r.longitude,
            formatted_address=r.formatted_address,
            concise_summary=r.concise_summary,
            is_duplicate=r.is_duplicate,
            master_ticket_id=r.master_ticket_id,
            duplicate_count=r.duplicate_count,
            priority_rank=r.priority_rank,
            priority_score=float(r.priority_score) if r.priority_score is not None else 0.0,
            priority_rationale=r.priority_rationale,
            lifecycle_status=r.lifecycle_status,
            assigned_department=r.assigned_department,
            resolution_notes=r.resolution_notes,
            is_manually_overridden=r.is_manually_overridden,
            override_reason=r.override_reason
        )
        for r in reports
    ]


@router.get("/{report_id}", response_model=ReportDetailResponse)
def get_report_detail(report_id: str, db: Session = Depends(get_db)):
    """Fetch complete detail for a single report."""
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetailResponse(
        id=r.id,
        tracking_id=r.tracking_id,
        created_at=r.created_at.isoformat(),
        updated_at=r.updated_at.isoformat() if r.updated_at else r.created_at.isoformat(),
        raw_description=r.raw_description,
        user_category=r.user_category,
        verified_category=r.verified_category,
        media_url=r.media_url,
        latitude=r.latitude,
        longitude=r.longitude,
        formatted_address=r.formatted_address,
        concise_summary=r.concise_summary,
        is_duplicate=r.is_duplicate,
        master_ticket_id=r.master_ticket_id,
        duplicate_count=r.duplicate_count,
        priority_rank=r.priority_rank,
        priority_score=float(r.priority_score) if r.priority_score is not None else 0.0,
        priority_rationale=r.priority_rationale,
        lifecycle_status=r.lifecycle_status,
        assigned_department=r.assigned_department,
        resolution_notes=r.resolution_notes,
        is_manually_overridden=r.is_manually_overridden,
        override_reason=r.override_reason
    )


@router.post("/{report_id}/override")
def override_report_endpoint(
    report_id: str,
    action: str = Form(...),
    justification: str = Form(...),
    new_priority: Optional[str] = Form(None)
):
    """TASK-045: Administrative priority & duplicate override endpoint."""
    try:
        return override_report(
            report_id=report_id,
            action=action,
            justification=justification,
            new_priority=new_priority
        )
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/{report_id}/audit-trail")
def get_report_audit_trail_endpoint(report_id: str):
    """TASK-046: Chronological audit history trail."""
    return get_report_audit_trail(report_id)


@router.post("/{report_id}/assign")
def assign_work_order_endpoint(
    report_id: str,
    department_name: str = Form(...),
    justification: Optional[str] = Form("Dispatched work order")
):
    """TASK-044: Departmental assignment & child ticket synchronization."""
    try:
        return assign_work_order(
            master_ticket_id=report_id,
            department_name=department_name,
            justification=justification
        )
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{report_id}/status")
def update_status_endpoint(
    report_id: str,
    status: str = Form(...),
    justification: Optional[str] = Form("Status progression")
):
    """TASK-043: Lifecycle state machine progression endpoint."""
    try:
        return transition_lifecycle_status(
            report_id=report_id,
            new_status=status,
            justification=justification
        )
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

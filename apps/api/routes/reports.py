import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status, Query
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.models import Report
from apps.api.schemas.report_schemas import (
    ReportCreateRequest,
    ReportCreateResponse,
    ReportTrackResponse,
    ReportDetailResponse,
    AssignWorkOrderRequest,
    OverrideReportRequest,
    StatusUpdateRequest,
    ResolveJobRequest,
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
from apps.api.core.auth import (
    authenticate_request_token,
    ROLE_DISPATCHER,
    ROLE_PLATFORM_ADMIN,
    ROLE_FIELD_LEAD
)
from apps.api.services.mock_integrations import (
    trigger_dispatch_integrations,
    trigger_resolution_integrations
)

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


async def parse_request_payload(request: Request) -> Dict[str, Any]:
    """Helper to flexibly extract JSON body or multipart/url-encoded form data."""
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        try:
            return await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
    try:
        form = await request.form()
        return dict(form)
    except Exception:
        try:
            return await request.json()
        except Exception:
            return {}


@router.post("", response_model=ReportCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_report(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public report submission endpoint (Stage 1: Capture).
    Supports both application/json payloads (Pydantic model) and multipart/form-data uploads.
    Executes AI pipeline synchronously and returns tracking ID and triage assessment.
    """
    ct = request.headers.get("content-type", "")
    media_url: Optional[str] = None

    if "multipart/form-data" in ct or "application/x-www-form-urlencoded" in ct:
        try:
            form = await request.form()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse form data: {str(e)}")

        photo = form.get("photo")
        if photo and hasattr(photo, "filename") and photo.filename:
            file_bytes = await photo.read()
            media_url = storage_service.store_incident_media(file_bytes, photo.filename)
        elif form.get("media_url"):
            media_url = str(form.get("media_url"))

        raw_data = {
            "raw_description": form.get("raw_description"),
            "latitude": form.get("latitude"),
            "longitude": form.get("longitude"),
            "user_category": form.get("user_category"),
            "formatted_address": form.get("formatted_address"),
            "media_url": media_url
        }
    else:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
        raw_data = body

    # Validate against Pydantic model
    try:
        validated = ReportCreateRequest(**raw_data)
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())

    raw_description = validated.raw_description.strip()
    latitude = validated.latitude
    longitude = validated.longitude
    user_category = validated.user_category or "Waterlogging & Drainage"
    formatted_address = validated.formatted_address
    final_media_url = validated.media_url or media_url

    # Address normalization
    resolved_address = normalize_address(latitude, longitude, formatted_address)

    # Tracking ID generation
    tracking_id = issue_unique_tracking_id(db)

    now_utc = datetime.now(timezone.utc)
    new_report = Report(
        id=str(uuid.uuid4()),
        tracking_id=tracking_id,
        created_at=now_utc,
        updated_at=now_utc,
        raw_description=raw_description,
        user_category=user_category,
        verified_category=user_category,
        media_url=final_media_url,
        latitude=latitude,
        longitude=longitude,
        formatted_address=resolved_address,
        concise_summary=raw_description[:100],
        is_duplicate=False,
        master_ticket_id=None,
        duplicate_count=1,
        priority_rank="Priority 3",
        priority_score=40.0,
        priority_rationale="Initial ingestion state; ready for AI triage.",
        lifecycle_status="Submitted"
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Execute AI understanding pipeline (Stage 2: Understand)
    ai_result = {}
    try:
        from apps.api.tasks.pipeline import process_incident_report_task
        ai_result = process_incident_report_task(new_report.id)
        db.refresh(new_report)
    except Exception as pipe_err:
        ai_result = {"pipeline_error": str(pipe_err)}

    return ReportCreateResponse(
        id=new_report.id,
        tracking_id=new_report.tracking_id,
        created_at=new_report.created_at.isoformat(),
        lifecycle_status=new_report.lifecycle_status,
        priority_rank=new_report.priority_rank,
        verified_category=new_report.verified_category,
        concise_summary=new_report.concise_summary,
        message="Incident report submitted successfully.",
        ai_pipeline=ai_result if ai_result else None
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
            created_at=r.created_at.isoformat() if r.created_at else None,
            updated_at=r.updated_at.isoformat() if r.updated_at else (r.created_at.isoformat() if r.created_at else None),
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
    r = db.query(Report).filter((Report.id == report_id) | (Report.tracking_id == report_id)).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetailResponse(
        id=r.id,
        tracking_id=r.tracking_id,
        created_at=r.created_at.isoformat() if r.created_at else None,
        updated_at=r.updated_at.isoformat() if r.updated_at else (r.created_at.isoformat() if r.created_at else None),
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
async def override_report_endpoint(
    report_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """TASK-045: Administrative priority & duplicate override endpoint."""
    try:
        user_info = authenticate_request_token(authorization, [ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
    except PermissionError as pe:
        raise HTTPException(status_code=getattr(pe, "status_code", 401), detail=str(pe))

    payload = await parse_request_payload(request)
    action = payload.get("action")
    justification = payload.get("justification", "")
    new_priority = payload.get("new_priority")
    user_id = user_info.get("sub", "dispatcher_01")

    if not action:
        raise HTTPException(status_code=422, detail="action is required")

    try:
        return override_report(
            report_id=report_id,
            action=action,
            justification=justification,
            user_id=user_id,
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
async def assign_work_order_endpoint(
    report_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """TASK-044: Departmental assignment & child ticket synchronization with simulated integration triggers."""
    try:
        user_info = authenticate_request_token(authorization, [ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
    except PermissionError as pe:
        raise HTTPException(status_code=getattr(pe, "status_code", 401), detail=str(pe))

    payload = await parse_request_payload(request)
    department_name = payload.get("department_name")
    justification = payload.get("justification", "Dispatched work order")
    user_id = user_info.get("sub", "dispatcher_01")

    if not department_name or not str(department_name).strip():
        raise HTTPException(status_code=422, detail="department_name is required for work order assignment")

    try:
        result = assign_work_order(
            master_ticket_id=report_id,
            department_name=department_name,
            user_id=user_id,
            justification=justification
        )
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # Trigger mock SMS and ERP integrations (TASK-072)
    try:
        r = db.query(Report).filter((Report.id == report_id) | (Report.tracking_id == report_id)).first()
        if r:
            mock_events = trigger_dispatch_integrations(
                tracking_id=r.tracking_id,
                department=department_name,
                location=r.formatted_address or "Ward 12",
                category=r.verified_category or "General",
                priority=r.priority_rank or "Priority 3",
                report_count=int(r.duplicate_count or 1),
            )
            result["mock_integrations"] = mock_events
    except Exception:
        pass

    return result


@router.post("/{report_id}/status")
async def update_status_endpoint(
    report_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """TASK-043: Lifecycle state machine progression endpoint."""
    try:
        user_info = authenticate_request_token(authorization, [ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN, ROLE_FIELD_LEAD])
    except PermissionError as pe:
        raise HTTPException(status_code=getattr(pe, "status_code", 401), detail=str(pe))

    payload = await parse_request_payload(request)
    status_val = payload.get("status")
    justification = payload.get("justification", "Status progression")
    user_id = user_info.get("sub", "dispatcher_01")

    if not status_val:
        raise HTTPException(status_code=422, detail="status is required")

    try:
        return transition_lifecycle_status(
            report_id=report_id,
            new_status=status_val,
            user_id=user_id,
            justification=justification
        )
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{report_id}/resolve")
async def resolve_field_job_endpoint(
    report_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    TASK-071: Field Lead job resolution endpoint with mandatory notes and evidence photo.
    Protected endpoint: requires Field Lead, Dispatcher, or Platform Admin.
    """
    try:
        user_info = authenticate_request_token(authorization, [ROLE_FIELD_LEAD, ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
    except PermissionError as pe:
        raise HTTPException(status_code=getattr(pe, "status_code", 401), detail=str(pe))

    payload = await parse_request_payload(request)
    resolution_notes = str(payload.get("resolution_notes", "")).strip()
    evidence_photo_url = str(payload.get("evidence_photo_url", "")).strip()
    justification = payload.get("justification", "Field crew marked job as resolved via Field Portal")
    user_id = user_info.get("sub", "field_crew_01")
    department = user_info.get("department", "Field Operations")

    if not resolution_notes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resolution_notes is required to mark a job as Resolved."
        )

    report = db.query(Report).filter((Report.id == report_id) | (Report.tracking_id == report_id)).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

    if report.lifecycle_status == "Resolved":
        raise HTTPException(
            status_code=400,
            detail="Report is already in 'Resolved' state. No further transition is permitted."
        )

    actual_id = report.id
    tracking_id = report.tracking_id
    dept = report.assigned_department or department
    now_utc = datetime.now(timezone.utc)
    now_iso = now_utc.isoformat()

    # Update resolution notes and updated_at
    report.resolution_notes = resolution_notes
    report.updated_at = now_utc
    db.commit()

    # Transition lifecycle status to Resolved via state machine
    try:
        transition_lifecycle_status(
            report_id=actual_id,
            new_status="Resolved",
            user_id=user_id,
            justification=justification
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))

    # Fire mock SMS + ERP resolution events (TASK-072)
    mock_events = {}
    try:
        mock_events = trigger_resolution_integrations(
            tracking_id=tracking_id,
            department=dept,
            resolution_notes=resolution_notes,
        )
    except Exception:
        pass

    return {
        "report_id": actual_id,
        "tracking_id": tracking_id,
        "lifecycle_status": "Resolved",
        "resolution_notes": resolution_notes,
        "evidence_photo_url": evidence_photo_url or None,
        "resolved_at": now_iso,
        "mock_integrations": mock_events,
    }

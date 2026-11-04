"""
FastAPI Route Handlers for Field Lead Tasks (Phase 11: TASK-070)
================================================================
GET /api/v1/field/tasks
"""

from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.models import Report
from apps.api.schemas.report_schemas import FieldTaskListResponse, FieldTaskItem
from apps.api.core.auth import (
    authenticate_request_token,
    ROLE_FIELD_LEAD,
    ROLE_DISPATCHER,
    ROLE_PLATFORM_ADMIN
)

router = APIRouter(prefix="/api/v1/field", tags=["Field"])


@router.get("/tasks", response_model=FieldTaskListResponse)
def get_field_tasks(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    TASK-070: Simplified task queue for field maintenance leads.
    Department filtering is strictly derived from the validated JWT token claims,
    preventing tampering via query parameters.
    """
    try:
        user_info = authenticate_request_token(authorization, [ROLE_FIELD_LEAD, ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
    except PermissionError as pe:
        raise HTTPException(status_code=getattr(pe, "status_code", 401), detail=str(pe))

    token_department = user_info.get("department")
    token_role = user_info.get("role")

    query = db.query(Report).filter(Report.lifecycle_status.in_(["Assigned", "Resolved"]))

    # Platform Admin sees all; department-specific field lead only sees their department's work orders
    if token_role != ROLE_PLATFORM_ADMIN and token_department:
        query = query.filter(Report.assigned_department == token_department)

    reports = query.order_by(Report.priority_score.desc(), Report.created_at.asc()).all()

    tasks: List[FieldTaskItem] = []
    for r in reports:
        dispatch_ts = None
        if r.dispatch_timestamp:
            dispatch_ts = r.dispatch_timestamp.isoformat() if hasattr(r.dispatch_timestamp, "isoformat") else str(r.dispatch_timestamp)

        tasks.append(
            FieldTaskItem(
                id=r.id,
                tracking_id=r.tracking_id,
                created_at=r.created_at.isoformat() if r.created_at else None,
                updated_at=r.updated_at.isoformat() if r.updated_at else None,
                raw_description=r.raw_description,
                verified_category=r.verified_category,
                concise_summary=r.concise_summary,
                formatted_address=r.formatted_address,
                latitude=float(r.latitude) if r.latitude is not None else 0.0,
                longitude=float(r.longitude) if r.longitude is not None else 0.0,
                priority_rank=r.priority_rank,
                priority_score=float(r.priority_score) if r.priority_score is not None else 0.0,
                priority_rationale=r.priority_rationale,
                lifecycle_status=r.lifecycle_status,
                assigned_department=r.assigned_department,
                dispatch_timestamp=dispatch_ts,
                duplicate_count=int(r.duplicate_count) if r.duplicate_count else 1,
                is_duplicate=bool(r.is_duplicate),
                media_url=r.media_url,
                resolution_notes=r.resolution_notes,
            )
        )

    return {
        "department": token_department or "All Departments",
        "role": token_role,
        "total": len(tasks),
        "tasks": tasks
    }


"""
FastAPI Route Handlers for Cluster Endpoints (Phase 6: Reveal)
=============================================================
TASK-041: POST /api/v1/clusters/{cluster_id}/action-brief
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional, Dict, Any
from pathlib import Path

from apps.api.services.clustering_service import detect_spatial_clusters
from apps.api.services.action_brief_service import generate_action_brief_from_reports
from apps.api.core.auth import authenticate_request_token, ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN

router = APIRouter(prefix="/api/v1/clusters", tags=["clusters"])
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "citysense.db"


@router.post("/{cluster_id}/action-brief")
def generate_cluster_action_brief(
    cluster_id: str,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    TASK-041: Generates executive action brief for a cluster.
    Protected endpoint: requires Dispatcher or Platform Admin role.
    """
    # Enforce RBAC
    if authorization:
        try:
            authenticate_request_token(authorization, [ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
        except PermissionError as pe:
            raise HTTPException(status_code=getattr(pe, "status_code", 403), detail=str(pe))

    clusters = detect_spatial_clusters(db_path=str(DB_PATH))
    matched_cluster = None
    for c in clusters:
        if c["cluster_id"] == cluster_id:
            matched_cluster = c
            break

    if not matched_cluster:
        raise HTTPException(status_code=404, detail=f"Cluster '{cluster_id}' not found.")

    brief = generate_action_brief_from_reports(
        cluster_id=matched_cluster["cluster_id"],
        cluster_title=matched_cluster["title"],
        reports=matched_cluster["reports"],
        center_point=matched_cluster["center_point"]
    )
    return brief


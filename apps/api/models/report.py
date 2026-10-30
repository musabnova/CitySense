import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Boolean, Integer, Numeric, DateTime, ForeignKey
from apps.api.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tracking_id = Column(String(12), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Citizen Input Layer
    raw_description = Column(Text, nullable=False)
    user_category = Column(String(64), nullable=True)
    media_url = Column(String(512), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    formatted_address = Column(String(256), nullable=True)

    # AI Intelligence Layer
    verified_category = Column(String(64), nullable=False)
    concise_summary = Column(String(256), nullable=True)
    is_duplicate = Column(Boolean, default=False, nullable=False)
    master_ticket_id = Column(String(36), ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)
    duplicate_count = Column(Integer, default=1, nullable=False)

    # Vector Embedding & Prioritization
    description_embedding_json = Column(Text, nullable=True)
    priority_rank = Column(String(32), default="Priority 4", nullable=False)
    priority_score = Column(Numeric(5, 2), default=0.00, nullable=False)
    priority_rationale = Column(Text, nullable=True)

    # Workflow & Operations
    lifecycle_status = Column(String(32), default="Submitted", nullable=False)
    assigned_department = Column(String(128), nullable=True)
    dispatch_timestamp = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Audit & Overrides
    is_manually_overridden = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text, nullable=True)
    overridden_by_user_id = Column(String(36), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "tracking_id": self.tracking_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "raw_description": self.raw_description,
            "user_category": self.user_category,
            "verified_category": self.verified_category,
            "media_url": self.media_url,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "formatted_address": self.formatted_address,
            },
            "concise_summary": self.concise_summary,
            "is_duplicate": self.is_duplicate,
            "master_ticket_id": self.master_ticket_id,
            "duplicate_count": self.duplicate_count,
            "priority_rank": self.priority_rank,
            "priority_score": float(self.priority_score) if self.priority_score is not None else 0.0,
            "priority_rationale": self.priority_rationale,
            "lifecycle_status": self.lifecycle_status,
            "assigned_department": self.assigned_department,
            "dispatch_timestamp": self.dispatch_timestamp.isoformat() if self.dispatch_timestamp else None,
            "resolution_notes": self.resolution_notes,
            "is_manually_overridden": self.is_manually_overridden,
            "override_reason": self.override_reason,
        }


import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from apps.api.core.database import Base

class ReportAuditLog(Base):
    __tablename__ = "report_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    action_type = Column(String(64), nullable=False)
    previous_value = Column(Text, nullable=False)
    new_value = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "report_id": self.report_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action_type": self.action_type,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "justification": self.justification
        }


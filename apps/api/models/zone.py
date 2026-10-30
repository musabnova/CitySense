import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from apps.api.core.database import Base

class AdministrativeZone(Base):
    __tablename__ = "administrative_zones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(64), nullable=False)
    level = Column(String(32), nullable=False) # City, Division, Zone, Ward
    parent_id = Column(String(36), ForeignKey("administrative_zones.id", ondelete="SET NULL"), nullable=True)
    boundary_geojson = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "parent_id": self.parent_id,
            "boundary_geojson": self.boundary_geojson,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


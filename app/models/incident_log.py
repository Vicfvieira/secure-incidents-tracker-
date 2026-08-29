import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IncidentLog(Base):
    """Immutable audit trail entry recording a single field change on an incident."""

    __tablename__ = "incident_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str] = mapped_column(String(255), nullable=True)
    new_value: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    incident = relationship("Incident", back_populates="logs")
    changed_by = relationship("User", back_populates="incident_logs")

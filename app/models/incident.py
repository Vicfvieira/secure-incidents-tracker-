import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.encryption import EncryptedJSON, EncryptedString
from app.database import Base


class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentType(str, enum.Enum):
    PHISHING = "PHISHING"
    DATA_LEAK = "DATA_LEAK"
    MALWARE = "MALWARE"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DENIAL_OF_SERVICE = "DENIAL_OF_SERVICE"
    OTHER = "OTHER"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Field-level encryption at rest for sensitive incident details.
    description: Mapped[str] = mapped_column(EncryptedString, nullable=False)
    indicators: Mapped[list] = mapped_column(EncryptedJSON, nullable=True, default=list)

    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity"), nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status"), nullable=False, default=IncidentStatus.OPEN
    )
    type: Mapped[IncidentType] = mapped_column(Enum(IncidentType, name="incident_type"), nullable=False)

    reporter_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    reporter = relationship("User", back_populates="reported_incidents", foreign_keys=[reporter_id])
    logs = relationship(
        "IncidentLog", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentLog.timestamp"
    )

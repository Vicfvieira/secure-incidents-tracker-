from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.incident_log import IncidentLog
from app.models.user import User, UserRole
from app.schemas.incident import IncidentCreate, IncidentUpdate


def create_incident(db: Session, payload: IncidentCreate, reporter: User) -> Incident:
    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        type=payload.type,
        indicators=payload.indicators,
        reporter_id=reporter.id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def list_incidents(
    db: Session,
    current_user: User,
    page: int = 1,
    limit: int = 20,
    severity: IncidentSeverity | None = None,
    status: IncidentStatus | None = None,
) -> tuple[list[Incident], int]:
    filters = []
    if current_user.role == UserRole.REPORTER:
        filters.append(Incident.reporter_id == current_user.id)
    if severity is not None:
        filters.append(Incident.severity == severity)
    if status is not None:
        filters.append(Incident.status == status)

    total = db.scalar(select(func.count()).select_from(Incident).where(*filters)) or 0

    stmt = (
        select(Incident)
        .where(*filters)
        .order_by(Incident.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    items = list(db.scalars(stmt))
    return items, total


def get_incident(db: Session, incident_id: str) -> Incident | None:
    return db.get(Incident, incident_id)


def update_incident(db: Session, incident: Incident, payload: IncidentUpdate, changed_by: User) -> Incident:
    """Applies severity/status changes and writes an immutable audit log entry per changed field."""
    updates = payload.model_dump(exclude_unset=True)

    for field_name in ("severity", "status"):
        if field_name not in updates:
            continue
        new_value = updates[field_name]
        old_value = getattr(incident, field_name)
        if old_value == new_value:
            continue

        db.add(
            IncidentLog(
                incident_id=incident.id,
                changed_by_id=changed_by.id,
                field_name=field_name,
                old_value=old_value.value if old_value is not None else None,
                new_value=new_value.value if new_value is not None else None,
            )
        )
        setattr(incident, field_name, new_value)

    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident: Incident) -> None:
    db.delete(incident)
    db.commit()


def list_incident_logs(db: Session, incident_id: str) -> list[IncidentLog]:
    stmt = (
        select(IncidentLog)
        .where(IncidentLog.incident_id == incident_id)
        .order_by(IncidentLog.timestamp.asc())
    )
    return list(db.scalars(stmt))

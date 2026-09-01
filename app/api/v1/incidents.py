import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.incident import (
    create_incident,
    delete_incident,
    get_incident,
    list_incident_logs,
    list_incidents,
    update_incident,
)
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models.incident import IncidentSeverity, IncidentStatus
from app.models.user import User, UserRole
from app.schemas.incident import IncidentCreate, IncidentPage, IncidentRead, IncidentUpdate
from app.schemas.incident_log import IncidentLogRead

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _get_owned_or_visible_incident(db: Session, incident_id: str, current_user: User):
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    if current_user.role == UserRole.REPORTER and incident.reporter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this incident")
    return incident


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    return create_incident(db, payload, current_user)


@router.get("", response_model=IncidentPage)
def list_all(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    severity: IncidentSeverity | None = Query(default=None),
    status: IncidentStatus | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentPage:
    items, total = list_incidents(db, current_user, page=page, limit=limit, severity=severity, status=status)
    total_pages = math.ceil(total / limit) if total else 0
    return IncidentPage(items=items, total=total, page=page, limit=limit, total_pages=total_pages)


@router.get("/{incident_id}", response_model=IncidentRead)
def get_one(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentRead:
    return _get_owned_or_visible_incident(db, incident_id, current_user)


@router.patch("/{incident_id}", response_model=IncidentRead)
def update(
    incident_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN)),
) -> IncidentRead:
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return update_incident(db, incident, payload, current_user)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    delete_incident(db, incident)


@router.get("/{incident_id}/logs", response_model=list[IncidentLogRead])
def get_logs(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN)),
) -> list[IncidentLogRead]:
    incident = get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return list_incident_logs(db, incident_id)

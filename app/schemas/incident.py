from datetime import datetime

from pydantic import BaseModel, Field

from app.models.incident import IncidentSeverity, IncidentStatus, IncidentType


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    severity: IncidentSeverity
    type: IncidentType
    indicators: list[str] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None


class IncidentRead(BaseModel):
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    type: IncidentType
    indicators: list[str]
    reporter_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentPage(BaseModel):
    items: list[IncidentRead]
    total: int
    page: int
    limit: int
    total_pages: int

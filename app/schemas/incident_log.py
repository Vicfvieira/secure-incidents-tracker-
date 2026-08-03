from datetime import datetime

from pydantic import BaseModel


class IncidentLogRead(BaseModel):
    id: str
    incident_id: str
    changed_by_id: str
    field_name: str
    old_value: str | None
    new_value: str | None
    timestamp: datetime

    model_config = {"from_attributes": True}

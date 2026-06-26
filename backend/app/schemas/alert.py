from typing import Optional
from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    title: str
    level: str = Field(default="major", description="critical/major/minor/info")
    device_id: Optional[str] = None
    plot_id: Optional[str] = None
    rule_id: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    description: Optional[str] = None


class AlertResponse(AlertBase):
    id: str
    status: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    handled_by: Optional[str] = None
    handled_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertUpdateStatus(BaseModel):
    status: str = Field(..., description="acknowledged/handled/closed/archived")

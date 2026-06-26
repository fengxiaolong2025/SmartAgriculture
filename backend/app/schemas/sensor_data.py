from typing import Optional
from pydantic import BaseModel, Field


class SensorDataBase(BaseModel):
    device_id: str
    metric_name: str
    value: float
    unit: str = ""
    time: str
    plot_id: Optional[str] = None


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataResponse(SensorDataBase):
    id: str

    model_config = {"from_attributes": True}


class SensorDataQuery(BaseModel):
    device_id: Optional[str] = None
    metric_name: Optional[str] = None
    plot_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=1000)

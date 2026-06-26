from typing import Optional
from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    device_type: str = Field(..., description="sensor/controller/actuator/gateway/camera")
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    plot_id: Optional[str] = None
    status: str = Field(default="online")
    is_active: bool = True
    description: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    plot_id: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class DeviceResponse(DeviceBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}

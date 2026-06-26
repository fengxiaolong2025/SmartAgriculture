from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin


class SensorData(Base, UUIDMixin):
    __tablename__ = "sensor_data"

    device_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="指标名称: temperature/humidity/soil_moisture/light/co2/soil_ph/wind_speed/rainfall",
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    time: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    plot_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)

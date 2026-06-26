from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class VentilationRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ventilation_records"

    plot_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    start_time: Mapped[str] = mapped_column(String(30), nullable=False)
    end_time: Mapped[str] = mapped_column(String(30), nullable=True)
    fan_speed: Mapped[float] = mapped_column(Float, nullable=True, comment="风速（档位或转速）")
    operator_id: Mapped[str] = mapped_column(String(32), nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

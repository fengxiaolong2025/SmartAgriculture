from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class PestControlRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pest_control_records"

    plot_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    pesticide_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, comment="用量（升或克）")
    method: Mapped[str] = mapped_column(String(30), nullable=True)
    apply_time: Mapped[str] = mapped_column(String(30), nullable=False)
    target_pest: Mapped[str] = mapped_column(String(100), nullable=True, comment="防治对象")
    operator_id: Mapped[str] = mapped_column(String(32), nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

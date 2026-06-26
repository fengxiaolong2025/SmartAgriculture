from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class FertilizationRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "fertilization_records"

    plot_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    fertilizer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, comment="用量（kg）")
    method: Mapped[str] = mapped_column(String(30), nullable=True, comment="施肥方式")
    apply_time: Mapped[str] = mapped_column(String(30), nullable=False)
    operator_id: Mapped[str] = mapped_column(String(32), nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class HarvestRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "harvest_records"

    plot_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    crop_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    harvest_time: Mapped[str] = mapped_column(String(30), nullable=False)
    yield_amount: Mapped[float] = mapped_column(Float, nullable=False, comment="产量（kg）")
    quality_grade: Mapped[str] = mapped_column(String(10), nullable=True, comment="质量等级: A/B/C")
    operator_id: Mapped[str] = mapped_column(String(32), nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

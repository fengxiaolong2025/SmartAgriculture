from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class Plot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "plots"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    area: Mapped[float] = mapped_column(Float, nullable=True, comment="面积（亩）")
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    crop_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    planting_date: Mapped[str] = mapped_column(String(20), nullable=True, comment="定植日期")

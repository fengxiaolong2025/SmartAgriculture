from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class Crop(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "crops"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variety: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True, comment="作物分类")
    growth_cycle_days: Mapped[int] = mapped_column(Integer, nullable=True, comment="生长周期（天）")
    optimal_temp_min: Mapped[float] = mapped_column(Float, nullable=True)
    optimal_temp_max: Mapped[float] = mapped_column(Float, nullable=True)
    optimal_humidity_min: Mapped[float] = mapped_column(Float, nullable=True)
    optimal_humidity_max: Mapped[float] = mapped_column(Float, nullable=True)
    optimal_soil_moisture_min: Mapped[float] = mapped_column(Float, nullable=True)
    optimal_soil_moisture_max: Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class AlertRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    operator: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="比较运算符: gt/lt/gte/lte/eq",
    )
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="major",
        comment="告警级别: critical/major/minor/info",
    )
    device_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    plot_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

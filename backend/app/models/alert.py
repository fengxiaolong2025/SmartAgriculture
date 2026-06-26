from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class Alert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="告警级别: critical/major/minor/info",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="triggered",
        index=True,
        comment="状态: triggered/acknowledged/handled/closed/archived",
    )
    device_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    plot_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    rule_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=True)
    metric_value: Mapped[float] = mapped_column(nullable=True)
    threshold_value: Mapped[float] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    acknowledged_by: Mapped[str] = mapped_column(String(32), nullable=True)
    acknowledged_at: Mapped[str] = mapped_column(String(30), nullable=True)
    handled_by: Mapped[str] = mapped_column(String(32), nullable=True)
    handled_at: Mapped[str] = mapped_column(String(30), nullable=True)

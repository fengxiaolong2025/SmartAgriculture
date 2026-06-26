from sqlalchemy import String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class Device(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "devices"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="设备类型: sensor/controller/actuator/gateway/camera",
    )
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=True)
    plot_id: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="online", comment="online/offline/maintenance")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

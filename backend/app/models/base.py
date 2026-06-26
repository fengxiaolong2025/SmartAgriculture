import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    """UUID 主键 Mixin - 使用 32 位 UUID hex 字符串以兼容 SQLite。"""
    id: Mapped[str] = mapped_column(
        CHAR(32),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
        index=True,
    )


class TimestampMixin:
    """时间戳 Mixin - 自动管理创建和更新时间。"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

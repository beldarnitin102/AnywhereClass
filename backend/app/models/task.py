
from datetime import datetime, timezone

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text

from app.db.base import Base


class TaskRecord(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True
    )
    owner_id: Mapped[str | None] = mapped_column(
    String(36),
    ForeignKey("users.id", ondelete="RESTRICT"),
    nullable=True,
    index=True,
    )
    command: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False,
        default="awaiting_approval"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    plan: Mapped[list[str]] = mapped_column(
        JSON, nullable=False
    )
    mode: Mapped[str] = mapped_column(
        String(30), nullable=False,
        default="simulation"
    )

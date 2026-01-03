"""Request logging model for API analytics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass
class RequestLog(db.Model):
    """Model to log API requests for analytics."""

    __tablename__ = "request_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, server_default=func.now()
    )
    method: Mapped[str] = mapped_column(String(10))
    endpoint: Mapped[str] = mapped_column(String(200))
    status_code: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    @classmethod
    def create(
        cls, method: str, endpoint: str, status_code: int, user_id: int | None = None
    ) -> RequestLog:
        """Factory method to create a new request log entry."""
        log = cls(
            method=method, endpoint=endpoint, status_code=status_code, user_id=user_id
        )
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def get_recent(cls, limit: int = 10) -> list[RequestLog]:
        """Get most recent request logs."""
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_daily_counts(cls, days: int = 30) -> list[tuple]:
        """Get daily request counts for the last N days."""
        # Use func.date() for SQLite compatibility instead of cast(, Date)
        date_col = func.date(cls.timestamp)

        return (
            db.session.query(
                date_col.label("date"),
                func.count(cls.id).label("count"),
            )
            .group_by(date_col)
            .order_by(date_col.desc())
            .limit(days)
            .all()
        )

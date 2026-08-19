import uuid
from datetime import datetime, timedelta
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class TyreCompound(str, enum.Enum):
    SOFT = "soft"
    MEDIUM = "medium"
    HARD = "hard"
    INTERMEDIATE = "intermediate"
    WET = "wet"
    C0 = "c0"
    C1 = "c1"
    C2 = "c2"
    C3 = "c3"
    C4 = "c4"
    C5 = "c5"
    UNKNOWN = "unknown"


class PitStop(Base):
    __tablename__ = "pit_stops"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    pit_duration_seconds: Mapped[float | None] = mapped_column(Float)
    total_duration_seconds: Mapped[float | None] = mapped_column(Float)
    tyre_compound_in: Mapped[str | None] = mapped_column(String(32))
    tyre_compound_out: Mapped[str | None] = mapped_column(String(32))
    tyre_age_in: Mapped[int | None] = mapped_column(Integer)
    is_driver_change: Mapped[bool] = mapped_column(default=False)
    is_penalty: Mapped[bool] = mapped_column(default=False)
    position_in: Mapped[int | None] = mapped_column(Integer)
    position_out: Mapped[int | None] = mapped_column(Integer)

    session = relationship("Session")
    driver = relationship("Driver")

    __table_args__ = (Index("idx_pit_session_driver_lap", "session_id", "driver_id", "lap_number"),)


class TyreSet(Base):
    __tablename__ = "tyre_sets"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    compound: Mapped[str] = mapped_column(String(32), nullable=False)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    total_laps: Mapped[int] = mapped_column(Integer, default=0)
    is_used: Mapped[bool] = mapped_column(default=False)
    is_available: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (Index("idx_tyre_session_driver", "session_id", "driver_id"),)

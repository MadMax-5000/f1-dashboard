import uuid
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Lap(Base):
    __tablename__ = "laps"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer)
    time_seconds: Mapped[float | None] = mapped_column(Float)
    sector_1_time: Mapped[float | None] = mapped_column(Float)
    sector_2_time: Mapped[float | None] = mapped_column(Float)
    sector_3_time: Mapped[float | None] = mapped_column(Float)
    speed_trap_kmh: Mapped[float | None] = mapped_column(Float)
    is_pit_lap: Mapped[bool] = mapped_column(default=False)
    is_out_lap: Mapped[bool] = mapped_column(default=False)
    is_in_lap: Mapped[bool] = mapped_column(default=False)
    tyre_compound: Mapped[str | None] = mapped_column(String(32))
    tyre_age_laps: Mapped[int | None] = mapped_column(Integer)
    is_valid: Mapped[bool] = mapped_column(default=True)
    fresh_tyre: Mapped[bool] = mapped_column(default=False)
    track_status: Mapped[str | None] = mapped_column(String(32))
    drs_used: Mapped[bool] = mapped_column(default=False)
    laps_led: Mapped[int] = mapped_column(Integer, default=0)

    session = relationship("Session", back_populates="laps")
    driver = relationship("Driver", back_populates="laps")

    __table_args__ = (
        Index("idx_lap_session_driver", "session_id", "driver_id"),
        Index("idx_lap_session_lap", "session_id", "lap_number"),
        UniqueConstraint("session_id", "driver_id", "lap_number", name="uq_session_driver_lap"),
    )

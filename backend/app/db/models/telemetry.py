import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TelemetryFrame(Base):
    __tablename__ = "telemetry_frames"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    distance: Mapped[float] = mapped_column(Float, nullable=False)
    speed: Mapped[float | None] = mapped_column(Float)
    rpm: Mapped[float | None] = mapped_column(Float)
    gear: Mapped[int | None] = mapped_column(Integer)
    throttle: Mapped[float | None] = mapped_column(Float)
    brake: Mapped[float | None] = mapped_column(Float)
    drs: Mapped[bool | None] = mapped_column(Boolean)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)
    z: Mapped[float | None] = mapped_column(Float)

    session = relationship("Session")
    driver = relationship("Driver", back_populates="telemetry")

    __table_args__ = (
        Index("idx_tf_session_driver_lap", "session_id", "driver_id", "lap_number"),
        Index("idx_tf_timestamp", "timestamp"),
        Index("idx_tf_session_distance", "session_id", "distance"),
    )


class CarData(Base):
    __tablename__ = "car_data"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    speed: Mapped[float | None] = mapped_column(Float)
    rpm: Mapped[float | None] = mapped_column(Float)
    gear: Mapped[int | None] = mapped_column(Integer)
    throttle: Mapped[float | None] = mapped_column(Float)
    brake: Mapped[float | None] = mapped_column(Float)
    drs: Mapped[bool | None] = mapped_column(Boolean)
    ers_deploy: Mapped[float | None] = mapped_column(Float)
    ers_harvest: Mapped[float | None] = mapped_column(Float)
    ers_battery: Mapped[float | None] = mapped_column(Float)
    tyre_temp_inner: Mapped[float | None] = mapped_column(Float)
    tyre_temp_middle: Mapped[float | None] = mapped_column(Float)
    tyre_temp_outer: Mapped[float | None] = mapped_column(Float)
    tyre_pressure: Mapped[float | None] = mapped_column(Float)
    brake_temp: Mapped[float | None] = mapped_column(Float)
    fuel_remaining: Mapped[float | None] = mapped_column(Float)
    fuel_load: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        Index("idx_cd_session_driver", "session_id", "driver_id"),
        Index("idx_cd_timestamp", "timestamp"),
    )

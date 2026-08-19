import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Enum, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class EventType(str, enum.Enum):
    SAFETY_CAR = "safety_car"
    VIRTUAL_SAFETY_CAR = "virtual_safety_car"
    RED_FLAG = "red_flag"
    YELLOW_FLAG = "yellow_flag"
    OVERTAKE = "overtake"
    INCIDENT = "incident"
    PENALTY = "penalty"
    PIT_STOP = "pit_stop"
    DRS_ACTIVATION = "drs_activation"
    RETIREMENT = "retirement"
    WEATHER_CHANGE = "weather_change"
    TRACK_LIMIT = "track_limit"


class RaceEvent(Base):
    __tablename__ = "race_events"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str | None] = mapped_column(String(32))
    category: Mapped[str | None] = mapped_column(String(32))
    data: Mapped[dict | None] = mapped_column(nullable=True)

    session = relationship("Session")

    __table_args__ = (
        Index("idx_event_session_ts", "session_id", "timestamp"),
        Index("idx_event_session_type", "session_id", "event_type"),
        Index("idx_event_session_lap", "session_id", "lap_number"),
    )


class Incident(Base):
    __tablename__ = "incidents"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    driver_b_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    incident_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(64))
    severity: Mapped[str | None] = mapped_column(String(16))
    caused_retirement: Mapped[bool] = mapped_column(default=False)
    caused_safety_car: Mapped[bool] = mapped_column(default=False)
    video_timestamp: Mapped[float | None] = mapped_column(Float)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)

    driver_a = relationship("Driver", foreign_keys=[driver_a_id])
    driver_b = relationship("Driver", foreign_keys=[driver_b_id])
    session = relationship("Session")


class Penalty(Base):
    __tablename__ = "penalties"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    penalty_type: Mapped[str] = mapped_column(String(64), nullable=False)
    penalty_time: Mapped[float | None] = mapped_column(Float)
    penalty_positions: Mapped[int | None] = mapped_column(Integer)
    infringement: Mapped[str | None] = mapped_column(Text)
    is_served: Mapped[bool] = mapped_column(default=False)
    served_at_lap: Mapped[int | None] = mapped_column(Integer)

    driver = relationship("Driver")
    session = relationship("Session")


class SafetyCar(Base):
    __tablename__ = "safety_cars"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    deployment_time: Mapped[datetime] = mapped_column(nullable=False)
    deployment_lap: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieval_time: Mapped[datetime | None] = mapped_column()
    retrieval_lap: Mapped[int | None] = mapped_column(Integer)
    duration_laps: Mapped[int | None] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(16), default="safety_car")
    reason: Mapped[str | None] = mapped_column(Text)
    caused_by_incident_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("incidents.id"))

    session = relationship("Session")


class Overtake(Base):
    __tablename__ = "overtakes"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    overtaking_driver_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("drivers.id"), nullable=False
    )
    overtaken_driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    drs_used: Mapped[bool] = mapped_column(default=False)
    location: Mapped[str | None] = mapped_column(String(64))
    corner_number: Mapped[int | None] = mapped_column(Integer)
    straight_length: Mapped[float | None] = mapped_column(Float)
    speed_differential: Mapped[float | None] = mapped_column(Float)
    probability_success: Mapped[float | None] = mapped_column(Float)
    video_timestamp: Mapped[float | None] = mapped_column(Float)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)

    overtaking_driver = relationship("Driver", foreign_keys=[overtaking_driver_id])
    overtaken_driver = relationship("Driver", foreign_keys=[overtaken_driver_id])
    session = relationship("Session")

    __table_args__ = (Index("idx_overtake_session_lap", "session_id", "lap_number"),)

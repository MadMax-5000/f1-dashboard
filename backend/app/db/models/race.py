import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class SessionType(str, enum.Enum):
    PRACTICE_1 = "practice_1"
    PRACTICE_2 = "practice_2"
    PRACTICE_3 = "practice_3"
    QUALIFYING = "qualifying"
    QUALIFYING_1 = "qualifying_1"
    QUALIFYING_2 = "qualifying_2"
    QUALIFYING_3 = "qualifying_3"
    SPRINT_QUALIFYING = "sprint_qualifying"
    SPRINT = "sprint"
    RACE = "race"


class Race(Base):
    __tablename__ = "races"

    circuit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("circuits.id"), nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(512))
    race_ref: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scheduled_laps: Mapped[int | None] = mapped_column(Integer)
    scheduled_distance_km: Mapped[float | None] = mapped_column(Float)
    weekend_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    weekend_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    championship: Mapped[str] = mapped_column(
        String(64), default="FIA Formula One World Championship"
    )
    is_sprint_weekend: Mapped[bool] = mapped_column(default=False)

    circuit = relationship("Circuit", back_populates="races")
    sessions = relationship("Session", back_populates="race", cascade="all, delete-orphan")
    entries = relationship("RaceEntry", back_populates="race", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("season", "round", name="uq_season_round"),
        Index("idx_race_season", "season"),
        Index("idx_race_circuit", "circuit_id"),
    )


class Session(Base):
    __tablename__ = "sessions"

    race_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("races.id"), nullable=False)
    session_type: Mapped[SessionType] = mapped_column(Enum(SessionType), nullable=False)
    session_name: Mapped[str] = mapped_column(String(128), nullable=False)
    session_ref: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[float | None] = mapped_column(Float)
    total_laps: Mapped[int | None] = mapped_column(Integer)
    weather_simulated: Mapped[bool] = mapped_column(default=False)

    race = relationship("Race", back_populates="sessions")
    laps = relationship("Lap", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_session_race_type", "race_id", "session_type"),)


class RaceEntry(Base):
    __tablename__ = "race_entries"

    race_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("races.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    driver_number: Mapped[int] = mapped_column(Integer, nullable=False)
    starting_position: Mapped[int | None] = mapped_column(Integer)
    finishing_position: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(32))
    points: Mapped[float] = mapped_column(Float, default=0.0)
    car_number: Mapped[int | None] = mapped_column(Integer)

    race = relationship("Race", back_populates="entries")
    driver = relationship("Driver", backref="race_entries")
    team = relationship("Team", back_populates="entries")

    __table_args__ = (
        UniqueConstraint("race_id", "driver_id", name="uq_race_driver"),
        Index("idx_entry_race", "race_id"),
        Index("idx_entry_driver", "driver_id"),
    )

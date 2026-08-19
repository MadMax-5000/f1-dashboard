import uuid
from datetime import date
from sqlalchemy import String, Integer, Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Driver(Base):
    __tablename__ = "drivers"

    driver_number: Mapped[int] = mapped_column(Integer, nullable=False)
    broadcast_name: Mapped[str] = mapped_column(String(128), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    tla: Mapped[str] = mapped_column(String(3), nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False)
    team_name: Mapped[str] = mapped_column(String(128), nullable=False)
    headshot_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    driver_ref: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    teams = relationship("Team", secondary="race_entries", viewonly=True)
    laps = relationship("Lap", back_populates="driver")
    telemetry = relationship("TelemetryFrame", back_populates="driver")


class DriverStanding(Base):
    __tablename__ = "driver_standings"

    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    race_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("races.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    season: Mapped[int] = mapped_column(Integer, nullable=False)

    driver = relationship("Driver", backref="standings")
    race = relationship("Race", backref="driver_standings")

    __table_args__ = (UniqueConstraint("driver_id", "race_id", name="uq_driver_race_standing"),)

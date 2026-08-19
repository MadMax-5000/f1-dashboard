import uuid
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    constructor_ref: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    nationality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    base: Mapped[str | None] = mapped_column(String(256), nullable=True)
    team_principal: Mapped[str | None] = mapped_column(String(128), nullable=True)
    chassis: Mapped[str | None] = mapped_column(String(64), nullable=True)
    power_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)

    entries = relationship("RaceEntry", back_populates="team")


class TeamStanding(Base):
    __tablename__ = "team_standings"

    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    race_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("races.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    season: Mapped[int] = mapped_column(Integer, nullable=False)

    team = relationship("Team", backref="standings")
    race = relationship("Race", backref="team_standings")

    __table_args__ = (UniqueConstraint("team_id", "race_id", name="uq_team_race_standing"),)

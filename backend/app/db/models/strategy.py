import uuid
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, Enum, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class StrategyCategory(str, enum.Enum):
    OPTIMAL = "optimal"
    ALTERNATIVE = "alternative"
    COUNTERFACTUAL = "counterfactual"
    RL_GENERATED = "rl_generated"
    HUMAN_DEFINED = "human_defined"


class Strategy(Base):
    __tablename__ = "strategies"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[StrategyCategory] = mapped_column(Enum(StrategyCategory), nullable=False)
    expected_finish_position: Mapped[int | None] = mapped_column(Integer)
    expected_total_time: Mapped[float | None] = mapped_column(Float)
    expected_points: Mapped[float | None] = mapped_column(Float)
    risk_score: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    is_selected: Mapped[bool] = mapped_column(default=False)
    simulation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("simulation_runs.id"))

    session = relationship("Session")
    driver = relationship("Driver")
    steps = relationship("StrategyStep", back_populates="strategy", cascade="all, delete-orphan")
    simulation = relationship("SimulationRun")

    __table_args__ = (Index("idx_strategy_session_driver", "session_id", "driver_id"),)


class StrategyStep(Base):
    __tablename__ = "strategy_steps"

    strategy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("strategies.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_start: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    tyre_compound: Mapped[str | None] = mapped_column(String(32))
    fuel_load: Mapped[float | None] = mapped_column(Float)
    pace_mode: Mapped[str | None] = mapped_column(String(16))
    expected_lap_time: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)

    strategy = relationship("Strategy", back_populates="steps")

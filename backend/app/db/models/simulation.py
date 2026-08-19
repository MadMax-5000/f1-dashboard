import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Enum, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class SimulationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SimulationType(str, enum.Enum):
    REPLAY = "replay"
    COUNTERFACTUAL = "counterfactual"
    MONTE_CARLO = "monte_carlo"
    STRATEGY_OPTIMISATION = "strategy_optimisation"
    RL_TRAINING = "rl_training"


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    type: Mapped[SimulationType] = mapped_column(Enum(SimulationType), nullable=False)
    status: Mapped[SimulationStatus] = mapped_column(
        Enum(SimulationStatus), default=SimulationStatus.PENDING
    )
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text)
    parameters: Mapped[dict | None] = mapped_column(nullable=True)
    start_time: Mapped[datetime | None] = mapped_column()
    end_time: Mapped[datetime | None] = mapped_column()
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    total_ticks: Mapped[int | None] = mapped_column(Integer)
    ray_job_id: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
    config: Mapped[dict | None] = mapped_column(nullable=True)

    session = relationship("Session")
    results = relationship(
        "SimulationResult", back_populates="simulation_run", cascade="all, delete-orphan"
    )
    counterfactuals = relationship(
        "Counterfactual", back_populates="simulation_run", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_sim_session", "session_id"),
        Index("idx_sim_status", "status"),
    )


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulation_runs.id"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    tick: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time: Mapped[float | None] = mapped_column(Float)
    sector_1: Mapped[float | None] = mapped_column(Float)
    sector_2: Mapped[float | None] = mapped_column(Float)
    sector_3: Mapped[float | None] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float)
    distance: Mapped[float | None] = mapped_column(Float)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)
    data: Mapped[dict | None] = mapped_column(nullable=True)

    simulation_run = relationship("SimulationRun", back_populates="results")
    driver = relationship("Driver")

    __table_args__ = (
        Index("idx_sr_run", "simulation_run_id"),
        Index("idx_sr_run_tick", "simulation_run_id", "tick"),
    )


class Counterfactual(Base):
    __tablename__ = "counterfactuals"

    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulation_runs.id"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    scenario_name: Mapped[str] = mapped_column(String(256), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(64), nullable=False)
    intervention: Mapped[dict] = mapped_column(nullable=False)
    original_position: Mapped[int | None] = mapped_column(Integer)
    counterfactual_position: Mapped[int | None] = mapped_column(Integer)
    original_time: Mapped[float | None] = mapped_column(Float)
    counterfactual_time: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float)
    probability_distribution: Mapped[dict | None] = mapped_column(nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text)

    simulation_run = relationship("SimulationRun", back_populates="counterfactuals")
    driver = relationship("Driver")

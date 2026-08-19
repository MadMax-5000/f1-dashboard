import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    prediction_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    features_snapshot: Mapped[dict | None] = mapped_column(nullable=True)
    prediction_value: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_lower: Mapped[float | None] = mapped_column(Float)
    prediction_upper: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float)
    feature_importance: Mapped[dict | None] = mapped_column(nullable=True)
    shap_values: Mapped[dict | None] = mapped_column(nullable=True)
    ground_truth: Mapped[float | None] = mapped_column(Float)
    is_correct: Mapped[bool | None] = mapped_column()

    session = relationship("Session")

    __table_args__ = (
        Index("idx_pred_session_type", "session_id", "prediction_type"),
        Index("idx_pred_model", "model_name", "model_version"),
    )


class DriverPrediction(Base):
    __tablename__ = "driver_predictions"

    prediction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("predictions.id"), nullable=False)
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_lap_time: Mapped[float | None] = mapped_column(Float)
    predicted_position: Mapped[int | None] = mapped_column(Integer)
    predicted_tyre_age: Mapped[int | None] = mapped_column(Integer)
    predicted_fuel_load: Mapped[float | None] = mapped_column(Float)

    prediction = relationship("Prediction")
    driver = relationship("Driver")

    __table_args__ = (
        Index("idx_dp_prediction", "prediction_id"),
        Index("idx_dp_driver_lap", "driver_id", "lap_number"),
    )

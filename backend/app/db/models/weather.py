import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    air_temperature_c: Mapped[float | None] = mapped_column(Float)
    track_temperature_c: Mapped[float | None] = mapped_column(Float)
    humidity_pct: Mapped[float | None] = mapped_column(Float)
    pressure_mb: Mapped[float | None] = mapped_column(Float)
    wind_speed_ms: Mapped[float | None] = mapped_column(Float)
    wind_direction_deg: Mapped[float | None] = mapped_column(Float)
    rainfall: Mapped[bool | None] = mapped_column(default=False)
    rain_intensity: Mapped[float | None] = mapped_column(Float)
    track_grip: Mapped[float | None] = mapped_column(Float)
    cloud_cover_pct: Mapped[float | None] = mapped_column(Float)

    session = relationship("Session")

    __table_args__ = (Index("idx_weather_session_ts", "session_id", "timestamp"),)

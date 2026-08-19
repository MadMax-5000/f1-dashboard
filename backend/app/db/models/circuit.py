import uuid
from sqlalchemy import String, Float, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Circuit(Base):
    __tablename__ = "circuits"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    circuit_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    location: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(64))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    altitude: Mapped[float | None] = mapped_column(Float)
    length_km: Mapped[float | None] = mapped_column(Float)
    turns: Mapped[int | None] = mapped_column(Integer)
    drs_zones_count: Mapped[int | None] = mapped_column(Integer, default=2)
    track_map_url: Mapped[str | None] = mapped_column(String(512))

    corners = relationship("Corner", back_populates="circuit", cascade="all, delete-orphan")
    sectors = relationship("Sector", back_populates="circuit", cascade="all, delete-orphan")
    drs_zones = relationship("DRSZone", back_populates="circuit", cascade="all, delete-orphan")
    races = relationship("Race", back_populates="circuit")


class Corner(Base):
    __tablename__ = "corners"

    circuit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("circuits.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(64))
    type: Mapped[str | None] = mapped_column(String(32))
    apex_latitude: Mapped[float | None] = mapped_column(Float)
    apex_longitude: Mapped[float | None] = mapped_column(Float)
    entry_speed_kmh: Mapped[float | None] = mapped_column(Float)
    exit_speed_kmh: Mapped[float | None] = mapped_column(Float)
    braking_distance_m: Mapped[float | None] = mapped_column(Float)
    gforce: Mapped[float | None] = mapped_column(Float)

    circuit = relationship("Circuit", back_populates="corners")

    __table_args__ = (Index("idx_corner_circuit_number", "circuit_id", "number", unique=True),)


class Sector(Base):
    __tablename__ = "sectors"

    circuit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("circuits.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_point: Mapped[float] = mapped_column(Float)
    end_point: Mapped[float] = mapped_column(Float)
    length_km: Mapped[float | None] = mapped_column(Float)

    circuit = relationship("Circuit", back_populates="sectors")

    __table_args__ = (Index("idx_sector_circuit_number", "circuit_id", "number", unique=True),)


class DRSZone(Base):
    __tablename__ = "drs_zones"

    circuit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("circuits.id"), nullable=False)
    zone_number: Mapped[int] = mapped_column(Integer, nullable=False)
    detection_point: Mapped[float] = mapped_column(Float)
    activation_point: Mapped[float] = mapped_column(Float)
    length_m: Mapped[float | None] = mapped_column(Float)

    circuit = relationship("Circuit", back_populates="drs_zones")

    __table_args__ = (Index("idx_drs_circuit_zone", "circuit_id", "zone_number", unique=True),)

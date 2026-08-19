from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import numpy as np


@dataclass
class DriverState:
    driver_id: str
    driver_number: int
    position: int
    lap_number: int
    distance: float
    speed: float
    rpm: float
    gear: int
    throttle: float
    brake: float
    drs_active: bool
    x: float
    y: float
    z: float

    tyre_compound: str
    tyre_age_laps: int
    tyre_temperature: float

    fuel_remaining: float
    fuel_load: float

    ers_energy: float
    ers_deploy_mode: str

    sector: int
    in_pit: bool
    pit_stop_count: int
    lap_time_accumulator: float
    sector_times: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    delta_to_leader: float = 0.0
    delta_to_next: float = 0.0
    delta_to_prev: float = 0.0

    is_retired: bool = False
    in_safety_car_period: bool = False
    has_drs_available: bool = False
    drs_detection_beam: bool = False


@dataclass
class RaceState:
    session_id: str
    tick: int
    timestamp: datetime
    lap_number: int
    total_laps: int
    race_phase: str

    drivers: dict[str, DriverState] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)

    safety_car_active: bool = False
    safety_car_type: str | None = None
    vsc_active: bool = False
    red_flag: bool = False

    air_temperature: float = 25.0
    track_temperature: float = 30.0
    rainfall: bool = False
    rain_intensity: float = 0.0
    wind_speed: float = 0.0
    track_grip: float = 1.0

    events: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_driver(self, driver_id: str) -> DriverState | None:
        return self.drivers.get(driver_id)

    def driver_positions(self) -> list[tuple[str, int, float]]:
        return [
            (d.driver_id, d.position, d.distance)
            for d in sorted(self.drivers.values(), key=lambda x: x.position)
        ]

    def gap_matrix(self) -> np.ndarray:
        n = len(self.order)
        matrix = np.zeros((n, n))
        for i, d_id in enumerate(self.order):
            if d_id in self.drivers:
                for j, o_id in enumerate(self.order):
                    if o_id in self.drivers:
                        matrix[i, j] = (
                            self.drivers[d_id].delta_to_leader - self.drivers[o_id].delta_to_leader
                        )
        return matrix

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "tick": self.tick,
            "lap_number": self.lap_number,
            "phase": self.race_phase,
            "order": self.order,
            "drivers": {
                did: {
                    "position": ds.position,
                    "lap": ds.lap_number,
                    "speed": ds.speed,
                    "x": ds.x,
                    "y": ds.y,
                    "tyre": ds.tyre_compound,
                    "tyre_age": ds.tyre_age_laps,
                    "fuel": ds.fuel_remaining,
                    "delta_leader": ds.delta_to_leader,
                }
                for did, ds in self.drivers.items()
            },
            "safety_car": self.safety_car_active,
            "weather": {
                "air_temp": self.air_temperature,
                "track_temp": self.track_temperature,
                "rainfall": self.rainfall,
            },
        }

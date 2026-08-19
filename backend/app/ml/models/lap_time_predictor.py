import numpy as np
import pandas as pd
import structlog
from typing import Any
from dataclasses import dataclass

logger = structlog.get_logger()


@dataclass
class LapTimeFeatures:
    driver_id: str
    circuit_id: str
    lap_number: int
    position: int
    tyre_compound: str
    tyre_age: int
    fuel_load: float
    track_temperature: float
    air_temperature: float
    rainfall: bool
    wind_speed: float
    sector_1_prev: float
    sector_2_prev: float
    sector_3_prev: float
    avg_speed_prev_lap: float
    drs_available: bool
    is_out_lap: bool
    is_in_lap: bool
    safety_car_active: bool
    stint_lap_count: int
    track_grip: float


class LapTimePredictor:
    def __init__(self):
        self._model = None
        self._is_trained = False
        self._feature_names = [
            "lap_number",
            "position",
            "tyre_age",
            "fuel_load",
            "track_temperature",
            "air_temperature",
            "wind_speed",
            "sector_1_prev",
            "sector_2_prev",
            "sector_3_prev",
            "avg_speed_prev_lap",
            "stint_lap_count",
            "track_grip",
            "is_rainfall",
            "is_drs",
            "is_out_lap",
            "is_in_lap",
            "is_safety_car",
        ]

    def _encode_features(self, features: LapTimeFeatures) -> np.ndarray:
        compound_map = {"soft": 0, "medium": 1, "hard": 2, "intermediate": 3, "wet": 4}
        row = [
            features.lap_number,
            features.position,
            features.tyre_age,
            features.fuel_load,
            features.track_temperature,
            features.air_temperature,
            features.wind_speed,
            features.sector_1_prev,
            features.sector_2_prev,
            features.sector_3_prev,
            features.avg_speed_prev_lap,
            features.stint_lap_count,
            features.track_grip,
            float(features.rainfall),
            float(features.drs_available),
            float(features.is_out_lap),
            float(features.is_in_lap),
            float(features.safety_car_active),
        ]
        compound_feat = [0.0] * 5
        compound_idx = compound_map.get(features.tyre_compound, 0)
        compound_feat[compound_idx] = 1.0
        return np.array(row + compound_feat, dtype=np.float32)

    def predict(self, features: LapTimeFeatures) -> dict[str, float]:
        x = self._encode_features(features).reshape(1, -1)
        base_lap_time = 90.0
        adjustments = {
            "tyre_age": features.tyre_age * 0.05,
            "fuel_load": (features.fuel_load - 50.0) * 0.01,
            "track_temp": max(0, features.track_temperature - 30.0) * 0.02,
            "rainfall": 3.0 if features.rainfall else 0.0,
            "safety_car": 5.0 if features.safety_car_active else 0.0,
            "out_lap": 2.0 if features.is_out_lap else 0.0,
            "in_lap": 1.5 if features.is_in_lap else 0.0,
            "stint_age": max(0, features.stint_lap_count - 15) * 0.1,
        }
        predicted = base_lap_time + sum(adjustments.values())
        return {
            "predicted_lap_time": round(predicted, 3),
            "base_lap_time": base_lap_time,
            "adjustments": adjustments,
            "confidence": 0.85,
            "uncertainty": 0.5 + len(adjustments) * 0.1,
        }

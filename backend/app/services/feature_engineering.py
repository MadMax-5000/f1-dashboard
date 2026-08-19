import numpy as np
import pandas as pd
from typing import Any
from dataclasses import dataclass, field


@dataclass
class DriverFeatures:
    driver_id: str
    lap_number: int
    position: int

    lap_time: float = 0.0
    sector_1: float = 0.0
    sector_2: float = 0.0
    sector_3: float = 0.0

    speed_trap: float = 0.0
    avg_speed: float = 0.0
    top_speed: float = 0.0
    min_speed_corner: float = 0.0

    throttle_pct: float = 0.0
    brake_pct: float = 0.0
    avg_rpm: float = 0.0
    avg_gear: float = 0.0

    tyre_compound: str = "unknown"
    tyre_age_laps: int = 0
    tyre_degradation_index: float = 0.0

    fuel_load: float = 0.0
    fuel_consumption_rate: float = 0.0

    drs_usage_pct: float = 0.0
    ers_deployment: float = 0.0

    delta_to_leader: float = 0.0
    delta_to_next: float = 0.0
    delta_to_prev: float = 0.0
    gap_to_leader: float = 0.0

    in_traffic: bool = False
    dirty_air_estimate: float = 0.0
    slipstream_benefit: float = 0.0

    overtakes_attempted: int = 0
    overtakes_completed: int = 0
    times_overtaken: int = 0
    defensive_actions: int = 0

    track_grip: float = 1.0
    track_evolution_lap: float = 0.0
    rain_intensity: float = 0.0

    is_pit_lap: bool = False
    is_out_lap: bool = False
    is_in_lap: bool = False
    pits_so_far: int = 0

    consistency_score: float = 1.0
    aggression_score: float = 0.5
    pressure_index: float = 0.0
    performance_index: float = 0.0


class FeatureComputer:
    @staticmethod
    def compute_lap_features(
        telemetry_df: pd.DataFrame,
        laps_df: pd.DataFrame,
        driver_id: str,
    ) -> pd.DataFrame:
        if telemetry_df.empty:
            return pd.DataFrame()

        features = telemetry_df.copy()
        features["speed_smooth"] = features["speed"].rolling(5, center=True).mean()
        features["acceleration"] = (
            features["speed"].diff() / features["time"].diff().dt.total_seconds()
        )
        features["jerk"] = (
            features["acceleration"].diff() / features["time"].diff().dt.total_seconds()
        )
        features["throttle_brake_overlap"] = (
            (features["throttle"] > 0.1) & (features["brake"] > 0.1)
        ).astype(float)

        return features

    @staticmethod
    def compute_corner_features(telemetry_df: pd.DataFrame) -> dict[str, float]:
        if telemetry_df.empty:
            return {}

        braking_events = FeatureComputer._detect_braking_events(telemetry_df)
        cornering_events = FeatureComputer._detect_cornering(telemetry_df)

        return {
            "braking_events": len(braking_events),
            "avg_braking_distance": np.mean([b["distance"] for b in braking_events])
            if braking_events
            else 0.0,
            "min_corner_speed": min([c["min_speed"] for c in cornering_events])
            if cornering_events
            else 0.0,
            "avg_corner_exit_speed": np.mean([c["exit_speed"] for c in cornering_events])
            if cornering_events
            else 0.0,
        }

    @staticmethod
    def _detect_braking_events(df: pd.DataFrame) -> list[dict]:
        events = []
        braking = False
        start_idx = None
        for i in range(len(df)):
            is_braking = df.iloc[i].get("brake", 0) > 0.1
            if is_braking and not braking:
                braking = True
                start_idx = i
            elif not is_braking and braking:
                events.append(
                    {
                        "start": start_idx,
                        "end": i,
                        "distance": df.iloc[i].get("distance", 0)
                        - df.iloc[start_idx].get("distance", 0),
                    }
                )
                braking = False
        return events

    @staticmethod
    def _detect_cornering(df: pd.DataFrame) -> list[dict]:
        events = []
        cornering = False
        start_idx = None
        min_speed = float("inf")
        for i in range(len(df)):
            speed = df.iloc[i].get("speed", 0)
            is_cornering = speed < 200 and (
                df.iloc[i].get("throttle", 1) < 0.8 or df.iloc[i].get("brake", 0) > 0.05
            )
            if is_cornering and not cornering:
                cornering = True
                start_idx = i
                min_speed = speed
            elif cornering:
                min_speed = min(min_speed, speed)
                if not is_cornering:
                    events.append(
                        {
                            "start": start_idx,
                            "end": i,
                            "min_speed": min_speed,
                            "exit_speed": speed,
                        }
                    )
                    cornering = False
                    min_speed = float("inf")
        return events

    @staticmethod
    def compute_driver_metrics(
        laps: pd.DataFrame,
    ) -> dict[str, float]:
        if laps.empty:
            return {}

        valid = laps[laps["is_valid"] == True] if "is_valid" in laps.columns else laps
        lap_times = valid["time_seconds"].dropna()

        if len(lap_times) < 3:
            return {"consistency": 1.0, "avg_lap_time": 0.0}

        return {
            "consistency": float(1.0 - (lap_times.std() / lap_times.mean())),
            "avg_lap_time": float(lap_times.mean()),
            "best_lap_time": float(lap_times.min()),
            "median_lap_time": float(lap_times.median()),
            "lap_time_std": float(lap_times.std()),
            "total_laps": len(valid),
            "improvement_rate": float(
                lap_times.iloc[: min(10, len(lap_times))].mean()
                - lap_times.iloc[-min(10, len(lap_times)) :].mean()
            ),
        }

    @staticmethod
    def compute_tyre_degradation(
        lap_times: list[float],
        tyre_age: list[int],
    ) -> dict[str, float]:
        if len(lap_times) < 3:
            return {"degradation_rate": 0.0, "degradation_curve": []}

        coeffs = np.polyfit(tyre_age, lap_times, 2)
        degradation_rate = coeffs[1] if len(coeffs) > 1 else 0.0
        return {
            "degradation_rate": float(degradation_rate),
            "degradation_quadratic": float(coeffs[0]) if len(coeffs) > 2 else 0.0,
            "degradation_intercept": float(coeffs[-1]),
        }

    @staticmethod
    def compute_overtake_risk(
        leader_time: float,
        follower_time: float,
        drs_available: bool,
        straight_length: float,
    ) -> float:
        time_gap = follower_time - leader_time
        if time_gap <= 0:
            return 0.0
        speed_advantage = (leader_time - follower_time) / leader_time
        drs_bonus = 0.15 if drs_available else 0.0
        risk = max(0.0, min(1.0, (speed_advantage + drs_bonus) * 5.0))
        return risk

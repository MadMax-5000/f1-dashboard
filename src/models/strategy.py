"""Race strategy prediction - pit stop windows and compound selection."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
import joblib
import structlog

logger = structlog.get_logger()

MODEL_DIR = Path(__file__).parent.parent.parent / "data" / "models"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


class StrategyModel:
    """Predict number of pit stops and compound choices per race."""

    def __init__(self):
        self.stops_model: lgb.LGBMClassifier | None = None
        self.compound_model: lgb.LGBMClassifier | None = None
        self.metrics: dict = {}

    def prepare_strategy_data(self, results: pd.DataFrame, laps_df: pd.DataFrame | None = None):
        """Build strategy features from race/lap data."""
        # For now, use race-level features to predict number of stops
        # In production, lap data would be used for more granular predictions
        features = results[["year", "round", "driver_id", "circuit_id", "grid", "laps"]].copy()

        # Circuit historical avg stops (approximated from laps completed)
        circuit_avg_laps = results.groupby("circuit_id")["laps"].mean()
        features["circuit_avg_laps"] = features["circuit_id"].map(circuit_avg_laps)

        return features

    def predict_strategy(
        self,
        circuit_id: str,
        total_laps: int,
        grid_position: int,
    ) -> dict:
        """Predict likely race strategy for given conditions."""
        # Heuristic-based strategy prediction based on circuit characteristics
        # and historical patterns until we have enough lap-level training data

        if total_laps > 55:
            likely_stops = 2
            strategies = [
                {"stops": 2, "probability": 0.65, "compounds": ["MEDIUM", "HARD", "MEDIUM"]},
                {"stops": 1, "probability": 0.25, "compounds": ["MEDIUM", "HARD"]},
                {"stops": 3, "probability": 0.10, "compounds": ["SOFT", "MEDIUM", "HARD", "SOFT"]},
            ]
        else:
            likely_stops = 1
            strategies = [
                {"stops": 1, "probability": 0.70, "compounds": ["SOFT", "HARD"]},
                {"stops": 2, "probability": 0.25, "compounds": ["SOFT", "MEDIUM", "SOFT"]},
                {"stops": 1, "probability": 0.05, "compounds": ["MEDIUM", "HARD"]},
            ]

        # Adjust for grid position - front runners may have different strategy
        if grid_position <= 3:
            strategies[0]["probability"] += 0.05
            strategies[-1]["probability"] -= 0.05

        pit_window_start = int(total_laps * 0.3)
        pit_window_end = int(total_laps * 0.55)

        return {
            "likely_stops": likely_stops,
            "strategies": strategies,
            "optimal_pit_window": {"start_lap": pit_window_start, "end_lap": pit_window_end},
        }

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.metrics, MODEL_DIR / "strategy_metrics.joblib")

    def load(self):
        self.metrics = joblib.load(MODEL_DIR / "strategy_metrics.joblib")

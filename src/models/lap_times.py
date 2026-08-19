"""Lap time prediction model using gradient boosting."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import structlog

logger = structlog.get_logger()

MODEL_DIR = Path(__file__).parent.parent.parent / "data" / "models"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

FEATURE_COLS = [
    "tyre_life",
    "stint_number",
    "lap_in_stint",
    "fuel_corrected_lap",
    "compound_encoded",
    "position",
    "driver_avg_pace",
    "track_evolution",
]


class LapTimeModel:
    def __init__(self):
        self.model: xgb.XGBRegressor | None = None
        self.metrics: dict = {}

    def prepare_lap_data(self, laps_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare lap-level data with engineered features."""
        df = laps_df.copy()

        compound_map = {"SOFT": 0, "MEDIUM": 1, "HARD": 2, "INTERMEDIATE": 3, "WET": 4}
        df["compound_encoded"] = df["Compound"].map(compound_map).fillna(1)

        df["lap_in_stint"] = df.groupby(["Driver", "Stint"]).cumcount() + 1
        df["tyre_life"] = df["TyreLife"]
        df["stint_number"] = df["Stint"]
        df["position"] = df["Position"]

        total_laps = df["LapNumber"].max()
        df["fuel_corrected_lap"] = df["LapNumber"] / total_laps

        df["driver_avg_pace"] = df.groupby("Driver")["LapTime_seconds"].transform(
            lambda x: x.expanding().mean().shift(1)
        )
        df["track_evolution"] = df["LapNumber"] / total_laps

        df = df.dropna(subset=["LapTime_seconds"])
        df = df[df["LapTime_seconds"] > 0]
        # Remove outliers (pit laps, safety car laps)
        median = df["LapTime_seconds"].median()
        df = df[df["LapTime_seconds"] < median * 1.3]

        return df

    def train(self, laps_df: pd.DataFrame):
        df = self.prepare_lap_data(laps_df)

        available_cols = [c for c in FEATURE_COLS if c in df.columns]
        X = df[available_cols].fillna(0)
        y = df["LapTime_seconds"]

        tscv = TimeSeriesSplit(n_splits=3)
        train_idx, test_idx = list(tscv.split(X))[-1]

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42,
        )
        self.model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        preds = self.model.predict(X_test)
        self.metrics = {
            "mae": float(mean_absolute_error(y_test, preds)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
            "r2": float(r2_score(y_test, preds)),
            "test_size": len(X_test),
        }
        logger.info("lap_time model trained", **self.metrics)

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        available_cols = [c for c in FEATURE_COLS if c in features.columns]
        X = features[available_cols].fillna(0)
        return self.model.predict(X)

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, MODEL_DIR / "lap_times.joblib")
        joblib.dump(self.metrics, MODEL_DIR / "lap_times_metrics.joblib")

    def load(self):
        self.model = joblib.load(MODEL_DIR / "lap_times.joblib")
        self.metrics = joblib.load(MODEL_DIR / "lap_times_metrics.joblib")

"""Qualifying position prediction model."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
import lightgbm as lgb
import joblib
import structlog

logger = structlog.get_logger()

MODEL_DIR = Path(__file__).parent.parent.parent / "data" / "models"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

FEATURE_COLS = [
    "rolling_finish_position_filled_5",
    "rolling_points_5",
    "career_races",
    "career_points",
    "rolling_avg_position_5",
    "rolling_total_points_5",
    "h2h_rolling_5",
    "pole_win_rate",
]


class QualifyingModel:
    def __init__(self):
        self.model: lgb.LGBMRegressor | None = None
        self.metrics: dict = {}

    def train(self, df: pd.DataFrame | None = None):
        if df is None:
            df = pd.read_parquet(PROCESSED_DIR / "features.parquet")

        df = df.dropna(subset=["quali_position"])
        X = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
        y = df["quali_position"]

        tscv = TimeSeriesSplit(n_splits=5)
        train_idx, test_idx = list(tscv.split(X))[-1]

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        self.model = lgb.LGBMRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1,
        )
        self.model.fit(X_train, y_train, eval_set=[(X_test, y_test)])

        preds = self.model.predict(X_test)
        self.metrics = {
            "mae": float(mean_absolute_error(y_test, preds)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
            "test_size": len(X_test),
        }
        logger.info("qualifying model trained", **self.metrics)

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        X = features[FEATURE_COLS].fillna(features[FEATURE_COLS].median())
        results = features[["driver_id"]].copy()
        results["predicted_quali_position"] = self.model.predict(X)
        return results.sort_values("predicted_quali_position")

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, MODEL_DIR / "qualifying.joblib")
        joblib.dump(self.metrics, MODEL_DIR / "qualifying_metrics.joblib")

    def load(self):
        self.model = joblib.load(MODEL_DIR / "qualifying.joblib")
        self.metrics = joblib.load(MODEL_DIR / "qualifying_metrics.joblib")


if __name__ == "__main__":
    model = QualifyingModel()
    model.train()
    model.save()
    print(f"Metrics: {model.metrics}")

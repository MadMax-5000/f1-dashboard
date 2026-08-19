"""Race winner / podium prediction model using XGBoost."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, log_loss, top_k_accuracy_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import structlog

logger = structlog.get_logger()

MODEL_DIR = Path(__file__).parent.parent.parent / "data" / "models"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

FEATURE_COLS = [
    "grid",
    "rolling_finish_position_filled_5",
    "rolling_points_5",
    "rolling_is_podium_5",
    "rolling_is_points_5",
    "rolling_is_dnf_5",
    "career_races",
    "career_points",
    "rolling_avg_position_5",
    "rolling_total_points_5",
    "quali_gap_pct",
    "h2h_rolling_5",
    "avg_grid_winner",
    "pole_win_rate",
    "avg_finishers",
]


class RaceWinnerModel:
    def __init__(self):
        self.win_model: xgb.XGBClassifier | None = None
        self.podium_model: xgb.XGBClassifier | None = None
        self.metrics: dict = {}

    def _prepare_data(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
        features = df[FEATURE_COLS].copy()
        features = features.fillna(features.median())
        return features, df["target_win"], df["target_podium"]

    def train(self, df: pd.DataFrame | None = None):
        if df is None:
            df = pd.read_parquet(PROCESSED_DIR / "features.parquet")

        df = df.dropna(subset=["position"])
        X, y_win, y_podium = self._prepare_data(df)

        tscv = TimeSeriesSplit(n_splits=5)
        train_idx, test_idx = list(tscv.split(X))[-1]

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_win_train, y_win_test = y_win.iloc[train_idx], y_win.iloc[test_idx]
        y_pod_train, y_pod_test = y_podium.iloc[train_idx], y_podium.iloc[test_idx]

        self.win_model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=len(y_win_train) / max(y_win_train.sum(), 1),
            eval_metric="logloss",
            random_state=42,
        )
        self.win_model.fit(X_train, y_win_train, eval_set=[(X_test, y_win_test)], verbose=False)

        self.podium_model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=len(y_pod_train) / max(y_pod_train.sum(), 1),
            eval_metric="logloss",
            random_state=42,
        )
        self.podium_model.fit(
            X_train, y_pod_train, eval_set=[(X_test, y_pod_test)], verbose=False
        )

        win_probs = self.win_model.predict_proba(X_test)[:, 1]
        pod_probs = self.podium_model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "win_log_loss": float(log_loss(y_win_test, win_probs)),
            "win_accuracy": float(accuracy_score(y_win_test, (win_probs > 0.5).astype(int))),
            "podium_log_loss": float(log_loss(y_pod_test, pod_probs)),
            "podium_accuracy": float(accuracy_score(y_pod_test, (pod_probs > 0.5).astype(int))),
            "test_size": len(X_test),
        }
        logger.info("race_winner model trained", **self.metrics)

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        X = features[FEATURE_COLS].copy().fillna(features[FEATURE_COLS].median())
        results = features[["driver_id"]].copy()
        results["win_probability"] = self.win_model.predict_proba(X)[:, 1]
        results["podium_probability"] = self.podium_model.predict_proba(X)[:, 1]
        return results.sort_values("win_probability", ascending=False)

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.win_model, MODEL_DIR / "race_winner_win.joblib")
        joblib.dump(self.podium_model, MODEL_DIR / "race_winner_podium.joblib")
        joblib.dump(self.metrics, MODEL_DIR / "race_winner_metrics.joblib")

    def load(self):
        self.win_model = joblib.load(MODEL_DIR / "race_winner_win.joblib")
        self.podium_model = joblib.load(MODEL_DIR / "race_winner_podium.joblib")
        self.metrics = joblib.load(MODEL_DIR / "race_winner_metrics.joblib")


if __name__ == "__main__":
    model = RaceWinnerModel()
    model.train()
    model.save()
    print(f"Metrics: {model.metrics}")

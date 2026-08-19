"""Unified prediction interface that loads models and generates predictions."""

import pandas as pd
from pathlib import Path
import structlog

from src.models.race_winner import RaceWinnerModel
from src.models.qualifying import QualifyingModel
from src.models.championship import ChampionshipModel
from src.models.strategy import StrategyModel

logger = structlog.get_logger()

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


class F1Predictor:
    """Facade for all F1 prediction models."""

    def __init__(self):
        self.race_winner = RaceWinnerModel()
        self.qualifying = QualifyingModel()
        self.championship = ChampionshipModel()
        self.strategy = StrategyModel()
        self._loaded = False

    def load_models(self):
        try:
            self.race_winner.load()
            self.qualifying.load()
            self._loaded = True
            logger.info("models loaded successfully")
        except Exception as e:
            logger.warning("some models failed to load", error=str(e))

    def predict_next_race(self, race_features: pd.DataFrame) -> dict:
        """Predict winner/podium probabilities for an upcoming race."""
        if not self._loaded:
            self.load_models()

        winner_preds = self.race_winner.predict(race_features)
        quali_preds = self.qualifying.predict(race_features)

        return {
            "race_winner": winner_preds.to_dict(orient="records"),
            "qualifying": quali_preds.to_dict(orient="records"),
        }

    def predict_championship(
        self,
        current_standings: dict[str, float],
        remaining_races: int,
        win_probabilities: dict[str, float],
    ) -> dict:
        """Run championship Monte Carlo simulation."""
        results = self.championship.simulate_season(
            current_standings, remaining_races, win_probabilities
        )
        return {
            "probabilities": self.championship.get_probabilities().to_dict(orient="records"),
            "simulations": self.championship.n_simulations,
        }

    def predict_strategy(
        self, circuit_id: str, total_laps: int, grid_position: int
    ) -> dict:
        return self.strategy.predict_strategy(circuit_id, total_laps, grid_position)

    def get_model_metrics(self) -> dict:
        return {
            "race_winner": self.race_winner.metrics,
            "qualifying": self.qualifying.metrics,
        }

"""Championship outcome prediction via Monte Carlo simulation."""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import structlog

logger = structlog.get_logger()

MODEL_DIR = Path(__file__).parent.parent.parent / "data" / "models"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

POINTS_SYSTEM = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


class ChampionshipModel:
    """Monte Carlo simulation of remaining season using race-win probabilities."""

    def __init__(self, n_simulations: int = 10000):
        self.n_simulations = n_simulations
        self.results: dict = {}

    def simulate_season(
        self,
        current_standings: dict[str, float],
        remaining_races: int,
        win_probabilities: dict[str, float],
    ) -> dict[str, dict]:
        """
        Simulate remaining races and compute championship probabilities.

        Args:
            current_standings: {driver_id: current_points}
            remaining_races: number of races left
            win_probabilities: {driver_id: base_win_probability}
        """
        drivers = list(current_standings.keys())
        n_drivers = len(drivers)

        # Normalize win probs
        probs = np.array([win_probabilities.get(d, 0.01) for d in drivers])
        probs = probs / probs.sum()

        championship_wins = {d: 0 for d in drivers}
        final_points_all = {d: [] for d in drivers}

        for _ in range(self.n_simulations):
            sim_points = dict(current_standings)

            for _ in range(remaining_races):
                # Sample finishing positions using Dirichlet-weighted random
                noise = np.random.dirichlet(np.ones(n_drivers) * 2)
                adjusted = probs * 0.7 + noise * 0.3
                positions = np.argsort(-adjusted) + 1

                for driver_idx, pos in enumerate(positions):
                    pts = POINTS_SYSTEM.get(int(pos), 0)
                    sim_points[drivers[driver_idx]] += pts

            winner = max(sim_points, key=sim_points.get)
            championship_wins[winner] += 1

            for d in drivers:
                final_points_all[d].append(sim_points[d])

        self.results = {}
        for d in drivers:
            self.results[d] = {
                "win_probability": championship_wins[d] / self.n_simulations,
                "expected_final_points": float(np.mean(final_points_all[d])),
                "points_std": float(np.std(final_points_all[d])),
                "current_points": current_standings[d],
            }

        return self.results

    def get_probabilities(self) -> pd.DataFrame:
        if not self.results:
            return pd.DataFrame()
        df = pd.DataFrame(self.results).T
        df.index.name = "driver_id"
        return df.sort_values("win_probability", ascending=False).reset_index()

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.results, MODEL_DIR / "championship_results.joblib")

    def load(self):
        self.results = joblib.load(MODEL_DIR / "championship_results.joblib")


if __name__ == "__main__":
    # Example usage with dummy data
    standings = {"verstappen": 300, "norris": 250, "leclerc": 200, "hamilton": 180}
    win_probs = {"verstappen": 0.35, "norris": 0.25, "leclerc": 0.2, "hamilton": 0.1}

    model = ChampionshipModel(n_simulations=10000)
    results = model.simulate_season(standings, remaining_races=5, win_probabilities=win_probs)
    print(model.get_probabilities())

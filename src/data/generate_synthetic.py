"""Generate synthetic F1 data for development/training when API is unavailable."""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

DRIVERS = [
    ("verstappen", "red_bull"), ("perez", "red_bull"),
    ("norris", "mclaren"), ("piastri", "mclaren"),
    ("leclerc", "ferrari"), ("sainz", "ferrari"),
    ("hamilton", "mercedes"), ("russell", "mercedes"),
    ("alonso", "aston_martin"), ("stroll", "aston_martin"),
    ("gasly", "alpine"), ("ocon", "alpine"),
    ("tsunoda", "rb"), ("ricciardo", "rb"),
    ("bottas", "sauber"), ("zhou", "sauber"),
    ("magnussen", "haas"), ("hulkenberg", "haas"),
    ("albon", "williams"), ("sargeant", "williams"),
]

CIRCUITS = [
    "bahrain", "jeddah", "albert_park", "suzuka", "shanghai",
    "miami", "imola", "monaco", "catalunya", "montreal",
    "spielberg", "silverstone", "hungaroring", "spa",
    "zandvoort", "monza", "marina_bay", "interlagos",
    "las_vegas", "losail", "yas_marina",
]

# Base strength per constructor (higher = faster)
CONSTRUCTOR_STRENGTH = {
    "red_bull": 0.95, "mclaren": 0.88, "ferrari": 0.87,
    "mercedes": 0.84, "aston_martin": 0.72, "alpine": 0.65,
    "rb": 0.62, "haas": 0.58, "sauber": 0.55, "williams": 0.52,
}

DRIVER_SKILL = {
    "verstappen": 0.98, "norris": 0.90, "leclerc": 0.89,
    "hamilton": 0.91, "piastri": 0.85, "russell": 0.86,
    "sainz": 0.85, "alonso": 0.87, "perez": 0.78,
    "gasly": 0.75, "ocon": 0.73, "tsunoda": 0.72,
    "stroll": 0.68, "ricciardo": 0.74, "bottas": 0.72,
    "hulkenberg": 0.71, "magnussen": 0.69, "zhou": 0.65,
    "albon": 0.73, "sargeant": 0.60,
}


def generate_race_results(years: list[int]) -> pd.DataFrame:
    np.random.seed(42)
    rows = []

    for year in years:
        # Vary constructor strength slightly per year
        year_strength = {k: v + np.random.normal(0, 0.03) for k, v in CONSTRUCTOR_STRENGTH.items()}

        n_races = min(len(CIRCUITS), 22)
        for round_num in range(1, n_races + 1):
            circuit_id = CIRCUITS[(round_num - 1) % len(CIRCUITS)]

            # Compute race performance score for each driver
            scores = []
            for driver_id, constructor_id in DRIVERS:
                base = year_strength.get(constructor_id, 0.6) * 0.6
                skill = DRIVER_SKILL.get(driver_id, 0.7) * 0.4
                noise = np.random.normal(0, 0.08)
                scores.append((driver_id, constructor_id, base + skill + noise))

            # Sort by score descending = finishing order
            scores.sort(key=lambda x: x[2], reverse=True)

            # Determine qualifying (similar but with different noise)
            quali_scores = []
            for driver_id, constructor_id, _ in scores:
                base = year_strength.get(constructor_id, 0.6) * 0.6
                skill = DRIVER_SKILL.get(driver_id, 0.7) * 0.4
                noise = np.random.normal(0, 0.06)
                quali_scores.append((driver_id, base + skill + noise))
            quali_scores.sort(key=lambda x: x[1], reverse=True)
            quali_order = {d: i + 1 for i, (d, _) in enumerate(quali_scores)}

            for pos, (driver_id, constructor_id, _) in enumerate(scores, 1):
                # ~5% DNF chance
                dnf = np.random.random() < 0.05
                points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

                rows.append({
                    "year": year,
                    "round": round_num,
                    "circuit_id": circuit_id,
                    "driver_id": driver_id,
                    "constructor_id": constructor_id,
                    "grid": quali_order.get(driver_id, pos),
                    "position": None if dnf else pos,
                    "points": 0.0 if dnf else points_map.get(pos, 0.0),
                    "status": "Retired" if dnf else "Finished",
                    "laps": np.random.randint(40, 60) if dnf else np.random.randint(50, 72),
                })

    return pd.DataFrame(rows)


def generate_qualifying(results: pd.DataFrame) -> pd.DataFrame:
    np.random.seed(43)
    rows = []

    for (year, round_num), group in results.groupby(["year", "round"]):
        circuit_id = group.iloc[0]["circuit_id"]
        base_time = np.random.uniform(75, 100)  # base qualifying time in seconds

        for _, row in group.iterrows():
            driver_id = row["driver_id"]
            constructor_id = row["constructor_id"]
            grid = row["grid"]

            gap = (grid - 1) * np.random.uniform(0.15, 0.4)
            q1_time = base_time + gap + np.random.normal(0, 0.1)
            q2_time = q1_time - np.random.uniform(0.1, 0.3) if grid <= 15 else None
            q3_time = q1_time - np.random.uniform(0.2, 0.5) if grid <= 10 else None

            def fmt(t):
                if t is None:
                    return None
                mins = int(t // 60)
                secs = t % 60
                return f"{mins}:{secs:06.3f}"

            rows.append({
                "year": year,
                "round": round_num,
                "circuit_id": circuit_id,
                "driver_id": driver_id,
                "constructor_id": constructor_id,
                "quali_position": grid,
                "q1": fmt(q1_time),
                "q2": fmt(q2_time),
                "q3": fmt(q3_time),
            })

    return pd.DataFrame(rows)


def generate_standings(results: pd.DataFrame) -> pd.DataFrame:
    standings = (
        results.groupby(["year", "driver_id", "constructor_id"])
        .agg(points=("points", "sum"), wins=("position", lambda x: (x == 1).sum()))
        .reset_index()
        .sort_values(["year", "points"], ascending=[True, False])
    )

    rows = []
    for year, group in standings.groupby("year"):
        group = group.sort_values("points", ascending=False).reset_index(drop=True)
        for i, row in group.iterrows():
            rows.append({
                "year": year,
                "position": i + 1,
                "driver_id": row["driver_id"],
                "constructor_id": row["constructor_id"],
                "points": row["points"],
                "wins": row["wins"],
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic race results...")
    results = generate_race_results(list(range(2018, 2027)))
    results.to_parquet(RAW_DIR / "race_results.parquet", index=False)
    print(f"  -> {len(results)} rows")

    print("Generating synthetic qualifying...")
    qualifying = generate_qualifying(results)
    qualifying.to_parquet(RAW_DIR / "qualifying.parquet", index=False)
    print(f"  -> {len(qualifying)} rows")

    print("Generating synthetic standings...")
    standings = generate_standings(results)
    standings.to_parquet(RAW_DIR / "standings.parquet", index=False)
    print(f"  -> {len(standings)} rows")

    print("Done! Data saved to data/raw/")

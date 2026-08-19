"""Feature engineering pipeline for F1 prediction models."""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load raw parquet files."""
    results = pd.read_parquet(RAW_DIR / "race_results.parquet")
    qualifying = pd.read_parquet(RAW_DIR / "qualifying.parquet")
    standings = pd.read_parquet(RAW_DIR / "standings.parquet")
    return results, qualifying, standings


def parse_quali_time(time_str: str | None) -> float | None:
    """Convert qualifying time string (M:SS.mmm) to seconds."""
    if time_str is None or pd.isna(time_str):
        return None
    try:
        parts = time_str.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    except (ValueError, AttributeError):
        return None


def compute_driver_form(results: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Compute rolling driver form features."""
    results = results.sort_values(["driver_id", "year", "round"])

    grouped = results.groupby("driver_id")

    results["finish_position_filled"] = results["position"].fillna(20)
    results["is_podium"] = (results["position"] <= 3).astype(int)
    results["is_points"] = (results["position"] <= 10).astype(int)
    results["is_dnf"] = results["position"].isna().astype(int)

    for col in ["finish_position_filled", "points", "is_podium", "is_points", "is_dnf"]:
        results[f"rolling_{col}_{window}"] = (
            results.groupby("driver_id")[col]
            .transform(lambda x: x.rolling(window, min_periods=1).mean().shift(1))
        )

    results["career_races"] = results.groupby("driver_id").cumcount()
    results["career_points"] = (
        results.groupby("driver_id")["points"].cumsum().shift(1).fillna(0)
    )
    results["career_wins"] = (
        results.groupby("driver_id")["is_podium"]
        .apply(lambda x: (x.shift(1).fillna(0)).cumsum())
        .reset_index(level=0, drop=True)
    )

    return results


def compute_constructor_form(results: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Compute rolling constructor performance."""
    constructor_race = (
        results.groupby(["constructor_id", "year", "round"])
        .agg(
            avg_position=("finish_position_filled", "mean"),
            total_points=("points", "sum"),
            best_position=("finish_position_filled", "min"),
        )
        .reset_index()
        .sort_values(["constructor_id", "year", "round"])
    )

    constructor_race[f"rolling_avg_position_{window}"] = (
        constructor_race.groupby("constructor_id")["avg_position"]
        .transform(lambda x: x.rolling(window, min_periods=1).mean().shift(1))
    )
    constructor_race[f"rolling_total_points_{window}"] = (
        constructor_race.groupby("constructor_id")["total_points"]
        .transform(lambda x: x.rolling(window, min_periods=1).mean().shift(1))
    )

    return constructor_race


def compute_circuit_features(results: pd.DataFrame) -> pd.DataFrame:
    """Compute circuit-level aggregated features."""
    circuit_stats = (
        results.groupby("circuit_id")
        .agg(
            avg_grid_winner=("grid", lambda x: x[results.loc[x.index, "position"] == 1].mean()),
            pole_win_rate=("position", lambda x: (
                (results.loc[x.index, "grid"] == 1) & (results.loc[x.index, "position"] == 1)
            ).mean()),
            avg_finishers=("position", lambda x: x.notna().mean()),
        )
        .reset_index()
    )
    return circuit_stats


def compute_grid_features(results: pd.DataFrame, qualifying: pd.DataFrame) -> pd.DataFrame:
    """Merge qualifying data and compute grid-related features."""
    merged = results.merge(
        qualifying[["year", "round", "driver_id", "quali_position", "q1", "q2", "q3"]],
        on=["year", "round", "driver_id"],
        how="left",
    )

    for col in ["q1", "q2", "q3"]:
        merged[f"{col}_seconds"] = merged[col].apply(parse_quali_time)

    merged["best_quali_time"] = merged[["q1_seconds", "q2_seconds", "q3_seconds"]].min(axis=1)

    race_best = merged.groupby(["year", "round"])["best_quali_time"].transform("min")
    merged["quali_gap_to_pole"] = merged["best_quali_time"] - race_best
    merged["quali_gap_pct"] = merged["quali_gap_to_pole"] / race_best

    merged["grid_position_change"] = merged["grid"] - merged["position"].fillna(20)

    return merged


def compute_head_to_head(results: pd.DataFrame) -> pd.DataFrame:
    """Compute teammate head-to-head record."""
    team_races = results.groupby(["constructor_id", "year", "round"]).filter(
        lambda x: len(x) == 2
    )

    h2h_records = []
    for (constructor, year, rnd), group in team_races.groupby(["constructor_id", "year", "round"]):
        if len(group) != 2:
            continue
        drivers = group.sort_values("finish_position_filled")
        winner = drivers.iloc[0]["driver_id"]
        loser = drivers.iloc[1]["driver_id"]
        h2h_records.append({"year": year, "round": rnd, "driver_id": winner, "beat_teammate": 1})
        h2h_records.append({"year": year, "round": rnd, "driver_id": loser, "beat_teammate": 0})

    if not h2h_records:
        return pd.DataFrame()

    h2h_df = pd.DataFrame(h2h_records)
    h2h_df = h2h_df.sort_values(["driver_id", "year", "round"])
    h2h_df["h2h_rolling_5"] = (
        h2h_df.groupby("driver_id")["beat_teammate"]
        .transform(lambda x: x.rolling(5, min_periods=1).mean().shift(1))
    )
    return h2h_df[["year", "round", "driver_id", "h2h_rolling_5"]]


def build_features(save: bool = True) -> pd.DataFrame:
    """Build the full feature matrix for model training."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    results, qualifying, standings = load_raw_data()

    results = compute_driver_form(results)

    constructor_form = compute_constructor_form(results)

    merged = compute_grid_features(results, qualifying)

    merged = merged.merge(
        constructor_form[["constructor_id", "year", "round",
                          "rolling_avg_position_5", "rolling_total_points_5"]],
        on=["constructor_id", "year", "round"],
        how="left",
    )

    h2h = compute_head_to_head(results)
    if not h2h.empty:
        merged = merged.merge(h2h, on=["year", "round", "driver_id"], how="left")

    circuit_stats = compute_circuit_features(results)
    merged = merged.merge(circuit_stats, on="circuit_id", how="left")

    # Target variables
    merged["target_win"] = (merged["position"] == 1).astype(int)
    merged["target_podium"] = (merged["position"] <= 3).astype(int)
    merged["target_points"] = (merged["position"] <= 10).astype(int)
    merged["target_position"] = merged["position"]

    if save:
        merged.to_parquet(PROCESSED_DIR / "features.parquet", index=False)

    return merged


if __name__ == "__main__":
    df = build_features()
    print(f"Feature matrix: {df.shape}")
    print(f"Columns: {list(df.columns)}")

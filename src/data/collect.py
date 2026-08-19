"""Data collection from FastF1 and Ergast/Jolpica API."""

import fastf1
import pandas as pd
import httpx
import structlog
from pathlib import Path

logger = structlog.get_logger()

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "fastf1_cache"


def setup_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))


def collect_race_results(year: int) -> pd.DataFrame:
    """Collect all race results for a given year from Ergast API."""
    url = f"https://api.jolpi.ca/ergast/f1/{year}/results.json?limit=1000"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    races = data["MRData"]["RaceTable"]["Races"]
    rows = []
    for race in races:
        round_num = int(race["round"])
        circuit_id = race["Circuit"]["circuitId"]
        for result in race["Results"]:
            rows.append({
                "year": year,
                "round": round_num,
                "circuit_id": circuit_id,
                "driver_id": result["Driver"]["driverId"],
                "constructor_id": result["Constructor"]["constructorId"],
                "grid": int(result["grid"]),
                "position": int(result["position"]) if result["position"].isdigit() else None,
                "points": float(result["points"]),
                "status": result["status"],
                "laps": int(result["laps"]),
            })
    return pd.DataFrame(rows)


def collect_qualifying(year: int) -> pd.DataFrame:
    """Collect qualifying results for a given year."""
    url = f"https://api.jolpi.ca/ergast/f1/{year}/qualifying.json?limit=1000"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    races = data["MRData"]["RaceTable"]["Races"]
    rows = []
    for race in races:
        round_num = int(race["round"])
        circuit_id = race["Circuit"]["circuitId"]
        for result in race.get("QualifyingResults", []):
            rows.append({
                "year": year,
                "round": round_num,
                "circuit_id": circuit_id,
                "driver_id": result["Driver"]["driverId"],
                "constructor_id": result["Constructor"]["constructorId"],
                "quali_position": int(result["position"]),
                "q1": result.get("Q1", None),
                "q2": result.get("Q2", None),
                "q3": result.get("Q3", None),
            })
    return pd.DataFrame(rows)


def collect_standings(year: int) -> pd.DataFrame:
    """Collect final driver standings for a year."""
    url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
        return pd.DataFrame()

    rows = []
    for entry in standings[0]["DriverStandings"]:
        rows.append({
            "year": year,
            "position": int(entry["position"]),
            "driver_id": entry["Driver"]["driverId"],
            "constructor_id": entry["Constructors"][0]["constructorId"],
            "points": float(entry["points"]),
            "wins": int(entry["wins"]),
        })
    return pd.DataFrame(rows)


def collect_session_laps(year: int, gp: str | int, session_type: str = "R") -> pd.DataFrame:
    """Collect lap-level data from FastF1 for a specific session."""
    setup_cache()
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load(laps=True, weather=True, telemetry=False)
    except Exception as e:
        logger.warning("failed to load session", year=year, gp=gp, error=str(e))
        return pd.DataFrame()

    laps = session.laps
    if laps is None or laps.empty:
        return pd.DataFrame()

    df = laps[
        ["Driver", "DriverNumber", "LapNumber", "LapTime", "Sector1Time",
         "Sector2Time", "Sector3Time", "Compound", "TyreLife", "Position",
         "IsPersonalBest", "Stint"]
    ].copy()

    for col in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]:
        df[f"{col}_seconds"] = df[col].dt.total_seconds()

    return df


def collect_all(years: list[int], output_dir: Path | None = None):
    """Collect all data for specified years and save as parquet."""
    setup_cache()
    output_dir = output_dir or RAW_DIR

    all_results = []
    all_qualifying = []
    all_standings = []

    for year in years:
        logger.info("collecting data", year=year)

        results = collect_race_results(year)
        if not results.empty:
            all_results.append(results)

        qualifying = collect_qualifying(year)
        if not qualifying.empty:
            all_qualifying.append(qualifying)

        standings = collect_standings(year)
        if not standings.empty:
            all_standings.append(standings)

    if all_results:
        df = pd.concat(all_results, ignore_index=True)
        df.to_parquet(output_dir / "race_results.parquet", index=False)
        logger.info("saved race results", rows=len(df))

    if all_qualifying:
        df = pd.concat(all_qualifying, ignore_index=True)
        df.to_parquet(output_dir / "qualifying.parquet", index=False)
        logger.info("saved qualifying", rows=len(df))

    if all_standings:
        df = pd.concat(all_standings, ignore_index=True)
        df.to_parquet(output_dir / "standings.parquet", index=False)
        logger.info("saved standings", rows=len(df))


if __name__ == "__main__":
    collect_all(list(range(2018, 2027)))

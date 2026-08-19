"""FastAPI server for serving F1 predictions."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from src.predict.predictor import F1Predictor

app = FastAPI(
    title="F1 Predictions API",
    version="0.1.0",
    description="Machine learning predictions for Formula 1 races",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = F1Predictor()


@app.on_event("startup")
async def startup():
    try:
        predictor.load_models()
    except Exception:
        pass  # Models may not be trained yet


class ChampionshipRequest(BaseModel):
    current_standings: dict[str, float]
    remaining_races: int
    win_probabilities: dict[str, float]


class StrategyRequest(BaseModel):
    circuit_id: str
    total_laps: int
    grid_position: int = 1


@app.get("/health")
async def health():
    return {"status": "ok", "models_loaded": predictor._loaded}


@app.get("/predictions/next-race")
async def predict_next_race():
    """Get predictions for the next upcoming race."""
    from pathlib import Path

    features_path = Path(__file__).parent.parent.parent / "data" / "processed" / "features.parquet"
    if not features_path.exists():
        raise HTTPException(status_code=503, detail="Feature data not available. Run data pipeline first.")

    df = pd.read_parquet(features_path)
    latest_year = df["year"].max()
    latest_round = df[df["year"] == latest_year]["round"].max()
    race_data = df[(df["year"] == latest_year) & (df["round"] == latest_round)]

    if race_data.empty:
        raise HTTPException(status_code=404, detail="No race data found")

    results = predictor.predict_next_race(race_data)
    return results


@app.post("/predictions/championship")
async def predict_championship(request: ChampionshipRequest):
    """Run championship simulation with Monte Carlo."""
    results = predictor.predict_championship(
        request.current_standings,
        request.remaining_races,
        request.win_probabilities,
    )
    return results


@app.post("/predictions/strategy")
async def predict_strategy(request: StrategyRequest):
    """Predict optimal race strategy."""
    return predictor.predict_strategy(
        request.circuit_id, request.total_laps, request.grid_position
    )


@app.get("/models/performance")
async def model_performance():
    """Get model accuracy metrics."""
    return predictor.get_model_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

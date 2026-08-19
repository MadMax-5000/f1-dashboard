from fastapi import APIRouter, Body

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{session_id}")
async def get_predictions(session_id: str, driver_id: str | None = None):
    return {"endpoint": "get_predictions", "session_id": session_id}


@router.post("/predict")
async def predict_lap_time(
    session_id: str = Body(...),
    driver_id: str = Body(...),
    lap_number: int = Body(...),
    features: dict = Body({}),
):
    return {
        "endpoint": "predict_lap_time",
        "session_id": session_id,
        "driver_id": driver_id,
        "lap_number": lap_number,
    }


@router.post("/predict/race")
async def predict_race_outcome(
    session_id: str = Body(...),
    model: str = Body("xgboost"),
    include_uncertainty: bool = Body(True),
):
    return {
        "endpoint": "predict_race_outcome",
        "session_id": session_id,
        "model": model,
        "status": "queued",
    }


@router.get("/models")
async def list_models():
    return {
        "models": [
            {"name": "lap_time_predictor", "version": "1.0", "type": "xgboost"},
            {"name": "race_outcome_predictor", "version": "1.0", "type": "temporal_fusion"},
            {"name": "overtake_probability", "version": "1.0", "type": "gradient_boosting"},
            {"name": "tyre_degradation", "version": "1.0", "type": "neural_network"},
            {"name": "strategy_optimizer", "version": "1.0", "type": "reinforcement_learning"},
        ]
    }

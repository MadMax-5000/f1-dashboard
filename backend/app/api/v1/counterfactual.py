from fastapi import APIRouter, Body
from typing import Annotated

router = APIRouter(prefix="/counterfactual", tags=["counterfactual"])


@router.post("/simulate")
async def simulate_counterfactual(
    session_id: str = Body(...),
    driver_id: str = Body(...),
    scenario_type: str = Body(...),
    intervention: dict = Body(...),
):
    return {
        "endpoint": "simulate_counterfactual",
        "session_id": session_id,
        "scenario_type": scenario_type,
        "status": "queued",
    }


@router.get("/scenarios")
async def list_scenarios():
    return {
        "endpoint": "list_scenarios",
        "scenarios": [
            {
                "id": "pit_one_lap_earlier",
                "name": "Pit One Lap Earlier",
                "description": "Simulate pitting one lap earlier than actual",
                "parameters": {"lap_delta": -1},
            },
            {
                "id": "no_safety_car",
                "name": "Remove Safety Car",
                "description": "Simulate race without safety car periods",
                "parameters": {},
            },
            {
                "id": "different_tyre",
                "name": "Different Tyre Compound",
                "description": "Change tyre compound for a stint",
                "parameters": {"compound": "hard"},
            },
            {
                "id": "no_drs",
                "name": "No DRS",
                "description": "Simulate race without DRS activation",
                "parameters": {},
            },
            {
                "id": "alternative_overtake",
                "name": "Alternative Overtake Attempt",
                "description": "Override an overtake outcome",
                "parameters": {},
            },
            {
                "id": "different_weather",
                "name": "Different Weather",
                "description": "Change weather conditions",
                "parameters": {"condition": "dry"},
            },
            {
                "id": "reduced_pit_time",
                "name": "Reduced Pit Stop Duration",
                "description": "Simulate faster pit stop",
                "parameters": {"time_saved": 1.0},
            },
            {
                "id": "mechanical_issue_removed",
                "name": "Remove Mechanical Issue",
                "description": "Simulate without mechanical problems",
                "parameters": {},
            },
        ],
    }


@router.get("/{counterfactual_id}")
async def get_counterfactual(counterfactual_id: str):
    return {"endpoint": "get_counterfactual", "counterfactual_id": counterfactual_id}


@router.get("/{counterfactual_id}/comparison")
async def compare_counterfactual(counterfactual_id: str):
    return {"endpoint": "compare_counterfactual", "counterfactual_id": counterfactual_id}

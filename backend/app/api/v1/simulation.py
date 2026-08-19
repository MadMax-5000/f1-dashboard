from fastapi import APIRouter, Body, Query
from typing import Annotated

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run")
async def run_simulation(
    session_id: str = Body(...),
    simulation_type: str = Body("monte_carlo"),
    num_runs: Annotated[int, Body(ge=1, le=100000)] = 1000,
    parameters: dict = Body({}),
):
    return {
        "endpoint": "run_simulation",
        "session_id": session_id,
        "type": simulation_type,
        "num_runs": num_runs,
        "status": "queued",
    }


@router.get("/runs/{session_id}")
async def get_simulation_runs(session_id: str):
    return {"endpoint": "get_simulation_runs", "session_id": session_id}


@router.get("/run/{simulation_id}")
async def get_simulation_run(simulation_id: str):
    return {"endpoint": "get_simulation_run", "simulation_id": simulation_id}


@router.get("/run/{simulation_id}/results")
async def get_simulation_results(
    simulation_id: str,
    tick: int | None = None,
    driver_id: str | None = None,
    limit: Annotated[int, Query(le=10000)] = 1000,
):
    return {
        "endpoint": "get_simulation_results",
        "simulation_id": simulation_id,
    }


@router.get("/run/{simulation_id}/distribution")
async def get_simulation_distribution(simulation_id: str):
    return {"endpoint": "get_simulation_distribution", "simulation_id": simulation_id}

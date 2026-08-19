from fastapi import APIRouter, BackgroundTasks, Query
from typing import Annotated

router = APIRouter(prefix="/twin", tags=["digital-twin"])


@router.post("/reconstruct/{session_id}")
async def reconstruct_session(session_id: str, background_tasks: BackgroundTasks):
    return {"endpoint": "reconstruct_session", "session_id": session_id, "status": "queued"}


@router.get("/state/{session_id}")
async def get_twin_state(
    session_id: str,
    tick: int | None = None,
    lap_number: int | None = None,
):
    return {"endpoint": "get_twin_state", "session_id": session_id, "tick": tick}


@router.get("/state/{session_id}/{driver_id}")
async def get_driver_twin_state(
    session_id: str,
    driver_id: str,
    tick: int | None = None,
):
    return {
        "endpoint": "get_driver_twin_state",
        "session_id": session_id,
        "driver_id": driver_id,
    }


@router.post("/replay/{session_id}")
async def replay_session(
    session_id: str,
    speed: Annotated[float, Query(ge=0.1, le=10)] = 1.0,
    start_tick: int | None = None,
    end_tick: int | None = None,
    driver_focus: str | None = None,
):
    return {
        "endpoint": "replay_session",
        "session_id": session_id,
        "speed": speed,
    }

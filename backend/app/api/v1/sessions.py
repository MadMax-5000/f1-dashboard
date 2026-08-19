from fastapi import APIRouter, Query
from typing import Annotated

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}")
async def get_session(session_id: str):
    return {"endpoint": "get_session", "session_id": session_id}


@router.get("/{session_id}/laps")
async def get_session_laps(
    session_id: str,
    driver_id: str | None = None,
    lap_number: int | None = None,
    limit: Annotated[int, Query(le=500)] = 100,
):
    return {
        "endpoint": "get_session_laps",
        "session_id": session_id,
        "driver_id": driver_id,
    }


@router.get("/{session_id}/laps/{lap_number}")
async def get_lap_detail(session_id: str, lap_number: int):
    return {"endpoint": "get_lap_detail", "session_id": session_id, "lap_number": lap_number}


@router.get("/{session_id}/events")
async def get_session_events(
    session_id: str,
    event_type: str | None = None,
    limit: Annotated[int, Query(le=500)] = 100,
):
    return {
        "endpoint": "get_session_events",
        "session_id": session_id,
        "event_type": event_type,
    }

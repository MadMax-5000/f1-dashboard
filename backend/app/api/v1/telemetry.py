from fastapi import APIRouter, Query
from typing import Annotated

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/{session_id}")
async def get_telemetry(
    session_id: str,
    driver_id: str | None = None,
    lap_number: int | None = None,
    limit: Annotated[int, Query(le=10000)] = 1000,
):
    return {"endpoint": "get_telemetry", "session_id": session_id, "driver_id": driver_id}


@router.get("/{session_id}/compare")
async def compare_telemetry(
    session_id: str,
    driver_a: str,
    driver_b: str,
    lap_number: int | None = None,
):
    return {
        "endpoint": "compare_telemetry",
        "session_id": session_id,
        "driver_a": driver_a,
        "driver_b": driver_b,
    }


@router.get("/{session_id}/cars")
async def get_car_data(
    session_id: str,
    driver_id: str | None = None,
    limit: Annotated[int, Query(le=10000)] = 1000,
):
    return {"endpoint": "get_car_data", "session_id": session_id, "driver_id": driver_id}


@router.websocket("/{session_id}/stream")
async def stream_telemetry(session_id: str):
    return None

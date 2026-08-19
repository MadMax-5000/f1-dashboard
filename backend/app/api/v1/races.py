from fastapi import APIRouter, Depends, Query
from typing import Annotated

router = APIRouter(prefix="/races", tags=["races"])


@router.get("/")
async def list_races(
    season: int | None = Query(None, ge=1950, le=2100),
    circuit_id: str | None = None,
    limit: Annotated[int, Query(le=100)] = 20,
    offset: int = 0,
):
    return {"endpoint": "list_races", "season": season, "limit": limit, "offset": offset}


@router.get("/{race_id}")
async def get_race(race_id: str):
    return {"endpoint": "get_race", "race_id": race_id}


@router.get("/{race_id}/sessions")
async def get_race_sessions(race_id: str):
    return {"endpoint": "get_race_sessions", "race_id": race_id}


@router.get("/{race_id}/results")
async def get_race_results(race_id: str):
    return {"endpoint": "get_race_results", "race_id": race_id}


@router.get("/{race_id}/standings")
async def get_race_standings(race_id: str):
    return {"endpoint": "get_race_standings", "race_id": race_id}

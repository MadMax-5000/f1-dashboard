from fastapi import APIRouter

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/")
async def list_teams(season: int | None = None):
    return {"endpoint": "list_teams", "season": season}


@router.get("/{team_id}")
async def get_team(team_id: str):
    return {"endpoint": "get_team", "team_id": team_id}

from fastapi import APIRouter

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("/")
async def list_drivers(season: int | None = None):
    return {"endpoint": "list_drivers", "season": season}


@router.get("/{driver_id}")
async def get_driver(driver_id: str):
    return {"endpoint": "get_driver", "driver_id": driver_id}


@router.get("/{driver_id}/laps")
async def get_driver_laps(driver_id: str, session_id: str | None = None):
    return {"endpoint": "get_driver_laps", "driver_id": driver_id}


@router.get("/{driver_id}/overtakes")
async def get_driver_overtakes(driver_id: str, session_id: str | None = None):
    return {"endpoint": "get_driver_overtakes", "driver_id": driver_id}


@router.get("/{driver_id}/comparison")
async def driver_comparison(driver_a: str, driver_b: str, session_id: str):
    return {"endpoint": "driver_comparison", "driver_a": driver_a, "driver_b": driver_b}

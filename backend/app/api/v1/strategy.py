from fastapi import APIRouter, Body

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.get("/{session_id}")
async def get_strategies(session_id: str, driver_id: str | None = None):
    return {"endpoint": "get_strategies", "session_id": session_id, "driver_id": driver_id}


@router.post("/optimize")
async def optimize_strategy(
    session_id: str = Body(...),
    driver_id: str = Body(...),
    objective: str = Body("maximize_finish_position"),
    constraints: dict | None = None,
):
    return {
        "endpoint": "optimize_strategy",
        "session_id": session_id,
        "objective": objective,
        "status": "queued",
    }


@router.get("/tree/{session_id}/{driver_id}")
async def get_strategy_tree(session_id: str, driver_id: str):
    return {"endpoint": "get_strategy_tree", "session_id": session_id, "driver_id": driver_id}


@router.get("/comparison/{session_id}")
async def compare_strategies(session_id: str, driver_ids: str):
    return {"endpoint": "compare_strategies", "session_id": session_id}

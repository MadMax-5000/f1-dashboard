from fastapi import APIRouter

router = APIRouter(prefix="/circuits", tags=["circuits"])


@router.get("/")
async def list_circuits():
    return {"endpoint": "list_circuits"}


@router.get("/{circuit_id}")
async def get_circuit(circuit_id: str):
    return {"endpoint": "get_circuit", "circuit_id": circuit_id}


@router.get("/{circuit_id}/map")
async def get_circuit_map(circuit_id: str):
    return {"endpoint": "get_circuit_map", "circuit_id": circuit_id}


@router.get("/{circuit_id}/corners")
async def get_circuit_corners(circuit_id: str):
    return {"endpoint": "get_circuit_corners", "circuit_id": circuit_id}

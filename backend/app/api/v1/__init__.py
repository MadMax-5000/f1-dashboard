from fastapi import APIRouter
from . import (
    races,
    sessions,
    telemetry,
    drivers,
    teams,
    circuits,
    twin,
    counterfactual,
    strategy,
    predictions,
    simulation,
)

router = APIRouter()
router.include_router(races.router)
router.include_router(sessions.router)
router.include_router(telemetry.router)
router.include_router(drivers.router)
router.include_router(teams.router)
router.include_router(circuits.router)
router.include_router(twin.router)
router.include_router(counterfactual.router)
router.include_router(strategy.router)
router.include_router(predictions.router)
router.include_router(simulation.router)

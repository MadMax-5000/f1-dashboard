import structlog
import numpy as np
from dataclasses import dataclass, field
from typing import Any
from copy import deepcopy

from app.twin.engine import RaceState, DriverState, TwinSimulator

logger = structlog.get_logger()


@dataclass
class CounterfactualScenario:
    id: str
    name: str
    description: str
    intervention: dict[str, Any]
    type: str


@dataclass
class CounterfactualResult:
    scenario_id: str
    original_outcome: dict[str, Any]
    counterfactual_outcome: dict[str, Any]
    delta: dict[str, float]
    confidence: float
    probability_distribution: dict[str, float] | None = None
    narrative: str | None = None


SCENARIO_REGISTRY: dict[str, CounterfactualScenario] = {
    "pit_one_lap_earlier": CounterfactualScenario(
        id="pit_one_lap_earlier",
        name="Pit One Lap Earlier",
        description="Shift all pit stops one lap earlier",
        intervention={"type": "pit_delta", "lap_delta": -1},
        type="strategy",
    ),
    "pit_one_lap_later": CounterfactualScenario(
        id="pit_one_lap_later",
        name="Pit One Lap Later",
        description="Shift all pit stops one lap later",
        intervention={"type": "pit_delta", "lap_delta": 1},
        type="strategy",
    ),
    "no_safety_car": CounterfactualScenario(
        id="no_safety_car",
        name="Remove Safety Car",
        description="Simulate race without any safety car periods",
        intervention={"type": "remove_safety_car"},
        type="race_condition",
    ),
    "different_tyre_compound": CounterfactualScenario(
        id="different_tyre_compound",
        name="Change Tyre Compound",
        description="Use a different tyre compound for the stint",
        intervention={"type": "tyre_compound", "compound": "hard"},
        type="strategy",
    ),
    "no_drs": CounterfactualScenario(
        id="no_drs",
        name="No DRS",
        description="Simulate race without DRS activation",
        intervention={"type": "disable_drs"},
        type="regulation",
    ),
    "reduced_pit_time": CounterfactualScenario(
        id="reduced_pit_time",
        name="Reduced Pit Stop",
        description="Reduce pit stop duration by specified seconds",
        intervention={"type": "pit_time_delta", "time_delta": -1.0},
        type="strategy",
    ),
    "different_weather": CounterfactualScenario(
        id="different_weather",
        name="Weather Change",
        description="Change weather conditions",
        intervention={"type": "weather", "condition": "dry"},
        type="environment",
    ),
    "mechanical_issue_removed": CounterfactualScenario(
        id="mechanical_issue_removed",
        name="Remove Mechanical Issue",
        description="Simulate without mechanical problems",
        intervention={"type": "remove_mechanical_issue"},
        type="reliability",
    ),
    "alternative_overtake": CounterfactualScenario(
        id="alternative_overtake",
        name="Alternative Overtake",
        description="Change the outcome of a specific overtake attempt",
        intervention={"type": "overtake_outcome", "overtake_id": "", "succeed": True},
        type="racing",
    ),
}


class CounterfactualEngine:
    def __init__(self, base_simulator: TwinSimulator):
        self._base = base_simulator
        self._results: dict[str, CounterfactualResult] = {}

    @property
    def results(self) -> dict[str, CounterfactualResult]:
        return dict(self._results)

    def get_scenario(self, scenario_id: str) -> CounterfactualScenario | None:
        return SCENARIO_REGISTRY.get(scenario_id)

    def list_scenarios(self) -> list[CounterfactualScenario]:
        return list(SCENARIO_REGISTRY.values())

    async def run(
        self,
        scenario_id: str,
        target_driver_id: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> CounterfactualResult:
        scenario = self.get_scenario(scenario_id)
        if scenario is None:
            raise ValueError(f"Unknown scenario: {scenario_id}")

        base_state = self._base.state
        if base_state is None:
            raise ValueError("Base simulator has no state initialized")

        intervention = dict(scenario.intervention)
        if parameters:
            intervention.update(parameters)

        original = self._extract_outcome(base_state, target_driver_id)
        cf_state = deepcopy(base_state)
        self._apply_intervention(cf_state, intervention, target_driver_id)
        counterfactual = self._extract_outcome(cf_state, target_driver_id)
        delta = self._compute_delta(original, counterfactual)
        confidence = self._estimate_confidence(scenario.type)

        result = CounterfactualResult(
            scenario_id=scenario_id,
            original_outcome=original,
            counterfactual_outcome=counterfactual,
            delta=delta,
            confidence=confidence,
            probability_distribution=self._generate_distribution(delta, confidence),
            narrative=self._generate_narrative(scenario, delta, target_driver_id),
        )
        self._results[scenario_id] = result
        logger.info(
            "counterfactual completed",
            scenario=scenario_id,
            confidence=confidence,
        )
        return result

    def _apply_intervention(
        self,
        state: RaceState,
        intervention: dict[str, Any],
        target_driver: str | None,
    ):
        itype = intervention.get("type")
        if itype == "pit_delta":
            lap_delta = intervention.get("lap_delta", 0)
            if target_driver and target_driver in state.drivers:
                self._shift_pit(state.drivers[target_driver], lap_delta)
        elif itype == "remove_safety_car":
            state.safety_car_active = False
            state.vsc_active = False
            self._adjust_pace_for_no_sc(state)
        elif itype == "tyre_compound":
            compound = intervention.get("compound", "hard")
            if target_driver and target_driver in state.drivers:
                state.drivers[target_driver].tyre_compound = compound
        elif itype == "disable_drs":
            for ds in state.drivers.values():
                ds.has_drs_available = False
                ds.drs_active = False
        elif itype == "pit_time_delta":
            time_delta = intervention.get("time_delta", 0)
        elif itype == "weather":
            condition = intervention.get("condition", "dry")
            if condition == "dry":
                state.rainfall = False
                state.rain_intensity = 0.0
                state.track_grip = 1.0
                state.track_temperature = 35.0
            elif condition == "wet":
                state.rainfall = True
                state.rain_intensity = 2.0
                state.track_grip = 0.6
                state.track_temperature = 22.0
        elif itype == "remove_mechanical_issue":
            if target_driver and target_driver in state.drivers:
                state.drivers[target_driver].is_retired = False
                state.drivers[target_driver].speed = max(state.drivers[target_driver].speed, 200)

    def _shift_pit(self, ds: DriverState, lap_delta: int):
        pass

    def _adjust_pace_for_no_sc(self, state: RaceState):
        for ds in state.drivers.values():
            if ds.in_safety_car_period:
                ds.speed = min(ds.speed, 250)

    def _extract_outcome(self, state: RaceState, driver_id: str | None) -> dict[str, Any]:
        if driver_id and driver_id in state.drivers:
            ds = state.drivers[driver_id]
            return {
                "position": ds.position,
                "lap": ds.lap_number,
                "speed": ds.speed,
                "tyre_compound": ds.tyre_compound,
                "tyre_age": ds.tyre_age_laps,
                "fuel_remaining": ds.fuel_remaining,
                "is_retired": ds.is_retired,
            }
        return {
            "order": state.order[:5],
            "lap": state.lap_number,
            "safety_car": state.safety_car_active,
        }

    def _compute_delta(
        self, original: dict[str, Any], counterfactual: dict[str, Any]
    ) -> dict[str, float]:
        deltas = {}
        for key in ("position", "lap", "speed", "tyre_age", "fuel_remaining"):
            if key in original and key in counterfactual:
                if original[key] is not None and counterfactual[key] is not None:
                    deltas[f"delta_{key}"] = float(
                        (counterfactual[key] or 0) - (original[key] or 0)
                    )
        return deltas

    def _estimate_confidence(self, scenario_type: str) -> float:
        confidence_map = {
            "strategy": 0.75,
            "race_condition": 0.50,
            "regulation": 0.85,
            "environment": 0.60,
            "reliability": 0.40,
            "racing": 0.55,
        }
        return confidence_map.get(scenario_type, 0.5)

    def _generate_distribution(
        self, delta: dict[str, float], confidence: float
    ) -> dict[str, float]:
        pos_delta = delta.get("delta_position", 0)
        std = 1.0 + (1.0 - confidence) * 3.0
        return {
            "mean": float(pos_delta),
            "std": float(std),
            "p5": float(pos_delta - 1.645 * std),
            "p50": float(pos_delta),
            "p95": float(pos_delta + 1.645 * std),
        }

    def _generate_narrative(
        self,
        scenario: CounterfactualScenario,
        delta: dict[str, float],
        target_driver: str | None,
    ) -> str:
        pos_delta = delta.get("delta_position", 0)
        if pos_delta < 0:
            return (
                f"{scenario.name} would gain {abs(int(pos_delta))} "
                f"position(s) for driver {target_driver}."
            )
        elif pos_delta > 0:
            return (
                f"{scenario.name} would lose {int(pos_delta)} "
                f"position(s) for driver {target_driver}."
            )
        return f"{scenario.name} shows no significant position change for driver {target_driver}."

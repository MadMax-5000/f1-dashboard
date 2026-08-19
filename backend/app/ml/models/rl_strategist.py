import numpy as np
import structlog
from dataclasses import dataclass
from typing import Any
from enum import Enum

logger = structlog.get_logger()


class PitAction(str, Enum):
    STAY_OUT = "stay_out"
    PIT_SOFT = "pit_soft"
    PIT_MEDIUM = "pit_medium"
    PIT_HARD = "pit_hard"
    PIT_INTERMEDIATE = "pit_intermediate"
    PIT_WET = "pit_wet"


class PaceMode(str, Enum):
    ATTACK = "attack"
    NORMAL = "normal"
    CONSERVE = "conserve"
    FUEL_SAVE = "fuel_save"
    PUSH = "push"


class ERSMode(str, Enum):
    BALANCED = "balanced"
    OVERTAKE = "overtake"
    DEFEND = "defend"
    HARVEST = "harvest"
    CHARGING = "charging"


@dataclass
class StrategyState:
    lap_number: int
    total_laps: int
    position: int
    driver_count: int
    gap_to_front: float
    gap_to_next: float
    gap_to_prev: float
    tyre_compound: str
    tyre_age_laps: int
    fuel_remaining: float
    fuel_per_lap: float
    track_temperature: float
    rainfall: float
    safety_car_active: bool
    stint_count: int
    laps_remaining: int
    pit_time_loss: float
    drs_available: bool
    track_position_value: float

    def to_array(self) -> np.ndarray:
        compound_map = {"soft": 0, "medium": 1, "hard": 2, "intermediate": 3, "wet": 4}
        return np.array(
            [
                self.lap_number / self.total_laps,
                self.position / max(self.driver_count, 1),
                np.clip(self.gap_to_front / 60.0, 0, 1),
                np.clip(self.gap_to_next / 10.0, 0, 1),
                np.clip(self.gap_to_prev / 10.0, 0, 1),
                compound_map.get(self.tyre_compound, 0) / 4.0,
                self.tyre_age_laps / 50.0,
                self.fuel_remaining / 110.0,
                np.clip(self.fuel_per_lap / 3.0, 0, 1),
                np.clip(self.track_temperature / 50.0, 0, 1),
                self.rainfall,
                float(self.safety_car_active),
                self.stint_count / 5.0,
                self.laps_remaining / self.total_laps,
                np.clip(self.pit_time_loss / 30.0, 0, 1),
                float(self.drs_available),
                np.clip(self.track_position_value, 0, 1),
            ],
            dtype=np.float32,
        )


class RLStrategist:
    def __init__(self):
        self._q_table: dict[bytes, np.ndarray] = {}
        self._epsilon = 0.1
        self._gamma = 0.95
        self._alpha = 0.1
        self._discrete_bins = 10

    def _discretize(self, state: np.ndarray) -> bytes:
        discrete = np.clip(
            np.floor(state * self._discrete_bins), 0, self._discrete_bins - 1
        ).astype(np.int8)
        return discrete.tobytes()

    def _get_pit_action(self, state: StrategyState) -> PitAction:
        if state.rainfall > 0.5:
            if state.tyre_compound in ("intermediate", "wet"):
                return PitAction.STAY_OUT
            return PitAction.PIT_INTERMEDIATE if state.rainfall < 2.0 else PitAction.PIT_WET
        if state.tyre_age_laps > 25:
            return PitAction.PIT_HARD
        if state.tyre_age_laps > 18 and state.laps_remaining > 15:
            return PitAction.PIT_MEDIUM
        return PitAction.STAY_OUT

    def _get_pace_mode(self, state: StrategyState) -> PaceMode:
        if state.laps_remaining <= 3:
            return PaceMode.PUSH
        if state.gap_to_next < 1.0 and state.drs_available:
            return PaceMode.ATTACK
        if state.gap_to_prev < 1.0 and state.gap_to_prev > 0:
            return PaceMode.DEFEND
        if state.fuel_remaining / max(state.laps_remaining, 1) < 1.5:
            return PaceMode.FUEL_SAVE
        return PaceMode.NORMAL

    def recommend(self, state: StrategyState) -> dict[str, Any]:
        pit_action = self._get_pit_action(state)
        pace_mode = self._get_pace_mode(state)

        return {
            "pit_action": pit_action.value,
            "pace_mode": pace_mode.value,
            "ers_mode": ERSMode.BALANCED.value,
            "reasoning": {
                "tyre_condition": "degraded" if state.tyre_age_laps > 18 else "fresh",
                "fuel_status": "critical"
                if state.fuel_remaining / max(state.laps_remaining, 1) < 1.5
                else "adequate",
                "race_phase": "late"
                if state.laps_remaining <= 5
                else "mid"
                if state.laps_remaining <= state.total_laps * 0.7
                else "early",
                "gap_analysis": {
                    "to_front": round(state.gap_to_front, 1),
                    "to_next": round(state.gap_to_next, 1),
                    "to_prev": round(state.gap_to_prev, 1),
                },
            },
            "recommended_pit_window": self._get_pit_window(state),
            "confidence": 0.75,
        }

    def _get_pit_window(self, state: StrategyState) -> dict[str, int]:
        ideal_lap = state.lap_number + max(5, 30 - state.tyre_age_laps)
        return {
            "earliest": max(state.lap_number + 1, state.lap_number),
            "ideal": min(ideal_lap, state.total_laps - 5),
            "latest": state.total_laps - 1,
        }

    def update(
        self,
        state: StrategyState,
        action: str,
        reward: float,
        next_state: StrategyState,
    ):
        state_key = self._discretize(state.to_array())
        if state_key not in self._q_table:
            self._q_table[state_key] = np.zeros(len(PitAction))
        action_idx = list(PitAction).index(PitAction(action))
        next_key = self._discretize(next_state.to_array())
        next_max = np.max(self._q_table[next_key]) if next_key in self._q_table else 0
        td_target = reward + self._gamma * next_max
        td_error = td_target - self._q_table[state_key][action_idx]
        self._q_table[state_key][action_idx] += self._alpha * td_error

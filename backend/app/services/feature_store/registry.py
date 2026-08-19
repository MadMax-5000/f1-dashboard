import uuid
import structlog
import numpy as np
from datetime import datetime, timezone
from typing import Any, Callable
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class FeatureDefinition:
    name: str
    domain: str
    entity: str
    description: str
    data_type: str
    dimensionality: int = 1
    source: str = ""
    computation_fn: Callable | None = None
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)

    def compute(self, *args, **kwargs) -> Any:
        if self.computation_fn:
            return self.computation_fn(*args, **kwargs)
        raise NotImplementedError(f"No computation function for {self.name}")


@dataclass
class FeatureVector:
    entity_id: str
    timestamp: datetime
    features: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureRegistry:
    def __init__(self):
        self._definitions: dict[str, FeatureDefinition] = {}
        self._vectors: list[FeatureVector] = []
        self._stats: dict[str, dict] = {}

    def register(self, definition: FeatureDefinition):
        if definition.name in self._definitions:
            logger.warning("feature_redefined", name=definition.name)
        self._definitions[definition.name] = definition
        logger.info("feature_registered", name=definition.name, domain=definition.domain)

    def get(self, name: str) -> FeatureDefinition | None:
        return self._definitions.get(name)

    def list_by_domain(self, domain: str) -> list[FeatureDefinition]:
        return [f for f in self._definitions.values() if f.domain == domain]

    def list_by_entity(self, entity: str) -> list[FeatureDefinition]:
        return [f for f in self._definitions.values() if f.entity == entity]

    def compute_vector(self, entity_id: str, features: list[str], **kwargs) -> FeatureVector:
        computed = {}
        for fname in features:
            defn = self._definitions.get(fname)
            if defn:
                computed[fname] = defn.compute(**kwargs)
            else:
                logger.warning("feature_not_found", name=fname)
        return FeatureVector(
            entity_id=entity_id,
            timestamp=datetime.now(timezone.utc),
            features=computed,
        )

    def store_vector(self, vector: FeatureVector):
        self._vectors.append(vector)
        for name, value in vector.features.items():
            if name not in self._stats:
                self._stats[name] = {
                    "count": 0,
                    "sum": 0.0,
                    "sum_sq": 0.0,
                    "min": float("inf"),
                    "max": float("-inf"),
                }
            s = self._stats[name]
            s["count"] += 1
            if isinstance(value, (int, float)):
                s["sum"] += value
                s["sum_sq"] += value * value
                s["min"] = min(s["min"], value)
                s["max"] = max(s["max"], value)

    def get_statistics(self, feature_name: str) -> dict[str, float] | None:
        s = self._stats.get(feature_name)
        if not s or s["count"] == 0:
            return None
        mean = s["sum"] / s["count"]
        variance = (s["sum_sq"] / s["count"]) - (mean * mean)
        return {
            "count": s["count"],
            "mean": mean,
            "std": np.sqrt(max(0, variance)),
            "min": s["min"],
            "max": s["max"],
        }

    @property
    def definitions(self) -> dict[str, FeatureDefinition]:
        return dict(self._definitions)


feature_registry = FeatureRegistry()


def register_feature(
    name: str, domain: str, entity: str, description: str, data_type: str = "float"
):
    def decorator(func: Callable):
        feature_registry.register(
            FeatureDefinition(
                name=name,
                domain=domain,
                entity=entity,
                description=description,
                data_type=data_type,
                computation_fn=func,
            )
        )
        return func

    return decorator


# ── Built-in Feature Definitions ──


@register_feature("lap_time_rolling_avg", "pace", "driver", "Rolling average of last 5 lap times")
def lap_time_rolling_avg(lap_times: list[float]) -> float:
    recent = lap_times[-5:] if len(lap_times) >= 5 else lap_times
    return float(np.mean(recent)) if recent else 0.0


@register_feature(
    "tyre_degradation_rate", "tyre", "driver", "Lap time loss per lap on current tyre set"
)
def tyre_degradation_rate(lap_times: list[float], tyre_age: list[int]) -> float:
    if len(lap_times) < 3:
        return 0.0
    coeffs = np.polyfit(tyre_age[-len(lap_times) :], lap_times, 1)
    return float(coeffs[0]) if len(coeffs) > 0 else 0.0


@register_feature(
    "fuel_effect_adjustment", "car", "driver", "Expected lap time gain per 10kg fuel burn"
)
def fuel_effect_adjustment(fuel_burn_per_lap: float) -> float:
    return fuel_burn_per_lap * 0.03


@register_feature("track_position_value", "race", "driver", "Value of current track position (0-1)")
def track_position_value(position: int, total_cars: int, lap: int, total_laps: int) -> float:
    pos_norm = 1.0 - (position - 1) / max(total_cars - 1, 1)
    lap_progress = lap / max(total_laps, 1)
    return float(pos_norm * 0.7 + lap_progress * 0.3)


@register_feature("dirty_air_estimate", "aero", "driver", "Estimated lap time loss from dirty air")
def dirty_air_estimate(delta_to_front: float, track_type: str = "high_speed") -> float:
    if delta_to_front < 1.0:
        return float((1.0 - delta_to_front) * (0.3 if track_type == "high_speed" else 0.15))
    return 0.0


@register_feature(
    "overtaking_opportunity_score", "race", "driver", "Likelihood of successful overtake (0-1)"
)
def overtaking_opportunity_score(
    speed_advantage: float,
    drs_available: bool,
    straight_length: float,
    defending_skill: float = 0.5,
) -> float:
    drs_bonus = 0.15 if drs_available else 0.0
    raw_score = (speed_advantage + drs_bonus) * (straight_length / 1000.0)
    return float(np.clip(raw_score * (1.0 - defending_skill), 0.0, 1.0))

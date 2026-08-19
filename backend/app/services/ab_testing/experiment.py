import uuid
import structlog
import numpy as np
from datetime import datetime, timezone
from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = structlog.get_logger()


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ANALYSED = "analysed"


class VariantType(str, Enum):
    CONTROL = "control"
    TREATMENT = "treatment"
    CHAMPION = "champion"
    CHALLENGER = "challenger"


@dataclass
class ExperimentVariant:
    name: str
    variant_type: VariantType
    config: dict[str, Any]
    traffic_allocation: float = 0.5
    metrics: dict[str, list[float]] = field(default_factory=dict)


@dataclass
class Experiment:
    experiment_id: str
    name: str
    description: str
    hypothesis: str
    status: ExperimentStatus
    variants: list[ExperimentVariant]
    target_metric: str
    minimum_sample_size: int = 100
    confidence_level: float = 0.95
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    results: dict[str, Any] = field(default_factory=dict)


class ExperimentService:
    def __init__(self):
        self._experiments: dict[str, Experiment] = {}
        self._rng = np.random.default_rng()

    def create(
        self,
        name: str,
        description: str,
        hypothesis: str,
        control_config: dict[str, Any],
        treatment_configs: list[dict[str, Any]],
        target_metric: str = "finish_position",
        minimum_sample_size: int = 100,
    ) -> Experiment:
        eid = str(uuid.uuid4())
        variants = [
            ExperimentVariant(
                name="control",
                variant_type=VariantType.CONTROL,
                config=control_config,
                traffic_allocation=0.5 / (len(treatment_configs) + 1),
            )
        ]
        for i, tc in enumerate(treatment_configs):
            variants.append(
                ExperimentVariant(
                    name=f"treatment_{i}",
                    variant_type=VariantType.TREATMENT,
                    config=tc,
                    traffic_allocation=0.5 / (len(treatment_configs) + 1),
                )
            )
        exp = Experiment(
            experiment_id=eid,
            name=name,
            description=description,
            hypothesis=hypothesis,
            status=ExperimentStatus.DRAFT,
            variants=variants,
            target_metric=target_metric,
            minimum_sample_size=minimum_sample_size,
        )
        self._experiments[eid] = exp
        logger.info("experiment_created", name=name, id=eid)
        return exp

    def assign_variant(self, experiment_id: str, entity_id: str) -> str | None:
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != ExperimentStatus.RUNNING:
            return None
        r = self._rng.random()
        cumulative = 0.0
        for v in exp.variants:
            cumulative += v.traffic_allocation
            if r <= cumulative:
                logger.debug(
                    "variant_assigned", experiment=exp.name, entity=entity_id, variant=v.name
                )
                return v.name
        return exp.variants[-1].name if exp.variants else None

    def record_metric(
        self,
        experiment_id: str,
        variant_name: str,
        metric_name: str,
        value: float,
    ):
        exp = self._experiments.get(experiment_id)
        if not exp:
            return
        for v in exp.variants:
            if v.name == variant_name:
                if metric_name not in v.metrics:
                    v.metrics[metric_name] = []
                v.metrics[metric_name].append(value)
                break

    def start(self, experiment_id: str):
        exp = self._experiments.get(experiment_id)
        if not exp:
            return
        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.now(timezone.utc)
        logger.info("experiment_started", name=exp.name)

    def stop(self, experiment_id: str):
        exp = self._experiments.get(experiment_id)
        if not exp:
            return
        exp.status = ExperimentStatus.COMPLETED
        exp.completed_at = datetime.now(timezone.utc)
        self._analyse(exp)
        logger.info("experiment_completed", name=exp.name)

    def _analyse(self, exp: Experiment):
        import scipy.stats as stats

        control = None
        for v in exp.variants:
            if v.variant_type == VariantType.CONTROL:
                control = v
                break
        if not control:
            return
        control_data = control.metrics.get(exp.target_metric, [])
        results = {}
        for v in exp.variants:
            if v.variant_type == VariantType.CONTROL:
                continue
            treatment_data = v.metrics.get(exp.target_metric, [])
            if len(control_data) < 3 or len(treatment_data) < 3:
                results[v.name] = {"error": "insufficient_data"}
                continue
            t_stat, p_value = stats.ttest_ind(control_data, treatment_data, equal_var=False)
            effect_size = (np.mean(treatment_data) - np.mean(control_data)) / np.std(control_data)
            results[v.name] = {
                "mean_control": float(np.mean(control_data)),
                "mean_treatment": float(np.mean(treatment_data)),
                "effect_size": float(effect_size),
                "p_value": float(p_value),
                "significant": bool(p_value < (1.0 - exp.confidence_level)),
                "sample_size_control": len(control_data),
                "sample_size_treatment": len(treatment_data),
                "improvement_pct": float(
                    (np.mean(treatment_data) - np.mean(control_data))
                    / abs(np.mean(control_data))
                    * 100
                ),
            }
        exp.results = results
        exp.status = ExperimentStatus.ANALYSED
        logger.info("experiment_analysed", name=exp.name, results=results)

    def get(self, experiment_id: str) -> Experiment | None:
        return self._experiments.get(experiment_id)

    def list(self, status: ExperimentStatus | None = None) -> list[Experiment]:
        if status:
            return [e for e in self._experiments.values() if e.status == status]
        return list(self._experiments.values())


experiment_service = ExperimentService()

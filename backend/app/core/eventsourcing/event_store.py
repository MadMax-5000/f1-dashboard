import uuid
import structlog
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Protocol
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = structlog.get_logger()


class EventCategory(str, Enum):
    RACE_LIFECYCLE = "race_lifecycle"
    POSITION_CHANGE = "position_change"
    PIT_STOP = "pit_stop"
    OVERTAKE = "overtake"
    INCIDENT = "incident"
    PENALTY = "penalty"
    WEATHER = "weather"
    STRATEGY = "strategy"
    SIMULATION = "simulation"
    ANOMALY = "anomaly"


@dataclass
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    aggregate_id: str = ""
    event_type: str = ""
    category: EventCategory = EventCategory.RACE_LIFECYCLE
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    causation_id: uuid.UUID | None = None
    correlation_id: uuid.UUID | None = None

    @property
    def event_key(self) -> str:
        return f"{self.aggregate_id}:{self.event_type}:{self.version}"


class EventStore(Protocol):
    async def append(self, event: DomainEvent) -> None: ...
    async def read_stream(
        self, aggregate_id: str, from_version: int = 0
    ) -> AsyncGenerator[DomainEvent, None]: ...
    async def read_category(
        self, category: EventCategory, limit: int = 100
    ) -> list[DomainEvent]: ...


class PostgresEventStore:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def append(self, event: DomainEvent) -> None:
        async with self._session_factory() as session:
            stmt = """
                INSERT INTO event_store (
                    event_id, aggregate_id, event_type, category,
                    timestamp, version, data, metadata,
                    causation_id, correlation_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb, $9, $10)
            """
            await session.execute(
                stmt,
                event.event_id,
                event.aggregate_id,
                event.event_type,
                event.category.value,
                event.timestamp,
                event.version,
                event.data,
                event.metadata,
                event.causation_id,
                event.correlation_id,
            )
            logger.debug("event_appended", type=event.event_type, aggregate=event.aggregate_id)

    async def read_stream(
        self, aggregate_id: str, from_version: int = 0
    ) -> AsyncGenerator[DomainEvent, None]:
        async with self._session_factory() as session:
            rows = await session.fetch(
                """
                SELECT * FROM event_store
                WHERE aggregate_id = $1 AND version >= $2
                ORDER BY version ASC
                """,
                aggregate_id,
                from_version,
            )
            for row in rows:
                yield DomainEvent(
                    event_id=row["event_id"],
                    aggregate_id=row["aggregate_id"],
                    event_type=row["event_type"],
                    category=EventCategory(row["category"]),
                    timestamp=row["timestamp"],
                    version=row["version"],
                    data=row["data"],
                    metadata=row["metadata"],
                )

    async def read_category(self, category: EventCategory, limit: int = 100) -> list[DomainEvent]:
        async with self._session_factory() as session:
            rows = await session.fetch(
                """
                SELECT * FROM event_store
                WHERE category = $1
                ORDER BY timestamp DESC
                LIMIT $2
                """,
                category.value,
                limit,
            )
            return [
                DomainEvent(
                    event_id=row["event_id"],
                    aggregate_id=row["aggregate_id"],
                    event_type=row["event_type"],
                    category=EventCategory(row["category"]),
                    timestamp=row["timestamp"],
                    version=row["version"],
                    data=row["data"],
                )
                for row in rows
            ]


# Event definitions for the F1 domain
class RaceEvents:
    @staticmethod
    def race_started(race_id: str, data: dict) -> DomainEvent:
        return DomainEvent(
            aggregate_id=race_id,
            event_type="race.started",
            category=EventCategory.RACE_LIFECYCLE,
            data=data,
        )

    @staticmethod
    def lap_completed(
        race_id: str, driver_id: str, lap_number: int, lap_time: float
    ) -> DomainEvent:
        return DomainEvent(
            aggregate_id=f"{race_id}:{driver_id}",
            event_type="lap.completed",
            category=EventCategory.POSITION_CHANGE,
            data={
                "driver_id": driver_id,
                "lap_number": lap_number,
                "lap_time": lap_time,
            },
        )

    @staticmethod
    def overtake_committed(
        race_id: str,
        overtaking_driver: str,
        overtaken_driver: str,
        lap: int,
        location: str,
        probability: float,
    ) -> DomainEvent:
        return DomainEvent(
            aggregate_id=race_id,
            event_type="overtake.committed",
            category=EventCategory.OVERTAKE,
            data={
                "overtaking_driver": overtaking_driver,
                "overtaken_driver": overtaken_driver,
                "lap": lap,
                "location": location,
                "probability_success": probability,
            },
        )

    @staticmethod
    def pit_stop_completed(
        race_id: str,
        driver_id: str,
        lap: int,
        duration: float,
        compound_out: str,
    ) -> DomainEvent:
        return DomainEvent(
            aggregate_id=f"{race_id}:{driver_id}",
            event_type="pit.stop_completed",
            category=EventCategory.PIT_STOP,
            data={
                "driver_id": driver_id,
                "lap": lap,
                "duration": duration,
                "compound": compound_out,
            },
        )

    @staticmethod
    def safety_car_deployed(race_id: str, lap: int, reason: str) -> DomainEvent:
        return DomainEvent(
            aggregate_id=race_id,
            event_type="safety_car.deployed",
            category=EventCategory.INCIDENT,
            data={"lap": lap, "reason": reason},
        )


class EventSourcedRace:
    def __init__(self, race_id: str, event_store: PostgresEventStore):
        self._id = race_id
        self._store = event_store
        self._uncommitted: list[DomainEvent] = []
        self._version = 0
        self._state: dict[str, Any] = {}

    @property
    def version(self) -> int:
        return self._version

    async def load(self):
        async for event in self._store.read_stream(self._id):
            self._apply(event)
            self._version = event.version

    def _apply(self, event: DomainEvent):
        if event.event_type == "race.started":
            self._state["status"] = "running"
            self._state["start_time"] = event.timestamp
        elif event.event_type == "lap.completed":
            driver = event.data["driver_id"]
            if "laps" not in self._state:
                self._state["laps"] = {}
            if driver not in self._state["laps"]:
                self._state["laps"][driver] = []
            self._state["laps"][driver].append(event.data)
        elif event.event_type == "overtake.committed":
            if "overtakes" not in self._state:
                self._state["overtakes"] = []
            self._state["overtakes"].append(event.data)
        elif event.event_type == "pit.stop_completed":
            driver = event.data["driver_id"]
            if "pit_stops" not in self._state:
                self._state["pit_stops"] = {}
            if driver not in self._state["pit_stops"]:
                self._state["pit_stops"][driver] = []
            self._state["pit_stops"][driver].append(event.data)

    def add_event(self, event: DomainEvent):
        self._apply(event)
        self._version += 1
        event.version = self._version
        self._uncommitted.append(event)

    async def commit(self):
        for event in self._uncommitted:
            await self._store.append(event)
        self._uncommitted.clear()
        logger.info("events_committed", count=len(self._uncommitted), race=self._id)

    def get_state(self) -> dict[str, Any]:
        return dict(self._state)

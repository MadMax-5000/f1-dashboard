import uuid
import structlog
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable, TypeVar
from dataclasses import dataclass, field
from enum import Enum

logger = structlog.get_logger()

T = TypeVar("T")
CommandHandler = Callable[..., Awaitable[Any]]
QueryHandler = Callable[..., Awaitable[Any]]


class CommandStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class Command:
    command_id: uuid.UUID = field(default_factory=uuid.uuid4)
    command_type: str = ""
    aggregate_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: CommandStatus = CommandStatus.PENDING
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Query:
    query_id: uuid.UUID = field(default_factory=uuid.uuid4)
    query_type: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QueryResult:
    query_id: uuid.UUID
    query_type: str
    data: Any
    execution_time_ms: float
    cached: bool = False
    error: str | None = None


class CommandBus:
    def __init__(self):
        self._handlers: dict[str, CommandHandler] = {}
        self._middleware: list[Callable] = []
        self._history: list[Command] = []

    def register(self, command_type: str, handler: CommandHandler):
        if command_type in self._handlers:
            logger.warning("handler_overridden", command_type=command_type)
        self._handlers[command_type] = handler
        logger.debug("handler_registered", command_type=command_type)

    def add_middleware(self, mw: Callable):
        self._middleware.append(mw)

    async def dispatch(self, command: Command) -> Any:
        command.status = CommandStatus.PROCESSING
        self._history.append(command)
        try:
            for mw in self._middleware:
                await mw(command)
            handler = self._handlers.get(command.command_type)
            if handler is None:
                raise ValueError(f"No handler for command: {command.command_type}")
            result = await handler(command)
            command.status = CommandStatus.COMPLETED
            command.result = result
            logger.info(
                "command_completed", type=command.command_type, id=str(command.command_id)[:8]
            )
            return result
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error = str(e)
            logger.error("command_failed", type=command.command_type, error=str(e))
            raise

    @property
    def history(self) -> list[Command]:
        return list(self._history)


class QueryBus:
    def __init__(self):
        self._handlers: dict[str, QueryHandler] = {}
        self._cache: dict[str, tuple[QueryResult, datetime]] = {}
        self._cache_ttl_seconds: float = 30.0

    def register(self, query_type: str, handler: QueryHandler):
        self._handlers[query_type] = handler

    async def ask(self, query: Query, use_cache: bool = True) -> QueryResult:
        import time

        cache_key = f"{query.query_type}:{hash(frozenset(query.parameters.items()))}"
        if use_cache and cache_key in self._cache:
            result, cached_at = self._cache[cache_key]
            if (datetime.now(timezone.utc) - cached_at).total_seconds() < self._cache_ttl_seconds:
                result.cached = True
                return result
        start = time.monotonic()
        try:
            handler = self._handlers.get(query.query_type)
            if handler is None:
                raise ValueError(f"No handler for query: {query.query_type}")
            data = await handler(query)
            elapsed = (time.monotonic() - start) * 1000
            result = QueryResult(
                query_id=query.query_id,
                query_type=query.query_type,
                data=data,
                execution_time_ms=elapsed,
            )
            if use_cache:
                self._cache[cache_key] = (result, datetime.now(timezone.utc))
            logger.debug("query_completed", type=query.query_type, time_ms=f"{elapsed:.1f}")
            return result
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(
                query_id=query.query_id,
                query_type=query.query_type,
                data=None,
                execution_time_ms=elapsed,
                error=str(e),
            )

    def invalidate_cache(self, query_type: str | None = None):
        if query_type:
            self._cache = {k: v for k, v in self._cache.items() if not k.startswith(query_type)}
        else:
            self._cache.clear()
        logger.info("cache_invalidated", query_type=query_type)


# F1 Domain Commands
class RaceCommands:
    @staticmethod
    def start_race(race_id: str) -> Command:
        return Command(
            command_type="race.start",
            aggregate_id=race_id,
            data={"race_id": race_id},
        )

    @staticmethod
    def reconstruct_session(session_id: str) -> Command:
        return Command(
            command_type="session.reconstruct",
            aggregate_id=session_id,
            data={"session_id": session_id},
        )

    @staticmethod
    def run_counterfactual(session_id: str, driver_id: str, scenario: str, params: dict) -> Command:
        return Command(
            command_type="counterfactual.run",
            aggregate_id=session_id,
            data={
                "session_id": session_id,
                "driver_id": driver_id,
                "scenario": scenario,
                "parameters": params,
            },
        )

    @staticmethod
    def optimize_strategy(session_id: str, driver_id: str, objective: str) -> Command:
        return Command(
            command_type="strategy.optimize",
            aggregate_id=f"{session_id}:{driver_id}",
            data={
                "session_id": session_id,
                "driver_id": driver_id,
                "objective": objective,
            },
        )


# F1 Domain Queries
class RaceQueries:
    @staticmethod
    def get_lap_times(session_id: str, driver_id: str) -> Query:
        return Query(
            query_type="lap_times.by_driver",
            parameters={"session_id": session_id, "driver_id": driver_id},
        )

    @staticmethod
    def get_position_history(session_id: str) -> Query:
        return Query(
            query_type="position.history",
            parameters={"session_id": session_id},
        )

    @staticmethod
    def get_strategy_tree(session_id: str, driver_id: str) -> Query:
        return Query(
            query_type="strategy.tree",
            parameters={"session_id": session_id, "driver_id": driver_id},
        )

    @staticmethod
    def get_overtake_analysis(session_id: str) -> Query:
        return Query(
            query_type="overtake.analysis",
            parameters={"session_id": session_id},
        )

    @staticmethod
    def get_tyre_strategy(session_id: str, driver_id: str) -> Query:
        return Query(
            query_type="tyre.strategy",
            parameters={"session_id": session_id, "driver_id": driver_id},
        )

    @staticmethod
    def predict_outcome(session_id: str, lap: int, model: str) -> Query:
        return Query(
            query_type="predict.outcome",
            parameters={"session_id": session_id, "lap": lap, "model": model},
        )


command_bus = CommandBus()
query_bus = QueryBus()

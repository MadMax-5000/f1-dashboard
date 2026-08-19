import asyncio
import structlog
import numpy as np
from datetime import datetime, timezone
from typing import Callable, Awaitable
from collections import defaultdict

from app.twin.engine.state import RaceState, DriverState
from app.core.config import settings

logger = structlog.get_logger()

TickCallback = Callable[[RaceState], Awaitable[None]]


class TwinSimulator:
    def __init__(self):
        self._state: RaceState | None = None
        self._running = False
        self._paused = False
        self._speed_multiplier: float = 1.0
        self._tick_rate: float = 60.0
        self._callbacks: list[TickCallback] = []
        self._history: list[RaceState] = []

    @property
    def state(self) -> RaceState | None:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._running

    def on_tick(self, callback: TickCallback):
        self._callbacks.append(callback)

    def init_from_session(
        self,
        session_id: str,
        total_laps: int,
        driver_ids: list[tuple[str, int]],
        track_length_km: float = 5.0,
    ):
        now = datetime.now(timezone.utc)
        self._state = RaceState(
            session_id=session_id,
            tick=0,
            timestamp=now,
            lap_number=0,
            total_laps=total_laps,
            race_phase="pre_race",
        )
        for i, (did, dnum) in enumerate(driver_ids):
            self._state.drivers[did] = DriverState(
                driver_id=did,
                driver_number=dnum,
                position=i + 1,
                lap_number=0,
                distance=0.0,
                speed=0.0,
                rpm=0.0,
                gear=1,
                throttle=0.0,
                brake=0.0,
                drs_active=False,
                x=0.0,
                y=0.0,
                z=0.0,
                tyre_compound="soft",
                tyre_age_laps=0,
                tyre_temperature=25.0,
                fuel_remaining=110.0,
                fuel_load=110.0,
                ers_energy=4.0,
                ers_deploy_mode="balanced",
                sector=1,
                in_pit=False,
                pit_stop_count=0,
                lap_time_accumulator=0.0,
                delta_to_leader=0.0,
                delta_to_next=0.0,
                delta_to_prev=0.0,
            )
            self._state.order.append(did)
        logger.info(
            "twin initialized",
            session_id=session_id,
            drivers=len(driver_ids),
            total_laps=total_laps,
        )

    def apply_telemetry_frame(
        self,
        driver_id: str,
        speed: float | None = None,
        rpm: float | None = None,
        gear: int | None = None,
        throttle: float | None = None,
        brake: float | None = None,
        drs: bool | None = None,
        x: float | None = None,
        y: float | None = None,
    ):
        if not self._state or driver_id not in self._state.drivers:
            return
        ds = self._state.drivers[driver_id]
        if speed is not None:
            ds.speed = speed
        if rpm is not None:
            ds.rpm = rpm
        if gear is not None:
            ds.gear = gear
        if throttle is not None:
            ds.throttle = throttle
        if brake is not None:
            ds.brake = brake
        if drs is not None:
            ds.drs_active = drs
        if x is not None:
            ds.x = x
        if y is not None:
            ds.y = y

    def update_positions(self, positions: dict[str, int]):
        if not self._state:
            return
        for did, pos in positions.items():
            if did in self._state.drivers:
                self._state.drivers[did].position = pos
        self._state.order = sorted(
            self._state.drivers.keys(),
            key=lambda d: self._state.drivers[d].position,
        )

    def update_weather(
        self,
        air_temp: float | None = None,
        track_temp: float | None = None,
        rainfall: bool | None = None,
        rain_intensity: float | None = None,
        wind_speed: float | None = None,
        track_grip: float | None = None,
    ):
        if not self._state:
            return
        if air_temp is not None:
            self._state.air_temperature = air_temp
        if track_temp is not None:
            self._state.track_temperature = track_temp
        if rainfall is not None:
            self._state.rainfall = rainfall
        if rain_intensity is not None:
            self._state.rain_intensity = rain_intensity
        if wind_speed is not None:
            self._state.wind_speed = wind_speed
        if track_grip is not None:
            self._state.track_grip = track_grip

    def set_safety_car(self, active: bool, sc_type: str | None = None):
        if not self._state:
            return
        self._state.safety_car_active = active
        self._state.safety_car_type = sc_type
        if active:
            self._state.vsc_active = sc_type == "vsc"

    def add_event(self, event_type: str, data: dict):
        if not self._state:
            return
        self._state.events.append(
            {
                "tick": self._state.tick,
                "lap": self._state.lap_number,
                "type": event_type,
                "data": data,
            }
        )

    async def _run_tick(self):
        if not self._state:
            return
        self._state.tick += 1
        for ds in self._state.drivers.values():
            if ds.is_retired:
                continue
            ds.distance += ds.speed * (1.0 / self._tick_rate) / 3.6
            if ds.speed > 0:
                ds.fuel_remaining = max(0, ds.fuel_remaining - 0.003 * (ds.speed / 300))
            ds.lap_time_accumulator += 1.0 / self._tick_rate
        self._state.timestamp = datetime.now(timezone.utc)

    def set_speed(self, multiplier: float):
        self._speed_multiplier = max(0.1, min(10.0, multiplier))

    async def run(self, target_ticks: int | None = None):
        self._running = True
        self._paused = False
        logger.info("twin simulation started")
        try:
            while self._running:
                if self._paused:
                    await asyncio.sleep(0.1)
                    continue
                await self._run_tick()
                self._history.append(self._state)
                for cb in self._callbacks:
                    await cb(self._state)
                if target_ticks and self._state.tick >= target_ticks:
                    break
                await asyncio.sleep(1.0 / (self._tick_rate * self._speed_multiplier))
        except asyncio.CancelledError:
            logger.info("twin simulation cancelled")
        finally:
            self._running = False
            logger.info("twin simulation stopped", ticks=self._state.tick if self._state else 0)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._running = False

    def get_history(self, start_tick: int = 0, end_tick: int | None = None) -> list[RaceState]:
        if end_tick is None:
            end_tick = len(self._history)
        return self._history[start_tick:end_tick]

    def fast_forward(self, ticks: int):
        for _ in range(ticks):
            if not self._running:
                break
            self._run_tick()

import fastf1
import pandas as pd
import structlog
from typing import AsyncGenerator
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings

logger = structlog.get_logger()

CACHE_DIR = settings.data_dir / "fastf1_cache"


class FastF1Source:
    def __init__(self):
        fastf1.Cache.enable_cache(str(CACHE_DIR))
        logger.info("fastf1 cache enabled", path=str(CACHE_DIR))

    async def get_session(self, year: int, gp: str, session_type: str) -> fastf1.core.Session:
        return fastf1.get_session(year, gp, session_type)

    async def load_session(self, year: int, gp: str, session_type: str) -> fastf1.core.Session:
        session = await self.get_session(year, gp, session_type)
        session.load(
            laps=True,
            telemetry=True,
            weather=True,
            messages=True,
        )
        logger.info("session loaded", year=year, gp=gp, session=session_type)
        return session

    async def extract_laps(self, session: fastf1.core.Session) -> pd.DataFrame:
        laps = session.laps
        if laps is None or laps.empty:
            return pd.DataFrame()
        df = laps.copy()
        df["session_id"] = str(session.session_info.get("SessionName", ""))
        return df

    async def extract_telemetry(self, session: fastf1.core.Session, driver: str) -> pd.DataFrame:
        laps = session.laps.pick_driver(driver)
        if laps is None or laps.empty:
            return pd.DataFrame()
        telemetry = laps.get_telemetry()
        return telemetry

    async def extract_weather(self, session: fastf1.core.Session) -> pd.DataFrame:
        weather = session.weather_data
        if weather is None or weather.empty:
            return pd.DataFrame()
        return weather

    async def extract_positions(self, session: fastf1.core.Session) -> dict[str, pd.DataFrame]:
        result = {}
        for driver in session.drivers:
            try:
                pos = session.pos_data[driver]
                if pos is not None and not pos.empty:
                    result[driver] = pos
            except (KeyError, AttributeError):
                continue
        return result

    async def extract_car_data(self, session: fastf1.core.Session, driver: str) -> pd.DataFrame:
        car_data = session.car_data[driver]
        if car_data is None or car_data.empty:
            return pd.DataFrame()
        return car_data

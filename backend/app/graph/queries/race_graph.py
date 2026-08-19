import structlog
from typing import Any

logger = structlog.get_logger()


class RaceGraphQueries:
    def __init__(self, driver):
        self._driver = driver

    async def create_race_graph(self, race_id: str, session_id: str):
        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (r:Race {id: $race_id})
                SET r.session_id = $session_id
                """,
                race_id=race_id,
                session_id=session_id,
            )

    async def add_driver_node(self, driver_id: str, name: str, team: str):
        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (d:Driver {id: $driver_id})
                SET d.name = $name, d.team = $team
                """,
                driver_id=driver_id,
                name=name,
                team=team,
            )

    async def record_overtake(
        self,
        race_id: str,
        overtaking_driver: str,
        overtaken_driver: str,
        lap: int,
        location: str,
    ):
        async with self._driver.session() as session:
            await session.run(
                """
                MATCH (r:Race {id: $race_id})
                MATCH (a:Driver {id: $overtaking})
                MATCH (b:Driver {id: $overtaken})
                MERGE (a)-[o:OVERTAKES {
                    race_id: $race_id,
                    lap: $lap,
                    location: $location
                }]->(b)
                SET o.count = coalesce(o.count, 0) + 1
                """,
                race_id=race_id,
                overtaking=overtaking_driver,
                overtaken=overtaken_driver,
                lap=lap,
                location=location,
            )

    async def get_headtohead(self, driver_a: str, driver_b: str) -> dict[str, Any]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (a:Driver {id: $a})
                MATCH (b:Driver {id: $b})
                OPTIONAL MATCH (a)-[o:OVERTAKES]->(b)
                OPTIONAL MATCH (b)-[o2:OVERTAKES]->(a)
                RETURN
                    count(o) AS a_overtakes_b,
                    count(o2) AS b_overtakes_a
                """,
                a=driver_a,
                b=driver_b,
            )
            record = await result.single()
            return {
                "driver_a_overtakes_b": record["a_overtakes_b"] if record else 0,
                "driver_b_overtakes_a": record["b_overtakes_a"] if record else 0,
            }

    async def get_driver_race_path(self, race_id: str, driver_id: str) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (d:Driver {id: $driver_id})
                MATCH (d)-[o:OVERTAKES {race_id: $race_id}]->()
                RETURN o.lap AS lap, o.location AS location,
                       o.count AS overtakes
                ORDER BY o.lap ASC
                """,
                driver_id=driver_id,
                race_id=race_id,
            )
            return [dict(record) async for record in result]

    async def get_overtake_hotspots(self, race_id: str) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH ()-[o:OVERTAKES {race_id: $race_id}]->()
                RETURN o.location AS location, count(o) AS total,
                       count(DISTINCT o.lap) AS laps_involved
                ORDER BY total DESC
                """,
                race_id=race_id,
            )
            return [dict(record) async for record in result]

    async def get_strategy_similarity(self, session_id: str, driver_id: str) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (d:Driver {id: $driver_id})
                MATCH (d)-[:PITS {session_id: $session_id}]->(p:PitStop)
                WITH d, collect(p.lap) AS target_stops
                MATCH (other:Driver)-[:PITS {session_id: $session_id}]->(op:PitStop)
                WHERE other.id <> $driver_id
                WITH other, collect(op.lap) AS other_stops,
                     target_stops
                RETURN other.id AS driver_id,
                       gds.similarity.jaccard(
                           target_stops, other_stops
                       ) AS strategy_similarity
                ORDER BY strategy_similarity DESC
                """,
                driver_id=driver_id,
                session_id=session_id,
            )
            return [dict(record) async for record in result]

    async def get_driver_network(self, race_id: str) -> dict:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (a:Driver)-[o:OVERTAKES {race_id: $race_id}]->(b:Driver)
                RETURN a.id AS source, b.id AS target,
                       count(o) AS weight, collect(o.location) AS locations
                """,
                race_id=race_id,
            )
            nodes = set()
            links = []
            async for record in result:
                nodes.add(record["source"])
                nodes.add(record["target"])
                links.append(
                    {
                        "source": record["source"],
                        "target": record["target"],
                        "weight": record["weight"],
                        "locations": record["locations"],
                    }
                )
            return {
                "nodes": [{"id": n} for n in nodes],
                "links": links,
                "total_overtakes": sum(l["weight"] for l in links),
            }

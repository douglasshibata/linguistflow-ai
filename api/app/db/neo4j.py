"""Async Neo4j client (official driver 5.x) with parameterized Cypher queries."""

from __future__ import annotations

from typing import Any
from neo4j import AsyncGraphDatabase


class Neo4jStore:
    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = AsyncGraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_pool_size=50,
            connection_acquisition_timeout=30,
        )

    @property
    def driver(self):
        return self._driver

    async def verify_connectivity(self) -> bool:
        await self._driver.verify_connectivity()
        return True

    async def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        database: str | None = None,
    ) -> list[dict[str, Any]]:
        """Executes Cypher query using parameter maps to strictly prevent Cypher injection."""
        async with self._driver.session(database=database) as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def close(self) -> None:
        await self._driver.close()

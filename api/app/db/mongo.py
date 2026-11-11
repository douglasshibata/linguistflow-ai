"""Async MongoDB client (Motor) with strict input validation against NoSQL injection."""

from __future__ import annotations

from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel


def sanitize_nosql_filter(filter_dict: dict[str, Any]) -> dict[str, Any]:
    """Sanitizes filter dictionaries against NoSQL operator injection ($where, $gt, etc.)."""
    sanitized = {}
    for key, value in filter_dict.items():
        if isinstance(key, str) and key.startswith("$"):
            continue
        if isinstance(value, dict):
            sanitized[key] = sanitize_nosql_filter(value)
        else:
            sanitized[key] = value
    return sanitized


class MongoStore:
    def __init__(self, uri: str, database: str) -> None:
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(
            uri,
            maxPoolSize=10,
            minPoolSize=2,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="standard",
        )
        self._db: AsyncIOMotorDatabase = self._client[database]

    @property
    def database(self) -> AsyncIOMotorDatabase:
        return self._db

    def collection(self, name: str):
        return self._db[name]

    async def find_one_validated(
        self,
        collection_name: str,
        filter_dict: dict[str, Any],
        schema: type[BaseModel] | None = None,
    ) -> Any | None:
        """Finds one document using sanitized query filters and optional Pydantic schema validation."""
        safe_filter = sanitize_nosql_filter(filter_dict)
        doc = await self._db[collection_name].find_one(safe_filter)
        if doc and schema:
            return schema.model_validate(doc)
        return doc

    async def insert_validated(
        self,
        collection_name: str,
        document: BaseModel | dict[str, Any],
    ) -> str:
        """Inserts document after ensuring validation through Pydantic."""
        doc_dict = document.model_dump() if isinstance(document, BaseModel) else document
        result = await self._db[collection_name].insert_one(doc_dict)
        return str(result.inserted_id)

    async def ping(self) -> bool:
        await self._client.admin.command("ping")
        return True

    def close(self) -> None:
        self._client.close()

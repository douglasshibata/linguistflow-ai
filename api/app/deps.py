"""FastAPI dependency providers backed by app.state populated in lifespan."""

from __future__ import annotations

from fastapi import Request

from app.config import Settings, get_settings
from app.db.mongo import MongoStore
from app.db.neo4j import Neo4jStore
from app.llm.router import LlmRouter


def get_llm_router(request: Request) -> LlmRouter:
    return request.app.state.llm


def get_mongo(request: Request) -> MongoStore:
    return request.app.state.mongo


def get_neo4j(request: Request) -> Neo4jStore:
    return request.app.state.neo4j


def get_whisper_model(request: Request):
    return request.app.state.whisper


def get_mongo_collection(name: str):
    def _provider(request: Request):
        return request.app.state.mongo.collection(name)

    return _provider


__all__ = [
    "Settings",
    "get_llm_router",
    "get_mongo",
    "get_mongo_collection",
    "get_neo4j",
    "get_settings",
    "get_whisper_model",
]

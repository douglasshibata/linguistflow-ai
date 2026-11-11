from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse

from app.deps import get_llm_router
from app.lessons.schemas import (
    CreateLessonRequest,
    LessonQuery,
    LessonResponseSchema,
    ProvidersResponse,
)
from app.lessons.service import build_prompt
from app.llm.router import LlmError, LlmRouter

router = APIRouter(tags=["lessons"])


@router.post(
    "/api/v1/lessons",
    response_model=LessonResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create personalized lesson via POST",
)
async def create_personalized_lesson(
    request: Request,  # noqa: ARG001 — required by slowapi limiter
    payload: CreateLessonRequest,
    llm: LlmRouter = Depends(get_llm_router),
) -> LessonResponseSchema:
    prompt = build_prompt(payload.topic, payload.hobby, payload.target_language)
    try:
        content = await llm.generate(payload.provider, payload.model, prompt)
    except LlmError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Parse JSON if returned by structured model or fallback to schema format
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return LessonResponseSchema.model_validate(data)
    except Exception:
        pass

    return LessonResponseSchema(
        title=f"Lesson: {payload.topic}",
        target_language=payload.target_language,
        difficulty_level="Adaptive",
        vocabulary_focus=[payload.topic, payload.hobby],
        raw_content=content,
    )


@router.get("/api/lesson", response_class=PlainTextResponse)
async def generate_lesson_legacy(
    request: Request,  # noqa: ARG001 — required by slowapi limiter
    query: LessonQuery = Depends(),
    llm: LlmRouter = Depends(get_llm_router),
) -> str:
    prompt = build_prompt(query.topic, query.hobby, query.target_language)
    try:
        return await llm.generate(query.provider, query.model, prompt)
    except LlmError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/lesson/providers", response_model=ProvidersResponse)
@router.get("/api/v1/lessons/providers", response_model=ProvidersResponse)
async def list_providers(
    llm: LlmRouter = Depends(get_llm_router),
) -> ProvidersResponse:
    return ProvidersResponse(
        defaultProvider=llm.default_provider,
        providers=llm.list_providers(),
    )

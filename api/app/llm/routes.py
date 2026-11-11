from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_llm_router
from app.llm.router import LlmError, LlmRouter
from app.llm.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/llm", tags=["llm"])

@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    llm: LlmRouter = Depends(get_llm_router),
) -> ChatResponse:
    try:
        messages = [msg.model_dump() for msg in payload.messages]
        content = await llm.chat(payload.provider, payload.model, messages)
        return ChatResponse(content=content)
    except LlmError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

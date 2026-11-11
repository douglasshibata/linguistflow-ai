from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.deps import get_llm_router
from app.llm.router import LlmError, LlmRouter

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    provider: str | None = None
    model: str | None = None

@router.post("")
async def chat(
    request: Request,
    body: ChatRequest,
    llm: LlmRouter = Depends(get_llm_router),
) -> dict:
    # Concatenate history to provide context if there are multiple messages
    # LiteLLM generate() actually handles messages list, but our LlmRouter wraps it.
    # Let's see if we can pass the whole list.

    # We should update LlmRouter to handle messages instead of just prompt string
    # to better support chat history.

    messages = [m.model_dump() for m in body.messages]
    try:
        content = await llm.generate(body.provider, body.model, messages)
        return {"message": {"role": "assistant", "content": content}}
    except LlmError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

ProviderName = Annotated[
    str,
    StringConstraints(min_length=1, max_length=20, pattern=r"^[a-z]+$"),
]
ModelName = Annotated[
    str,
    StringConstraints(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9._\-:/]+$"),
]

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    provider: ProviderName | None = None
    model: ModelName | None = None
    stream: bool = False

class ChatResponse(BaseModel):
    content: str

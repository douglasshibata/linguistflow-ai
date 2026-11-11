from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

StudentId = Annotated[
    str,
    StringConstraints(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_\-]+$"),
]


class SpeechAnalysis(BaseModel):
    transcription: str
    pronunciation_score: float = Field(..., ge=0.0, le=1.0)
    stress_level: str = Field(..., pattern=r"^(High|Normal|Low)$")
    detected_language: str | None = None

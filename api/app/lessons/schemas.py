from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class CreateLessonRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_id: str = Field(
        ...,
        alias="studentId",
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_\-]+$",
    )
    topic: str = Field(..., min_length=1, max_length=100)
    hobby: str = Field(..., min_length=1, max_length=100)
    target_language: str = Field(
        default="English",
        alias="language",
        min_length=1,
        max_length=100,
    )
    provider: str | None = Field(default=None, max_length=20, pattern=r"^[a-z]+$")
    model: str | None = Field(default=None, max_length=80, pattern=r"^[a-zA-Z0-9._\-:/]+$")


class LessonDialogue(BaseModel):
    speaker: str | None = None
    text: str
    translation: str | None = None


class LessonResponseSchema(BaseModel):
    title: str = "Adaptive Language Lesson"
    target_language: str = "English"
    difficulty_level: str = "Intermediate"
    vocabulary_focus: list[str] = Field(default_factory=list)
    dialogue_script: list[LessonDialogue | dict] = Field(default_factory=list)
    cultural_tip: str = ""
    raw_content: str | None = None


StudentId = Annotated[
    str,
    StringConstraints(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_\-]+$"),
]
ShortText = Annotated[
    str,
    StringConstraints(min_length=1, max_length=100),
]
ProviderName = Annotated[
    str,
    StringConstraints(min_length=1, max_length=20, pattern=r"^[a-z]+$"),
]
ModelName = Annotated[
    str,
    StringConstraints(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9._\-:/]+$"),
]


class LessonQuery(BaseModel):
    studentId: StudentId
    topic: ShortText
    hobby: ShortText
    target_language: ShortText = Field("English", alias="language")
    provider: ProviderName | None = None
    model: ModelName | None = None


class ProvidersResponse(BaseModel):
    defaultProvider: str = Field(...)
    providers: dict[str, list[str]] = Field(default_factory=dict)

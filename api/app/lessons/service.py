"""Lesson generation: sanitize user input with multilingual guardrails, build prompt, delegate to LlmRouter."""

from __future__ import annotations

from app.core.guardrails import sanitize_and_validate_prompt_input

_MAX_LEN = 100

_PROMPT_TEMPLATE = (
    "You are the LinguistFlow AI Tutor.\n"
    "Generate a short conversation scenario for a student learning {language}.\n"
    "The lesson topic is: {topic}.\n"
    "The student is interested in: {hobby}.\n"
    "Format the response as follows:\n"
    "1. SCENARIO: A brief description of the context.\n"
    "2. DIALOGUE: 3 sentences in {language} with English translations.\n"
    "3. GRAMMAR: A brief explanation of a grammar point found in the dialogue.\n"
    "Ensure the tone is helpful and encouraging."
)


def sanitize(text: str | None) -> str:
    """Safely sanitizes input preserving all international alphabets and accents."""
    if not text:
        return ""
    # Strip HTML tags or script injection characters while preserving international characters
    cleaned = text[:_MAX_LEN].replace("<", "").replace(">", "").replace(";", "")
    return sanitize_and_validate_prompt_input(cleaned, max_chars=_MAX_LEN)


def build_prompt(topic: str, hobby: str, language: str) -> str:
    return _PROMPT_TEMPLATE.format(
        topic=sanitize(topic),
        hobby=sanitize(hobby),
        language=sanitize(language),
    )

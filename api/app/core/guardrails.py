"""Multilingual semantic guardrails.

Normalizes input preserving international alphabets (Latin, Cyrillic, CJK, Arabic, etc.)
while blocking semantic prompt injection and structural jailbreaks.
"""

from __future__ import annotations

import re
import unicodedata

from fastapi import HTTPException, status

JAILBREAK_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|above)\s+instructions\b"),
    re.compile(r"(?i)\bsystem\s+prompt\s+override\b"),
    re.compile(r"(?i)\byou\s+are\s+now\s+(unfiltered|dan|developer\s+mode)\b"),
    re.compile(r"(?i)\bdo\s+anything\s+now\b"),
    re.compile(r"(?i)\breveal\s+(the\s+)?(system\s+prompt|api\s+key)\b"),
]


def sanitize_and_validate_prompt_input(user_text: str | None, max_chars: int = 500) -> str:
    """Normalizes input preserving international alphabets while neutralizing prompt injections."""
    if not user_text or not user_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O parâmetro não pode ser vazio.",
        )

    # 1. Unicode NFKC normalization to prevent homoglyph bypass
    normalized = unicodedata.normalize("NFKC", user_text).strip()

    if len(normalized) > max_chars:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entrada excede o limite máximo permitido de {max_chars} caracteres.",
        )

    # 2. Jailbreak pattern detection
    for pattern in JAILBREAK_PATTERNS:
        if pattern.search(normalized):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Entrada bloqueada por violação das políticas de segurança institucional.",
            )

    return normalized

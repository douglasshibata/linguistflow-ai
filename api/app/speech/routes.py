from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pymongo import UpdateOne

from app.config import Settings, get_settings
from app.deps import get_mongo_collection, get_whisper_model
from app.speech.schemas import SpeechAnalysis, StudentId
from app.speech.service import (
    analyze_bytes_sync,
    validate_audio_binary,
    words_from_transcription,
)

router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/analyze", response_model=SpeechAnalysis)
async def analyze(
    request: Request,  # noqa: ARG001 — required by slowapi limiter
    file: UploadFile = File(...),
    student_id: StudentId = Form(...),
    expected_text: str | None = Form(default=None, max_length=500),  # noqa: ARG001
    settings: Settings = Depends(get_settings),
    whisper_model=Depends(get_whisper_model),
    heatmap=Depends(get_mongo_collection("heatmap")),
) -> SpeechAnalysis:
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="empty file")

    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="file too large")

    # Magic byte and format validation
    audio_format = validate_audio_binary(contents)
    suffix = f".{audio_format}"

    # Asynchronous offloading to avoid blocking FastAPI event loop
    try:
        analysis = await asyncio.to_thread(
            analyze_bytes_sync, whisper_model, contents, suffix=suffix
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"speech analysis failed: {str(exc)}") from exc

    words = words_from_transcription(analysis["transcription"])
    if words:
        ops = [
            UpdateOne(
                {"student_id": student_id, "word": word},
                {
                    "$inc": {"count": 1},
                    "$set": {
                        "last_stress_score": float(
                            0.6 if analysis["stress_level"] == "High" else 0.3
                        )
                    },
                },
                upsert=True,
            )
            for word in words
        ]
        try:
            await heatmap.bulk_write(ops, ordered=False)
        except Exception:  # noqa: BLE001 — non-fatal
            pass

    return SpeechAnalysis(
        transcription=analysis["transcription"],
        pronunciation_score=analysis["pronunciation_score"],
        stress_level=analysis["stress_level"],
        detected_language=analysis["detected_language"],
    )

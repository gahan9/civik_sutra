from __future__ import annotations

from typing import Any

from fastapi import Depends, APIRouter

from src.models.chat import (
    ChatRequest,
    ChatResponse,
    TranslateRequest,
    TranslateResponse,
)
from src.services.chat_service import ChatService
from src.data.election_timeline import ELECTION_EVENTS
from src.services.translation_service import TranslationService

router = APIRouter(prefix="/assistant", tags=["assistant"])

_translation_service_singleton: TranslationService | None = None


def get_chat_service() -> ChatService:
    """Provide a ChatService instance to FastAPI dependency injection."""
    return ChatService()


def get_translation_service() -> TranslationService:
    """Provide a process-wide TranslationService for FastAPI DI.

    A singleton keeps the LRU cache warm across requests.
    """
    global _translation_service_singleton
    if _translation_service_singleton is None:
        _translation_service_singleton = TranslationService()
    return _translation_service_singleton


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Process a single chat turn through the AI election coach."""
    location = request.location.model_dump() if request.location else None
    return await service.chat(
        message=request.message,
        session_id=request.session_id,
        language=request.language,
        location=location,
    )


@router.get("/questions")
async def quick_questions(
    language: str = "en",
    service: ChatService = Depends(get_chat_service),
) -> dict[str, list[str]]:
    """Return the localised list of suggested starter questions."""
    return {"questions": service.get_quick_questions(language)}


@router.get("/timeline")
async def election_timeline(stage: str | None = None) -> dict[str, Any]:
    """Return the curated election timeline for the voter journey UI.

    The same dataset powers the Gemini ``get_election_timeline`` tool and
    the calendar deep-link panel on the frontend, so the AI coach and the
    UI never disagree.
    """
    events = ELECTION_EVENTS
    if stage:
        normalised = stage.strip().lower()
        events = [e for e in events if normalised in e["stage"].lower()]
    return {"events": events, "count": len(events)}


@router.post("/translate", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    service: TranslationService = Depends(get_translation_service),
) -> TranslateResponse:
    """Translate dynamic content between supported locales.

    Used for content the i18n catalog cannot pre-translate — for example
    AI-generated chat answers, manifesto comparison narratives, or
    candidate background paragraphs.
    """
    translated = service.translate(
        request.text,
        target_language=request.target_language,
        source_language=request.source_language,
    )
    return TranslateResponse(
        text=translated,
        target_language=request.target_language,
        source_language=request.source_language,
    )

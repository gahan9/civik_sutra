from __future__ import annotations

from fastapi import APIRouter, Depends

from src.models.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

router = APIRouter(prefix="/assistant", tags=["assistant"])


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await service.chat(
        message=request.message,
        session_id=request.session_id,
        language=request.language,
    )


@router.get("/questions")
async def quick_questions(
    language: str = "en",
    service: ChatService = Depends(get_chat_service),
) -> dict[str, list[str]]:
    return {"questions": service.get_quick_questions(language)}

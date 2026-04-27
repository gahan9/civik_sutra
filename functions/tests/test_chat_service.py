from __future__ import annotations

import pytest

from src.models.chat import ChatResponse
from src.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_chat_service_fallback_response() -> None:
    service = ChatService(gemini_api_key=None)
    response = await service.chat("Hello", "session_123", "en")

    assert isinstance(response, ChatResponse)
    assert response.session_id == "session_123"
    assert "I'm unable to process this question right now" in response.response


@pytest.mark.asyncio
async def test_chat_service_fallback_response_hindi() -> None:
    service = ChatService(gemini_api_key=None)
    response = await service.chat("Hello", "session_123", "hi")

    assert "\u092e\u0948\u0902 \u0907\u0938 \u0938\u092e\u092f" in response.response


def test_get_quick_questions() -> None:
    service = ChatService(gemini_api_key=None)
    en_qs = service.get_quick_questions("en")
    assert len(en_qs) > 0
    assert "What documents do I need to carry for voting?" in en_qs

    hi_qs = service.get_quick_questions("hi")
    assert len(hi_qs) > 0


def test_extract_citations() -> None:
    service = ChatService(gemini_api_key=None)
    text = "According to the ECI, you must carry an EPIC card."
    citations = service._extract_citations(text)

    assert len(citations) == 1
    assert citations[0].source == "Election Commission of India"


def test_detect_tool_intents() -> None:
    service = ChatService(gemini_api_key=None)

    # Test booth intent
    booth_calls = service._detect_tool_intents("Where is my polling booth?")
    assert len(booth_calls) == 1
    assert booth_calls[0].tool_name == "booth_finder"

    # Test candidate intent
    cand_calls = service._detect_tool_intents("Compare candidates in South Delhi")
    assert len(cand_calls) == 1
    assert cand_calls[0].tool_name == "candidate_search"

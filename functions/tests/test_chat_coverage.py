"""Additional chat_service tests for coverage boost.

Targets session TTL, history limits, tool dispatchers, and language
parameter handling.
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.models.chat import ChatResponse
from src.services.chat_service import (
    ChatService,
    MAX_HISTORY_MESSAGES,
    SESSION_TTL_SECONDS,
    _generic_fallback,
    _user_part,
    _model_part,
)
from src.services.vertex_service import VertexFAQService


@pytest.mark.asyncio
async def test_session_history_expires_after_ttl() -> None:
    service = ChatService(gemini_api_key=None)
    service._sessions["old"] = [_user_part("hi"), _model_part("hello")]
    service._session_timestamps["old"] = time.time() - SESSION_TTL_SECONDS - 1

    history = service._load_history("old")
    assert history == []


@pytest.mark.asyncio
async def test_session_history_truncated_to_max() -> None:
    service = ChatService(gemini_api_key=None)
    big_history = [_user_part(f"msg-{i}") for i in range(30)]
    service._sessions["full"] = big_history
    service._session_timestamps["full"] = time.time()

    loaded = service._load_history("full")
    assert len(loaded) == MAX_HISTORY_MESSAGES


def test_generic_fallback_en() -> None:
    text = _generic_fallback("en")
    assert "election" in text.lower() or "civic" in text.lower() or "voter" in text.lower()


def test_generic_fallback_hi() -> None:
    text = _generic_fallback("hi")
    assert text != ""


def test_generic_fallback_unknown_lang_uses_en() -> None:
    text = _generic_fallback("zz")
    en_text = _generic_fallback("en")
    assert text == en_text


def test_user_part_structure() -> None:
    part = _user_part("Hello world")
    assert part["role"] == "user"
    assert part["parts"][0]["text"] == "Hello world"


def test_model_part_structure() -> None:
    part = _model_part("Bot reply")
    assert part["role"] == "model"
    assert part["parts"][0]["text"] == "Bot reply"


@pytest.mark.asyncio
async def test_dispatch_tool_faq_search() -> None:
    vertex = VertexFAQService(api_key=None)
    service = ChatService(gemini_api_key=None, vertex_service=vertex)
    result = await service._dispatch_tool(
        "lookup_election_faq",
        {"query": "What is an EVM?"},
    )
    assert "results" in result or "match_count" in result


@pytest.mark.asyncio
async def test_dispatch_tool_timeline() -> None:
    service = ChatService(gemini_api_key=None)
    result = await service._dispatch_tool(
        "get_election_timeline",
        {"stage": "Polling"},
    )
    assert "events" in result or "count" in result


@pytest.mark.asyncio
async def test_dispatch_tool_polling_location() -> None:
    service = ChatService(gemini_api_key=None)
    result = await service._dispatch_tool(
        "find_polling_location",
        {"lat": 28.6, "lng": 77.2},
    )
    assert "booths" in result or "error" not in result


@pytest.mark.asyncio
async def test_dispatch_tool_candidate_search() -> None:
    service = ChatService(gemini_api_key=None)
    result = await service._dispatch_tool(
        "search_candidates",
        {"query": "South Delhi"},
    )
    assert "candidates" in result


@pytest.mark.asyncio
async def test_chat_with_location_parameter() -> None:
    service = ChatService(gemini_api_key=None)
    response = await service.chat(
        "Where is my polling booth?",
        "session_loc",
        "en",
        location={"lat": 28.6139, "lng": 77.2090},
    )
    assert isinstance(response, ChatResponse)
    assert response.response


@pytest.mark.asyncio
async def test_chat_in_tamil_still_responds() -> None:
    service = ChatService(gemini_api_key=None)
    response = await service.chat(
        "What is NOTA?",
        "session_ta",
        "ta",
    )
    assert response.response != ""


@pytest.mark.asyncio
async def test_quick_questions_unknown_language() -> None:
    service = ChatService(gemini_api_key=None)
    qs = service.get_quick_questions("xx")
    en_qs = service.get_quick_questions("en")
    assert qs == en_qs

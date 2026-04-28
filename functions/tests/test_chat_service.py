from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.models.chat import ChatResponse
from src.services.chat_service import (
    SYSTEM_PROMPT,
    ChatService,
    _split_response,
    _dedupe_citations,
    _summarise_result,
    _extract_citations_from_text,
)
from src.models.chat import SourceCitation
from src.services.vertex_service import VertexFAQService


@pytest.mark.asyncio
async def test_chat_service_empty_message_returns_fallback() -> None:
    """Whitespace-only messages after sanitisation yield generic fallback, no crash."""
    vertex = VertexFAQService(api_key=None)
    service = ChatService(gemini_api_key=None, vertex_service=vertex)
    response = await service.chat("   \t  ", "session_ws", "en")
    assert response.session_id == "session_ws"
    assert response.citations == []
    assert response.response


@pytest.mark.asyncio
async def test_chat_service_falls_back_when_gemini_disabled() -> None:
    """Without an API key the coach must still produce a usable answer."""
    vertex = VertexFAQService(api_key=None)
    service = ChatService(gemini_api_key=None, vertex_service=vertex)
    response = await service.chat(
        "What documents do I need to vote?", "session_basic", "en"
    )

    assert isinstance(response, ChatResponse)
    assert response.session_id == "session_basic"
    assert response.response


@pytest.mark.asyncio
async def test_chat_service_uses_faq_fallback() -> None:
    """When Gemini is offline the coach should still surface a real FAQ answer."""
    vertex = VertexFAQService(api_key=None)
    service = ChatService(gemini_api_key=None, vertex_service=vertex)

    response = await service.chat(
        "What is NOTA and how do I use it?", "session_nota", "en"
    )

    assert "NOTA" in response.response
    assert response.tool_calls
    assert response.tool_calls[0].tool_name == "lookup_election_faq"


@pytest.mark.asyncio
async def test_chat_service_fallback_response_hindi() -> None:
    """Hindi callers receive a Hindi safety net when nothing else matches."""
    vertex = VertexFAQService(api_key=None)
    service = ChatService(gemini_api_key=None, vertex_service=vertex)

    response = await service.chat("xyz unknown topic", "session_hindi", "hi")
    assert response.response


def test_system_prompt_includes_neutral_and_hedge_rules() -> None:
    """Guardrails must cover vote recommendations and state-level variance."""
    lowered = SYSTEM_PROMPT.lower()
    assert "vote" in lowered and "recommend" in lowered
    assert "state" in lowered or "ceo" in lowered


def test_get_quick_questions() -> None:
    service = ChatService(gemini_api_key=None)
    en_qs = service.get_quick_questions("en")
    assert "What documents do I need to carry for voting?" in en_qs

    hi_qs = service.get_quick_questions("hi")
    assert hi_qs and isinstance(hi_qs[0], str)


def test_extract_citations_from_text() -> None:
    citations = _extract_citations_from_text(
        "According to the ECI, carry an EPIC card."
    )
    assert any(c.source == "Election Commission of India" for c in citations)


def test_dedupe_citations_removes_duplicates() -> None:
    raw = [
        SourceCitation(source="ECI", url="https://eci.gov.in"),
        SourceCitation(source="ECI", url="https://eci.gov.in"),
        SourceCitation(source="NVSP", url="https://nvsp.in"),
    ]
    deduped = _dedupe_citations(raw)
    assert len(deduped) == 2


def test_split_response_isolates_text_and_function_calls() -> None:
    payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Calling tool…"},
                        {
                            "functionCall": {
                                "name": "lookup_election_faq",
                                "args": {"query": "NOTA"},
                            }
                        },
                    ]
                }
            }
        ]
    }
    text, calls = _split_response(payload)
    assert text == "Calling tool…"
    assert len(calls) == 1
    assert calls[0]["functionCall"]["name"] == "lookup_election_faq"


def test_summarise_result_branches() -> None:
    assert _summarise_result(
        "check_voter_eligibility", {"eligible": True}
    ) == "eligible=True"
    assert (
        _summarise_result("lookup_election_faq", {"match_count": 2})
        == "matches=2"
    )
    assert _summarise_result(
        "find_polling_location", {"booths": [{}, {}]}
    ) == "booths=2"
    assert _summarise_result(
        "get_election_timeline", {"count": 7}
    ) == "events=7"
    assert _summarise_result(
        "search_candidates", {"candidates": [1]}
    ) == "candidates=1"
    assert "boom" in _summarise_result("anything", {"error": "boom"})


@pytest.mark.asyncio
async def test_dispatch_tool_eligibility_path() -> None:
    service = ChatService(gemini_api_key=None)
    result = await service._dispatch_tool(
        "check_voter_eligibility",
        {"age": 21, "citizenship": "indian", "residence": "resident"},
    )
    assert result["eligible"] is True
    assert "next_step" in result


@pytest.mark.asyncio
async def test_dispatch_tool_unknown_returns_error() -> None:
    service = ChatService(gemini_api_key=None)
    result = await service._dispatch_tool("nonexistent_tool", {})
    assert "error" in result


@pytest.mark.asyncio
async def test_function_calling_loop_executes_tool(monkeypatch: Any) -> None:
    """Verify the loop executes a function call, then returns the natural reply."""
    service = ChatService(gemini_api_key="fake-key")

    responses = iter(
        [
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "functionCall": {
                                        "name": "check_voter_eligibility",
                                        "args": {
                                            "age": 19,
                                            "citizenship": "indian",
                                        },
                                    }
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": "You are eligible to vote."}
                            ]
                        }
                    }
                ]
            },
        ]
    )

    async def fake_call(_self: Any, _system: str, _history: list[Any]) -> dict[str, Any]:
        return next(responses)

    monkeypatch.setattr(ChatService, "_call_gemini", fake_call)

    response = await service.chat(
        "Am I eligible at 19?", "session_loop", "en"
    )
    assert "eligible" in response.response.lower()
    assert any(
        tc.tool_name == "check_voter_eligibility" for tc in response.tool_calls
    )


@pytest.mark.asyncio
async def test_function_calling_loop_handles_empty_response(
    monkeypatch: Any,
) -> None:
    """If Gemini returns no content the coach must use the FAQ fallback."""
    service = ChatService(gemini_api_key="fake-key")

    async def fake_call(_self: Any, _system: str, _history: list[Any]) -> None:
        return None

    monkeypatch.setattr(ChatService, "_call_gemini", fake_call)

    fake_search = AsyncMock(return_value=[
        {
            "id": "voting-nota",
            "answer": "NOTA stands for None Of The Above.",
            "source": "ECI",
            "source_url": "https://eci.gov.in",
        }
    ])
    monkeypatch.setattr(service._vertex_service, "search", fake_search)

    response = await service.chat("What is NOTA?", "session_empty", "en")
    assert "NOTA" in response.response
    assert response.tool_calls[0].tool_name == "lookup_election_faq"

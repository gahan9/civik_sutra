from __future__ import annotations

import pytest

from src.services.vertex_service import (
    VertexFAQService,
    _tokenise,
    _cosine_similarity,
)


def test_cosine_similarity_basic_cases() -> None:
    assert _cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert _cosine_similarity([], [1.0]) == 0.0
    assert _cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_tokenise_strips_punctuation_and_lowercases() -> None:
    tokens = _tokenise("EVM, VVPAT and NOTA?!")
    assert "evm" in tokens
    assert "vvpat" in tokens
    assert "nota" in tokens


@pytest.mark.asyncio
async def test_search_returns_empty_for_empty_query() -> None:
    service = VertexFAQService(api_key=None)
    result = await service.search("")
    assert result == []


@pytest.mark.asyncio
async def test_search_keyword_fallback_finds_known_topic() -> None:
    service = VertexFAQService(api_key=None)
    result = await service.search("How do EVM machines work?")
    assert result, "Keyword fallback should return at least one match"
    assert any("evm" in entry["question"].lower() for entry in result)
    assert all(entry.get("fallback") is True for entry in result)


@pytest.mark.asyncio
async def test_search_keyword_fallback_returns_empty_for_irrelevant_query() -> None:
    service = VertexFAQService(api_key=None)
    result = await service.search("xyz qqq mmmnnn")
    assert result == []

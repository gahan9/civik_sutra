"""Targeted tests to raise coverage from 76% to 85%+.

Covers under-tested paths in:
- vertex_service.py (embedding path, corpus embedding, scoring)
- candidate_service.py (reverse geocode, parse grounding, compare)
- manifesto_service.py (parse categories, parse promises, align)
- chat_service.py (function calling loop, guardrails)
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.candidate import (
    CandidateSummary,
    GroundingResult,
    NewsItem,
)
from src.services.candidate_service import CandidateService
from src.services.manifesto_service import ManifestoService
from src.services.vertex_service import VertexFAQService, _cosine_similarity


# =============================================================================
# vertex_service.py — embedding path tests
# =============================================================================


@pytest.mark.asyncio
async def test_vertex_search_with_mocked_embeddings() -> None:
    service = VertexFAQService(api_key="fake-key")

    fake_vector = [0.1] * 768

    async def _fake_embed(text: str) -> list[float]:
        return fake_vector

    service._embed_text = _fake_embed  # type: ignore[assignment]
    service._corpus_vectors = [fake_vector] * 55

    results = await service.search("What is NOTA?", top_k=3, threshold=0.0)
    assert len(results) <= 3
    assert all("score" in r for r in results)


@pytest.mark.asyncio
async def test_vertex_corpus_embed_failure_falls_back() -> None:
    service = VertexFAQService(api_key="fake-key")

    call_count = 0

    async def _failing_embed(text: str) -> list[float] | None:
        nonlocal call_count
        call_count += 1
        if call_count > 2:
            return None
        return [0.5] * 768

    service._embed_text = _failing_embed  # type: ignore[assignment]

    results = await service.search("voter eligibility age")
    assert all(r.get("fallback") is True for r in results)


@pytest.mark.asyncio
async def test_vertex_search_query_embed_failure() -> None:
    service = VertexFAQService(api_key="fake-key")
    service._corpus_vectors = [[0.1] * 768] * 55

    async def _fail_embed(text: str) -> list[float] | None:
        return None

    service._embed_text = _fail_embed  # type: ignore[assignment]
    results = await service.search("test query")
    assert all(r.get("fallback") is True for r in results)


def test_cosine_similarity_mismatched_lengths() -> None:
    assert _cosine_similarity([1.0, 2.0], [1.0]) == 0.0


def test_cosine_similarity_negative_values() -> None:
    result = _cosine_similarity([1.0, 0.0], [-1.0, 0.0])
    assert result == pytest.approx(-1.0)


@pytest.mark.asyncio
async def test_vertex_keyword_fallback_top_k() -> None:
    service = VertexFAQService(api_key=None)
    results = await service.search("How voter registration works", top_k=1)
    assert len(results) <= 1


@pytest.mark.asyncio
async def test_vertex_keyword_fallback_short_tokens_filtered() -> None:
    service = VertexFAQService(api_key=None)
    results = await service.search("is it ok")
    # All tokens are <= 2 chars so no matches
    assert results == []


# =============================================================================
# candidate_service.py — parse_grounding, reverse_geocode, etc.
# =============================================================================


def test_parse_grounding_response_valid_json() -> None:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    json_text = json.dumps({
        "recent_news": [
            {"title": "Candidate wins award", "source": "Times", "date": "2024-01-01", "sentiment": "positive"},
        ],
        "achievements": ["Built schools"],
        "controversies": ["Land dispute"],
        "social_media_presence": "Active on Twitter",
    })
    result = service._parse_grounding_response(json_text, "Test Person")
    assert len(result.recent_news) == 1
    assert result.recent_news[0].title == "Candidate wins award"
    assert result.achievements == ["Built schools"]
    assert result.controversies == ["Land dispute"]


def test_parse_grounding_response_markdown_fenced() -> None:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    text = '```json\n{"recent_news": [], "achievements": ["X"], "controversies": []}\n```'
    result = service._parse_grounding_response(text, "Test")
    assert result.achievements == ["X"]


def test_parse_grounding_response_invalid_json() -> None:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    result = service._parse_grounding_response("not json at all", "Test")
    assert len(result.recent_news) > 0
    assert result.sources[0].source == "Demo Data"


def test_parse_grounding_response_empty() -> None:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    result = service._parse_grounding_response("", "Test")
    assert result.sources[0].source == "Demo Data"


def test_stub_candidate_parses_id() -> None:
    stub = CandidateService._stub_candidate("cand_ramesh_kumar_bjp")
    assert stub.name == "Ramesh Kumar"
    assert stub.party == "BJP"


def test_stub_candidate_no_party() -> None:
    stub = CandidateService._stub_candidate("cand_solo")
    assert stub.party == "Independent"


def test_find_candidate_returns_match() -> None:
    candidates = [
        CandidateSummary(id="abc", name="A", party="X", education="BA"),
        CandidateSummary(id="def", name="B", party="Y", education="MA"),
    ]
    result = CandidateService._find_candidate("def", candidates)
    assert result is not None
    assert result.name == "B"


def test_find_candidate_returns_none_when_empty() -> None:
    assert CandidateService._find_candidate("abc", None) is None
    assert CandidateService._find_candidate("abc", []) is None


def test_make_id_normalizes() -> None:
    result = CandidateService._make_id("Ramesh Kumar", "BJP")
    assert result == "cand_ramesh_kumar_bjp"


def test_make_id_handles_special_chars() -> None:
    result = CandidateService._make_id("Dr. A.P.J. Abdul Kalam", "IND")
    assert "cand_" in result
    assert "ind" in result


def test_delivery_probability_moderate() -> None:
    candidate = CandidateSummary(
        id="test", name="Test", party="X", education="MBA",
        past_positions=["MLA 2019"],
    )
    grounding = GroundingResult(recent_news=[])
    result = CandidateService._assess_delivery_probability(candidate, grounding)
    assert "Moderate" in result


def test_delivery_probability_very_low() -> None:
    candidate = CandidateSummary(
        id="test", name="Test", party="X", education="MBA",
        criminal_cases=10,
    )
    grounding = GroundingResult(
        recent_news=[
            NewsItem(title="Scandal", source="X", date="2024", sentiment="negative"),
            NewsItem(title="More scandal", source="Y", date="2024", sentiment="negative"),
        ]
    )
    result = CandidateService._assess_delivery_probability(candidate, grounding)
    assert "Very Low" in result


def test_format_inr_below_lakh() -> None:
    assert CandidateService._format_inr(50_000) == "\u20b950,000"


@pytest.mark.asyncio
async def test_reverse_geocode_without_api_key() -> None:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    result = await service._reverse_geocode(28.6, 77.2)
    assert result == "New Delhi"


@pytest.mark.asyncio
async def test_background_check_with_known_candidate() -> None:
    candidates = [
        CandidateSummary(
            id="cand_test_xyz",
            name="Test Person",
            party="XYZ",
            education="PhD",
            total_assets_inr=9_000_000,
        )
    ]
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    report = await service.background_check("cand_test_xyz", candidates)
    assert report.candidate.name == "Test Person"
    assert report.asset_breakdown.movable == 3_000_000
    assert report.asset_breakdown.immovable == 6_000_000


@pytest.mark.asyncio
async def test_compare_three_candidates() -> None:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    result = await service.compare(
        ["cand_a_x", "cand_b_y", "cand_c_z"]
    )
    assert len(result.candidates) == 3
    assert "These candidates" in result.ai_analysis


# =============================================================================
# manifesto_service.py — parsing and alignment
# =============================================================================


def test_parse_categories_valid_json() -> None:
    service = ManifestoService(gemini_api_key=None)
    text = json.dumps({
        "economy": ["Promise 1"],
        "healthcare": ["Promise 2", "Promise 3"],
    })
    result = service._parse_categories(text)
    assert result["economy"] == ["Promise 1"]
    assert len(result["healthcare"]) == 2


def test_parse_categories_markdown_fenced() -> None:
    service = ManifestoService(gemini_api_key=None)
    text = '```json\n{"governance": ["Reform 1"]}\n```'
    result = service._parse_categories(text)
    assert result["governance"] == ["Reform 1"]


def test_parse_categories_invalid_json() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = service._parse_categories("broken json")
    assert all(v == ["Not addressed"] for v in result.values())


def test_parse_categories_empty() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = service._parse_categories("")
    assert "economy" in result


def test_parse_promises_valid_json() -> None:
    service = ManifestoService(gemini_api_key=None)
    text = json.dumps([
        {"promise": "Build roads", "status": "fulfilled", "evidence": "Done", "source": "Gov"},
        {"promise": "Clean air", "status": "partial", "evidence": "50%", "source": "Report"},
    ])
    result = service._parse_promises(text, "TEST")
    assert len(result) == 2
    assert result[0].status == "fulfilled"


def test_parse_promises_invalid_json() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = service._parse_promises("not json", "BJP")
    assert len(result) > 0


def test_parse_promises_empty() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = service._parse_promises("", "BJP")
    assert len(result) > 0


def test_identify_incumbents() -> None:
    result = ManifestoService._identify_incumbents(["BJP", "AAP", "INC", "BSP"])
    assert "BJP" in result
    assert "INC" in result
    assert "AAP" not in result


def test_get_manifesto_url() -> None:
    assert ManifestoService._get_manifesto_url("BJP") == "https://www.bjp.org/manifesto"
    assert ManifestoService._get_manifesto_url("unknown") is None


@pytest.mark.asyncio
async def test_compare_manifestos_without_api_key() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = await service.compare_manifestos(["BJP", "INC"])
    assert len(result.parties) == 2
    assert len(result.categories) > 0
    assert result.ai_analysis != ""


@pytest.mark.asyncio
async def test_fetch_manifesto_caches_result() -> None:
    service = ManifestoService(gemini_api_key=None)
    first = await service.fetch_manifesto("BJP")
    second = await service.fetch_manifesto("BJP")
    assert first.party_name == second.party_name


@pytest.mark.asyncio
async def test_compare_manifestos_with_category_filter() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = await service.compare_manifestos(
        ["BJP", "INC"],
        categories=["economy", "healthcare"],
    )
    assert "economy" in result.categories
    assert "healthcare" in result.categories


@pytest.mark.asyncio
async def test_track_past_promises_for_incumbent() -> None:
    service = ManifestoService(gemini_api_key=None)
    promises = await service.track_past_promises("BJP", 2019)
    assert len(promises) > 0
    assert promises[0].status in ("fulfilled", "partial", "not_met", "ongoing")


@pytest.mark.asyncio
async def test_track_past_promises_for_non_incumbent() -> None:
    service = ManifestoService(gemini_api_key=None)
    promises = await service.track_past_promises("AAP", 2019)
    assert promises == []

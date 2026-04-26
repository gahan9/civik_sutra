from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from src.models.candidate import (
    CandidateSearchRequest,
    CandidateSummary,
    CompareRequest,
    GroundingResult,
    NewsItem,
    RawCandidateData,
    SourceCitation,
)
from src.services.candidate_service import CandidateService


def _make_service(
    scraper_candidates: list[RawCandidateData] | None = None,
) -> CandidateService:
    service = CandidateService(gemini_api_key=None, maps_api_key=None)
    if scraper_candidates is not None:
        service._scraper.fetch_myneta_candidates = AsyncMock(
            return_value=scraper_candidates,
        )
    else:
        service._scraper.fetch_myneta_candidates = AsyncMock(return_value=[])
    return service


@pytest.mark.asyncio
async def test_search_by_constituency_returns_candidates() -> None:
    service = _make_service()
    response = await service.search_by_constituency("South Delhi")

    assert response.constituency == "South Delhi"
    assert len(response.candidates) > 0
    assert all(isinstance(c, CandidateSummary) for c in response.candidates)


@pytest.mark.asyncio
async def test_search_by_constituency_uses_cache() -> None:
    service = _make_service()

    first = await service.search_by_constituency("South Delhi")
    second = await service.search_by_constituency("South Delhi")

    assert first.candidates == second.candidates
    service._scraper.fetch_myneta_candidates.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_constituency_with_scraped_data() -> None:
    raw = [
        RawCandidateData(
            name="Test Candidate",
            party="XYZ",
            education="PhD",
            criminal_cases=0,
            total_assets_inr=5_000_000,
        ),
    ]
    service = _make_service(scraper_candidates=raw)

    response = await service.search_by_constituency("Test Constituency")

    assert len(response.candidates) == 1
    assert response.candidates[0].name == "Test Candidate"
    assert response.candidates[0].party == "XYZ"


@pytest.mark.asyncio
async def test_search_by_location_resolves_constituency() -> None:
    service = _make_service()

    response = await service.search_by_location(lat=28.5245, lng=77.2066)

    assert response.constituency == "New Delhi"
    assert len(response.candidates) > 0


@pytest.mark.asyncio
async def test_grounding_search_returns_structured_result() -> None:
    service = _make_service()

    result = await service.grounding_search(
        "Ramesh Kumar", "South Delhi", "BJP",
    )

    assert isinstance(result, GroundingResult)
    assert len(result.recent_news) > 0
    assert all(isinstance(n, NewsItem) for n in result.recent_news)


@pytest.mark.asyncio
async def test_background_check_combines_sources() -> None:
    service = _make_service()

    report = await service.background_check("cand_ramesh_kumar_bjp")

    assert report.candidate.id == "cand_ramesh_kumar_bjp"
    assert isinstance(report.grounding, GroundingResult)
    assert "myneta" in report.source_urls


@pytest.mark.asyncio
async def test_compare_builds_matrix() -> None:
    service = _make_service()

    result = await service.compare(
        ["cand_ramesh_kumar_bjp", "cand_priya_singh_inc"],
    )

    assert len(result.dimensions) > 0
    assert "education" in result.dimensions
    assert "delivery_probability" in result.dimensions
    assert len(result.candidates) == 2


@pytest.mark.asyncio
async def test_compare_includes_ai_analysis() -> None:
    service = _make_service()

    result = await service.compare(
        ["cand_ramesh_kumar_bjp", "cand_priya_singh_inc"],
    )

    assert len(result.ai_analysis) > 0
    assert len(result.ai_analysis_citations) > 0


def test_compare_request_limits_to_4_candidates() -> None:
    with pytest.raises(ValidationError):
        CompareRequest(
            candidate_ids=["a", "b", "c", "d", "e"],
        )


def test_compare_request_requires_at_least_2() -> None:
    with pytest.raises(ValidationError):
        CompareRequest(candidate_ids=["only_one"])


def test_search_request_requires_constituency_or_coords() -> None:
    with pytest.raises(ValidationError):
        CandidateSearchRequest()


def test_search_request_validates_coordinate_bounds() -> None:
    with pytest.raises(ValidationError):
        CandidateSearchRequest(lat=200, lng=77.2)


def test_search_request_accepts_constituency_only() -> None:
    req = CandidateSearchRequest(constituency="South Delhi")
    assert req.constituency == "South Delhi"


def test_search_request_accepts_coords_only() -> None:
    req = CandidateSearchRequest(lat=28.5, lng=77.2)
    assert req.lat == 28.5


@pytest.mark.asyncio
async def test_cache_ttl_24h() -> None:
    service = _make_service()

    await service.search_by_constituency("Delhi")
    service._cache["search:delhi"] = (0, service._cache["search:delhi"][1])

    await service.search_by_constituency("Delhi")
    assert service._scraper.fetch_myneta_candidates.call_count == 2


def test_format_inr_crore() -> None:
    assert CandidateService._format_inr(21_000_000) == "\u20b92.1 Crore"


def test_format_inr_lakh() -> None:
    assert CandidateService._format_inr(500_000) == "\u20b95.0 Lakh"


def test_format_inr_zero() -> None:
    assert CandidateService._format_inr(0) == "Not declared"


def test_delivery_probability_high() -> None:
    candidate = CandidateSummary(
        id="test", name="Test", party="X", education="MBA",
        past_positions=["MLA 2014", "MLA 2019", "MP 2024"],
    )
    grounding = GroundingResult(
        recent_news=[
            NewsItem(title="Good", source="X", date="2024", sentiment="positive"),
        ],
    )
    result = CandidateService._assess_delivery_probability(candidate, grounding)
    assert "High" in result


def test_delivery_probability_low_with_criminal_cases() -> None:
    candidate = CandidateSummary(
        id="test", name="Test", party="X", education="MBA",
        criminal_cases=5,
    )
    grounding = GroundingResult()
    result = CandidateService._assess_delivery_probability(candidate, grounding)
    assert "Low" in result or "Very Low" in result

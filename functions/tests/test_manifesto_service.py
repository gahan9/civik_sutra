from __future__ import annotations

import pytest

from src.models.manifesto import ManifestoData, PromiseTracker, ManifestoComparison
from src.services.manifesto_service import ManifestoService


@pytest.mark.asyncio
async def test_compare_manifestos_returns_comparison() -> None:
    service = ManifestoService(gemini_api_key=None)
    result = await service.compare_manifestos(["BJP", "INC"])

    assert isinstance(result, ManifestoComparison)
    assert len(result.parties) == 2
    assert "economy" in result.categories
    assert "BJP" in result.categories["economy"]
    assert "INC" in result.categories["economy"]
    assert len(result.sources) == 2


@pytest.mark.asyncio
async def test_fetch_manifesto_returns_data() -> None:
    service = ManifestoService(gemini_api_key=None)
    data = await service.fetch_manifesto("BJP")

    assert isinstance(data, ManifestoData)
    assert data.party_name == "BJP"
    assert "economy" in data.categories
    assert len(data.categories["economy"]) > 0


@pytest.mark.asyncio
async def test_track_past_promises_returns_trackers() -> None:
    service = ManifestoService(gemini_api_key=None)
    promises = await service.track_past_promises("BJP", 2019)

    assert len(promises) > 0
    assert isinstance(promises[0], PromiseTracker)
    assert promises[0].status in ["fulfilled", "partial", "not_met", "ongoing"]


def test_align_categories() -> None:
    service = ManifestoService(gemini_api_key=None)
    m1 = ManifestoData(
        party_name="PartyA",
        categories={"economy": ["Promise A1"], "education": ["Promise A2"]},
        summary="Summary A",
    )
    m2 = ManifestoData(
        party_name="PartyB",
        categories={"economy": ["Promise B1"], "healthcare": ["Promise B2"]},
        summary="Summary B",
    )

    aligned = service._align_categories([m1, m2], filter_categories=None)

    assert "economy" in aligned
    assert aligned["economy"]["PartyA"] == ["Promise A1"]
    assert aligned["economy"]["PartyB"] == ["Promise B1"]

    assert "education" in aligned
    assert aligned["education"]["PartyA"] == ["Promise A2"]
    assert aligned["education"]["PartyB"] == ["Not addressed"]

    assert "healthcare" in aligned
    assert aligned["healthcare"]["PartyA"] == ["Not addressed"]
    assert aligned["healthcare"]["PartyB"] == ["Promise B2"]


def test_parse_categories_invalid_json() -> None:
    service = ManifestoService(gemini_api_key=None)
    parsed = service._parse_categories("This is not JSON")

    assert "economy" in parsed
    assert parsed["economy"] == ["Not addressed"]


def test_parse_promises_invalid_json() -> None:
    service = ManifestoService(gemini_api_key=None)
    parsed = service._parse_promises("This is not JSON", "BJP")

    assert len(parsed) > 0
    assert parsed[0].promise != "Unknown"

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.services.nl_service import (
    EntityResult,
    NLEnrichment,
    NLService,
    SentimentResult,
)


def _make_entity(name: str, type_: str, salience: float) -> SimpleNamespace:
    return SimpleNamespace(name=name, type_=type_, salience=salience)


def _make_sentiment(score: float, magnitude: float) -> SimpleNamespace:
    return SimpleNamespace(
        document_sentiment=SimpleNamespace(score=score, magnitude=magnitude)
    )


def _fake_language_types_module() -> SimpleNamespace:
    """Provide a fake google.cloud.language_v2.types for import mocking."""
    doc_type = SimpleNamespace(PLAIN_TEXT="PLAIN_TEXT")
    document_cls = type("Document", (), {"Type": doc_type})
    document_cls.__init__ = lambda self, **kw: None  # type: ignore[assignment]
    return SimpleNamespace(Document=document_cls)


@pytest.fixture(autouse=True)
def _patch_language_import(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure `from google.cloud.language_v2 import types` works in tests."""
    fake_types = _fake_language_types_module()
    fake_module = SimpleNamespace(types=fake_types)
    monkeypatch.setitem(sys.modules, "google.cloud.language_v2", fake_module)
    monkeypatch.setitem(sys.modules, "google.cloud.language_v2.types", fake_types)


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.analyze_entities.return_value = SimpleNamespace(
        entities=[
            _make_entity("ECI", "ORGANIZATION", 0.9),
            _make_entity("voter ID", "OTHER", 0.4),
        ]
    )
    client.analyze_sentiment.return_value = _make_sentiment(0.3, 0.7)
    return client


@pytest.fixture
def service(mock_client: MagicMock) -> NLService:
    return NLService(project_id="test-proj", client=mock_client)


def test_is_configured(service: NLService) -> None:
    assert service.is_configured is True


def test_not_configured_without_project() -> None:
    svc = NLService(project_id="")
    assert svc.is_configured is False


def test_analyse_returns_entities_and_sentiment(
    service: NLService,
) -> None:
    result = service.analyse("How do I get a voter ID from ECI?")
    assert len(result.entities) == 2
    assert result.entities[0].name == "ECI"
    assert result.entities[0].salience == 0.9
    assert result.sentiment.score == 0.3
    assert result.sentiment.magnitude == 0.7


def test_analyse_empty_text(service: NLService) -> None:
    result = service.analyse("")
    assert result == NLEnrichment()


def test_analyse_unconfigured_returns_empty() -> None:
    svc = NLService(project_id="")
    result = svc.analyse("test query")
    assert result == NLEnrichment()


def test_analyse_client_error_returns_empty(service: NLService) -> None:
    service._client.analyze_entities.side_effect = RuntimeError("API down")
    result = service.analyse("test query")
    assert result.entities == []
    assert result.sentiment == SentimentResult(score=0.0, magnitude=0.0)


def test_client_init_failure_degrades() -> None:
    svc = NLService(project_id="proj")
    with patch(
        "src.services.nl_service.NLService._get_client",
        return_value=None,
    ):
        result = svc.analyse("test")
        assert result == NLEnrichment()


def test_to_dict_serialisation() -> None:
    enrichment = NLEnrichment(
        entities=[EntityResult(name="ECI", entity_type="ORG", salience=0.8)],
        sentiment=SentimentResult(score=0.5, magnitude=0.6),
    )
    d = enrichment.to_dict()
    assert d["entities"][0]["name"] == "ECI"
    assert d["sentiment"]["score"] == 0.5

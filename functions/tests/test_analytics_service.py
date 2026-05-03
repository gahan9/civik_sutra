from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.services.analytics_service import AnalyticsService


class FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict] = []

    def add(self, doc: dict) -> None:
        self.docs.append(doc)


class FakeClient:
    def __init__(self) -> None:
        self._collection = FakeCollection()

    def collection(self, name: str) -> FakeCollection:
        return self._collection


@pytest.fixture
def fake_client() -> FakeClient:
    return FakeClient()


@pytest.fixture
def service(fake_client: FakeClient) -> AnalyticsService:
    return AnalyticsService(project_id="test-proj", client=fake_client)


def test_is_configured_with_project(service: AnalyticsService) -> None:
    assert service.is_configured is True


def test_is_not_configured_without_project() -> None:
    svc = AnalyticsService(project_id="")
    assert svc.is_configured is False


@patch.dict("os.environ", {"EP_ANALYTICS_ENABLED": "false"})
def test_disabled_via_env() -> None:
    svc = AnalyticsService(project_id="proj")
    assert svc.is_configured is False


def test_log_event_skips_when_unconfigured() -> None:
    svc = AnalyticsService(project_id="")
    svc.log_event("test_event")


def test_log_event_writes_to_firestore(
    service: AnalyticsService, fake_client: FakeClient
) -> None:
    async def _run() -> None:
        service.log_event(
            "chat_query",
            language="hi",
            journey_stage="eligibility",
            metadata={"tool": "faq_search"},
        )
        await asyncio.sleep(0.05)

    asyncio.run(_run())

    docs = fake_client._collection.docs
    assert len(docs) == 1
    doc = docs[0]
    assert doc["event"] == "chat_query"
    assert doc["language"] == "hi"
    assert doc["journey_stage"] == "eligibility"
    assert doc["metadata"] == {"tool": "faq_search"}
    assert "timestamp" in doc


def test_log_event_without_optional_fields(
    service: AnalyticsService, fake_client: FakeClient
) -> None:
    async def _run() -> None:
        service.log_event("language_switched")
        await asyncio.sleep(0.05)

    asyncio.run(_run())

    docs = fake_client._collection.docs
    assert len(docs) == 1
    assert "journey_stage" not in docs[0]
    assert "metadata" not in docs[0]


def test_write_failure_is_swallowed(service: AnalyticsService) -> None:
    broken_client = MagicMock()
    broken_client.collection.side_effect = RuntimeError("boom")
    service._client = broken_client

    async def _run() -> None:
        service.log_event("broken_event")
        await asyncio.sleep(0.05)

    asyncio.run(_run())


def test_client_init_failure_degrades_gracefully() -> None:
    svc = AnalyticsService(project_id="proj")
    with patch(
        "src.services.analytics_service.AnalyticsService._get_client",
        return_value=None,
    ):
        async def _run() -> None:
            svc.log_event("test")
            await asyncio.sleep(0.05)

        asyncio.run(_run())

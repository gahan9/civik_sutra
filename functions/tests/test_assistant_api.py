from __future__ import annotations

from fastapi.testclient import TestClient

from src.app import app
from src.api.assistant import get_translation_service
from src.services.translation_service import (
    TranslationService,
    reset_translation_cache,
)

client = TestClient(app)


def test_timeline_endpoint_returns_events() -> None:
    response = client.get("/assistant/timeline")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 5
    assert isinstance(payload["events"], list)
    first = payload["events"][0]
    for required in (
        "id",
        "title",
        "stage",
        "starts_on",
        "ends_on",
        "description",
        "source",
        "source_url",
    ):
        assert required in first


def test_timeline_endpoint_filters_by_stage() -> None:
    response = client.get("/assistant/timeline?stage=Polling")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert all("polling" in e["stage"].lower() for e in payload["events"])


def test_timeline_endpoint_returns_empty_when_filter_does_not_match() -> None:
    response = client.get("/assistant/timeline?stage=DoesNotExist")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["events"] == []


def test_quick_questions_endpoint_supports_languages() -> None:
    response = client.get("/assistant/questions?language=hi")
    assert response.status_code == 200
    payload = response.json()
    assert "questions" in payload
    assert len(payload["questions"]) > 0


def test_chat_request_validates_language() -> None:
    """The chat endpoint must reject unsupported languages."""
    response = client.post(
        "/assistant/chat",
        json={
            "message": "Hi",
            "session_id": "test",
            "language": "xx",
        },
    )
    assert response.status_code == 422


class _FakeTranslationService:
    def __init__(self, translated: str = "translated") -> None:
        self.translated = translated
        self.calls: list[dict[str, str | None]] = []

    def translate(
        self,
        text: str,
        *,
        target_language: str,
        source_language: str | None = None,
    ) -> str:
        self.calls.append(
            {
                "text": text,
                "target_language": target_language,
                "source_language": source_language,
            }
        )
        return self.translated


def test_translate_endpoint_returns_translated_text() -> None:
    fake = _FakeTranslationService(translated="नमस्ते")
    app.dependency_overrides[get_translation_service] = lambda: fake
    try:
        response = client.post(
            "/assistant/translate",
            json={
                "text": "hello",
                "target_language": "hi",
                "source_language": "en",
            },
        )
    finally:
        app.dependency_overrides.pop(get_translation_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "नमस्ते"
    assert payload["target_language"] == "hi"
    assert payload["source_language"] == "en"
    assert fake.calls[0]["target_language"] == "hi"


def test_translate_endpoint_rejects_unsupported_language() -> None:
    response = client.post(
        "/assistant/translate",
        json={"text": "hello", "target_language": "xx"},
    )
    assert response.status_code == 422


def test_translate_endpoint_rejects_empty_text() -> None:
    response = client.post(
        "/assistant/translate",
        json={"text": "", "target_language": "hi"},
    )
    assert response.status_code == 422


def test_translate_endpoint_falls_back_when_unconfigured() -> None:
    reset_translation_cache()
    real = TranslationService(project_id="", location="global")
    app.dependency_overrides[get_translation_service] = lambda: real
    try:
        response = client.post(
            "/assistant/translate",
            json={"text": "hello", "target_language": "hi"},
        )
    finally:
        app.dependency_overrides.pop(get_translation_service, None)

    assert response.status_code == 200
    assert response.json()["text"] == "hello"

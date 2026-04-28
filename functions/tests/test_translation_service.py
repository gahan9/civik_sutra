"""Tests for the Cloud Translation v3 service wrapper."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass

import pytest

from src.services.translation_service import (
    TranslationService,
    reset_translation_cache,
)


@dataclass
class _FakeTranslation:
    translated_text: str


@dataclass
class _FakeResponse:
    translations: list[_FakeTranslation]


class _FakeClient:
    """In-memory stand-in for ``TranslationServiceClient``."""

    def __init__(
        self,
        *,
        translated_text: str = "fake-translation",
        raise_exc: Exception | None = None,
    ) -> None:
        self.translated_text = translated_text
        self.raise_exc = raise_exc
        self.calls: list[dict[str, Any]] = []

    def translate_text(self, request: dict[str, Any]) -> _FakeResponse:
        self.calls.append(request)
        if self.raise_exc is not None:
            raise self.raise_exc
        return _FakeResponse(translations=[_FakeTranslation(self.translated_text)])


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    reset_translation_cache()


def test_returns_source_when_unconfigured() -> None:
    service = TranslationService(project_id="", location="global")
    assert service.translate("hello", target_language="hi") == "hello"


def test_returns_source_for_unsupported_target() -> None:
    service = TranslationService(project_id="proj", location="global")
    assert service.translate("hello", target_language="xx") == "hello"


def test_returns_source_when_target_equals_source() -> None:
    fake = _FakeClient()
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    result = service.translate(
        "hello", target_language="en", source_language="en"
    )
    assert result == "hello"
    assert fake.calls == []


def test_returns_source_for_empty_text() -> None:
    service = TranslationService(project_id="proj", location="global")
    assert service.translate("", target_language="hi") == ""
    assert service.translate("   ", target_language="hi") == "   "


def test_translates_with_explicit_source() -> None:
    fake = _FakeClient(translated_text="नमस्ते")
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    result = service.translate(
        "hello", target_language="hi", source_language="en"
    )
    assert result == "नमस्ते"
    assert len(fake.calls) == 1
    assert fake.calls[0]["target_language_code"] == "hi"
    assert fake.calls[0]["source_language_code"] == "en"
    assert fake.calls[0]["mime_type"] == "text/plain"


def test_translates_with_auto_detect_when_source_missing() -> None:
    fake = _FakeClient(translated_text="नमस्ते")
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    result = service.translate("hello", target_language="hi")
    assert result == "नमस्ते"
    assert "source_language_code" not in fake.calls[0]


def test_uses_cache_for_repeat_translation() -> None:
    fake = _FakeClient(translated_text="नमस्ते")
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    service.translate("hello", target_language="hi", source_language="en")
    service.translate("hello", target_language="hi", source_language="en")
    assert len(fake.calls) == 1


def test_clamps_long_input() -> None:
    fake = _FakeClient(translated_text="-clamped-")
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    long_text = "a" * 9_000
    service.translate(long_text, target_language="hi")
    assert len(fake.calls[0]["contents"][0]) == 5_000


def test_returns_source_when_client_raises() -> None:
    fake = _FakeClient(raise_exc=RuntimeError("boom"))
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    result = service.translate("hello", target_language="hi")
    assert result == "hello"


def test_returns_source_when_response_has_no_translations() -> None:
    class _EmptyClient:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        def translate_text(self, request: dict[str, Any]) -> _FakeResponse:
            self.calls.append(request)
            return _FakeResponse(translations=[])

    service = TranslationService(
        project_id="proj", location="global", client=_EmptyClient()
    )
    result = service.translate("hello", target_language="hi")
    assert result == "hello"


def test_is_configured_property_reflects_project_id() -> None:
    assert TranslationService(project_id="proj").is_configured is True
    assert TranslationService(project_id="").is_configured is False


def test_invalid_source_language_falls_back_to_auto_detect() -> None:
    fake = _FakeClient(translated_text="नमस्ते")
    service = TranslationService(
        project_id="proj", location="global", client=fake
    )
    service.translate(
        "hello", target_language="hi", source_language="zz"
    )
    assert "source_language_code" not in fake.calls[0]


def test_non_string_input_returns_empty_string() -> None:
    service = TranslationService(project_id="proj", location="global")
    assert service.translate(None, target_language="hi") == ""  # type: ignore[arg-type]

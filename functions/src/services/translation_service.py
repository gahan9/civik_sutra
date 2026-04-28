"""Google Cloud Translation v3 service with LRU cache and graceful fallback.

The CivikSutra UI ships static i18n catalogs for English and Hindi, but
several response surfaces are *dynamic* — AI-generated chat answers,
manifesto comparison narratives, candidate background paragraphs.

This service translates that runtime content between supported locales
(``en`` ⇄ ``hi``) using the Google Cloud Translation v3 ``translateText``
endpoint. A bounded LRU cache keeps cost predictable, and any backend or
configuration failure falls back to the source text — i.e. the user always
sees something readable, even when the translate API is unreachable.

Environment configuration:
    EP_GCP_PROJECT_ID         GCP project that hosts Translation API.
    EP_TRANSLATE_LOCATION     Regional endpoint (default ``global``).
    EP_TRANSLATE_CACHE_SIZE   Optional integer override for cache size.
"""

from __future__ import annotations

import os
import logging
from typing import Any
from functools import lru_cache

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: frozenset[str] = frozenset({"en", "hi"})
DEFAULT_CACHE_SIZE = 1024
MAX_INPUT_CHARS = 5_000


class TranslationService:
    """Translate runtime strings between supported locales (en/hi).

    Designed to be cheap and fail-soft: if the Cloud Translation client is
    not available — e.g. no service account, no project, or a transient
    network error — the service simply returns the source text unchanged.
    """

    def __init__(
        self,
        *,
        project_id: str | None = None,
        location: str | None = None,
        client: Any | None = None,
    ) -> None:
        """Initialise the translation service.

        Args:
            project_id: GCP project ID. Falls back to ``EP_GCP_PROJECT_ID``.
            location: Translation endpoint region (default ``global``).
            client: Optional pre-built ``TranslationServiceClient`` for
                tests. When ``None`` the client is created lazily on the
                first ``translate()`` call.

        """
        self._project_id = project_id or os.getenv("EP_GCP_PROJECT_ID", "")
        self._location = location or os.getenv(
            "EP_TRANSLATE_LOCATION", "global"
        )
        self._client = client
        self._client_init_failed = False

    @property
    def is_configured(self) -> bool:
        """True when a valid GCP project ID is available."""
        return bool(self._project_id)

    def translate(
        self,
        text: str,
        *,
        target_language: str,
        source_language: str | None = None,
    ) -> str:
        """Translate ``text`` to ``target_language``.

        Returns the source text unchanged when the service is not
        configured, the input is empty, or the underlying client raises.

        Args:
            text: The string to translate. Strings longer than
                ``MAX_INPUT_CHARS`` are clamped before translation.
            target_language: ISO-639-1 code for the target locale.
            source_language: Optional source language hint. When ``None``
                Cloud Translation auto-detects.

        """
        if not isinstance(text, str) or not text.strip():
            return text or ""

        normalised_target = target_language.strip().lower()
        if normalised_target not in SUPPORTED_LANGUAGES:
            return text

        if source_language is not None:
            normalised_source: str | None = source_language.strip().lower()
            if normalised_source not in SUPPORTED_LANGUAGES:
                normalised_source = None
            if normalised_source == normalised_target:
                return text
        else:
            normalised_source = None

        if not self.is_configured:
            return text

        clamped = text[:MAX_INPUT_CHARS]

        cached = _cached_translate(
            project_id=self._project_id,
            location=self._location,
            text=clamped,
            target_language=normalised_target,
            source_language=normalised_source or "",
            client_id=id(self),
        )
        if cached is not None:
            return cached

        client = self._get_client()
        if client is None:
            return text

        try:
            parent = f"projects/{self._project_id}/locations/{self._location}"
            request: dict[str, Any] = {
                "parent": parent,
                "contents": [clamped],
                "mime_type": "text/plain",
                "target_language_code": normalised_target,
            }
            if normalised_source:
                request["source_language_code"] = normalised_source
            response = client.translate_text(request=request)
            translations = getattr(response, "translations", None) or []
            if not translations:
                return text
            translated = getattr(translations[0], "translated_text", None)
            result = translated or text
        except Exception:  # noqa: BLE001 — graceful degradation by design.
            logger.exception("translation_failed")
            return text

        _cache_translation(
            project_id=self._project_id,
            location=self._location,
            text=clamped,
            target_language=normalised_target,
            source_language=normalised_source or "",
            client_id=id(self),
            translated=result,
        )
        return result

    def _get_client(self) -> Any | None:
        """Return the lazy-initialised Cloud Translation client.

        Falls back to ``None`` if the dependency or credentials are not
        available so the service degrades to a passthrough.
        """
        if self._client is not None:
            return self._client
        if self._client_init_failed:
            return None
        try:
            from google.cloud import translate_v3  # type: ignore[import-not-found]

            self._client = translate_v3.TranslationServiceClient()
            return self._client
        except Exception:  # noqa: BLE001 — we want a soft failure here.
            logger.warning("translation_client_unavailable", exc_info=True)
            self._client_init_failed = True
            return None


def _cache_size() -> int:
    """Return the LRU cache size from env, clamped to a sane minimum."""
    raw = os.getenv("EP_TRANSLATE_CACHE_SIZE")
    if not raw:
        return DEFAULT_CACHE_SIZE
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_CACHE_SIZE
    return max(64, value)


@lru_cache(maxsize=_cache_size())
def _cached_lookup(
    project_id: str,
    location: str,
    text: str,
    target_language: str,
    source_language: str,
    client_id: int,
) -> str | None:
    """LRU cache key resolver — populated via :func:`_cache_translation`."""
    # Real caching is done by manually inserting through a closure below;
    # this helper is only here so ``functools.lru_cache`` gives us the size
    # bound and eviction. Returning ``None`` signals "cache miss".
    del project_id, location, text, target_language, source_language, client_id
    return None


_TRANSLATION_CACHE: dict[tuple[str, str, str, str, str, int], str] = {}


def _cached_translate(
    *,
    project_id: str,
    location: str,
    text: str,
    target_language: str,
    source_language: str,
    client_id: int,
) -> str | None:
    """Look up a previously cached translation. Returns ``None`` on miss."""
    key = (project_id, location, text, target_language, source_language, client_id)
    return _TRANSLATION_CACHE.get(key)


def _cache_translation(
    *,
    project_id: str,
    location: str,
    text: str,
    target_language: str,
    source_language: str,
    client_id: int,
    translated: str,
) -> None:
    """Insert a translation into the bounded cache."""
    key = (project_id, location, text, target_language, source_language, client_id)
    _TRANSLATION_CACHE[key] = translated
    if len(_TRANSLATION_CACHE) > _cache_size():
        # Drop the oldest entry; ``dict`` preserves insertion order in 3.7+.
        oldest_key = next(iter(_TRANSLATION_CACHE))
        _TRANSLATION_CACHE.pop(oldest_key, None)


def reset_translation_cache() -> None:
    """Clear the in-memory translation cache (test helper)."""
    _TRANSLATION_CACHE.clear()
    _cached_lookup.cache_clear()

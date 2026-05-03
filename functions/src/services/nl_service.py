"""Google Cloud Natural Language API integration for query intent enrichment.

Extracts entities and sentiment from voter queries so the analytics pipeline
can track what topics voters care about and how they feel — without storing
any personally identifiable information.

Environment configuration:
    EP_GCP_PROJECT_ID    GCP project that hosts Cloud NL API.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EntityResult:
    """A single entity extracted from the query."""

    name: str
    entity_type: str
    salience: float


@dataclass(frozen=True)
class SentimentResult:
    """Overall sentiment of the query."""

    score: float
    magnitude: float


@dataclass
class NLEnrichment:
    """Combined NL analysis result."""

    entities: list[EntityResult] = field(default_factory=list)
    sentiment: SentimentResult = field(
        default_factory=lambda: SentimentResult(score=0.0, magnitude=0.0)
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialise for analytics logging."""
        return {
            "entities": [
                {"name": e.name, "type": e.entity_type, "salience": e.salience}
                for e in self.entities
            ],
            "sentiment": {
                "score": self.sentiment.score,
                "magnitude": self.sentiment.magnitude,
            },
        }


class NLService:
    """Thin wrapper around Cloud Natural Language ``analyze_entities`` + ``analyze_sentiment``."""

    def __init__(
        self,
        *,
        project_id: str | None = None,
        client: Any | None = None,
    ) -> None:
        """Initialise.

        Args:
            project_id: GCP project. Falls back to ``EP_GCP_PROJECT_ID``.
            client: Pre-built ``LanguageServiceClient`` for testing.

        """
        self._project_id = project_id or os.getenv("EP_GCP_PROJECT_ID", "")
        self._client = client
        self._client_init_failed = False

    @property
    def is_configured(self) -> bool:
        """True when a GCP project is available."""
        return bool(self._project_id)

    def analyse(self, text: str) -> NLEnrichment:
        """Run entity extraction and sentiment analysis on ``text``.

        Returns an empty ``NLEnrichment`` if the service is unconfigured or
        the API call fails — the caller should never block on this result.
        """
        if not text or not text.strip() or not self.is_configured:
            return NLEnrichment()

        client = self._get_client()
        if client is None:
            return NLEnrichment()

        try:
            from google.cloud.language_v2 import types  # type: ignore[import-not-found]

            document = types.Document(
                content=text[:5000],
                type_=types.Document.Type.PLAIN_TEXT,
                language_code="en",
            )

            entities_resp = client.analyze_entities(
                request={"document": document}
            )
            entities = [
                EntityResult(
                    name=getattr(e, "name", ""),
                    entity_type=str(getattr(e, "type_", "UNKNOWN")),
                    salience=float(getattr(e, "salience", 0.0)),
                )
                for e in getattr(entities_resp, "entities", [])
            ]

            sentiment_resp = client.analyze_sentiment(
                request={"document": document}
            )
            doc_sentiment = getattr(sentiment_resp, "document_sentiment", None)
            sentiment = SentimentResult(
                score=float(getattr(doc_sentiment, "score", 0.0)),
                magnitude=float(getattr(doc_sentiment, "magnitude", 0.0)),
            )

            return NLEnrichment(entities=entities, sentiment=sentiment)

        except Exception:  # noqa: BLE001
            logger.debug("nl_analysis_failed", exc_info=True)
            return NLEnrichment()

    def _get_client(self) -> Any | None:
        """Lazy-init the NL client.  ``None`` on failure."""
        if self._client is not None:
            return self._client
        if self._client_init_failed:
            return None
        try:
            from google.cloud import language_v2  # type: ignore[import-not-found]

            self._client = language_v2.LanguageServiceClient()
            return self._client
        except Exception:  # noqa: BLE001
            logger.warning("nl_client_unavailable", exc_info=True)
            self._client_init_failed = True
            return None

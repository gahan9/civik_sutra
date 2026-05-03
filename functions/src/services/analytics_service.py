"""Fire-and-forget Firestore event logging for CivikSutra analytics.

Logs anonymised usage events (no PII) to a ``civiksutra_events`` collection.
All writes are non-blocking — failures are swallowed so analytics never
degrades the user-facing request path.

Environment configuration:
    EP_GCP_PROJECT_ID    GCP project that hosts Firestore.
    EP_ANALYTICS_ENABLED Set to ``false`` to disable logging entirely.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

COLLECTION_NAME = "civiksutra_events"


class AnalyticsService:
    """Asynchronous, fire-and-forget event logger backed by Firestore."""

    def __init__(
        self,
        *,
        project_id: str | None = None,
        client: Any | None = None,
    ) -> None:
        """Initialise the analytics service.

        Args:
            project_id: GCP project ID. Falls back to ``EP_GCP_PROJECT_ID``.
            client: Optional pre-built Firestore client (for testing).

        """
        self._project_id = project_id or os.getenv("EP_GCP_PROJECT_ID", "")
        self._client = client
        self._client_init_failed = False
        self._enabled = os.getenv("EP_ANALYTICS_ENABLED", "true").lower() != "false"

    @property
    def is_configured(self) -> bool:
        """True when analytics can write to Firestore."""
        return self._enabled and bool(self._project_id)

    def log_event(
        self,
        event: str,
        *,
        language: str = "en",
        journey_stage: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Schedule a fire-and-forget event write.

        This method returns immediately. The Firestore write happens in a
        background ``asyncio.Task`` so it never blocks the HTTP response.

        Args:
            event: Event name (e.g. ``chat_query``, ``language_switched``).
            language: ISO-639-1 language code active at event time.
            journey_stage: Current voter journey stage, if applicable.
            metadata: Arbitrary extra data (no PII).

        """
        if not self.is_configured:
            return

        doc: dict[str, Any] = {
            "event": event,
            "timestamp": time.time(),
            "language": language,
        }
        if journey_stage:
            doc["journey_stage"] = journey_stage
        if metadata:
            doc["metadata"] = metadata

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._write(doc))
        except RuntimeError:
            pass

    async def _write(self, doc: dict[str, Any]) -> None:
        """Perform the actual Firestore insert.  Swallows all errors."""
        client = self._get_client()
        if client is None:
            return
        try:
            collection = client.collection(COLLECTION_NAME)
            collection.add(doc)
        except Exception:  # noqa: BLE001
            logger.debug("analytics_write_failed", exc_info=True)

    def _get_client(self) -> Any | None:
        """Lazy-init the Firestore client.  Returns ``None`` on failure."""
        if self._client is not None:
            return self._client
        if self._client_init_failed:
            return None
        try:
            from google.cloud import firestore  # type: ignore[import-not-found]

            self._client = firestore.Client(project=self._project_id)
            return self._client
        except Exception:  # noqa: BLE001
            logger.warning("firestore_client_unavailable", exc_info=True)
            self._client_init_failed = True
            return None

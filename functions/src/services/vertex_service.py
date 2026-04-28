"""Vertex AI semantic FAQ search using ``text-embedding-004`` embeddings.

Design notes
------------
* The FAQ corpus is embedded once at process start and cached in-memory for
  the lifetime of the function instance.
* Voter queries are embedded on demand and matched against the cached corpus
  with cosine similarity. Top-K results above a configurable threshold are
  returned to the caller.
* When the embeddings API is unreachable or the API key is missing, we fall
  back to deterministic keyword matching against the same corpus so the
  voter experience never breaks.
"""

from __future__ import annotations

import os
import json
import math
import asyncio
import urllib.error
import urllib.request
from typing import Any

import structlog

from src.data.faq_corpus import FAQ_CORPUS

logger = structlog.get_logger(__name__)

EMBEDDING_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "text-embedding-004:embedContent"
)
EMBEDDING_DIMENSIONS = 768
DEFAULT_TOP_K = 3
DEFAULT_THRESHOLD = 0.55


class VertexFAQService:
    """Semantic FAQ search backed by Gemini text embeddings.

    The service exposes a single :meth:`search` coroutine. Embedding the FAQ
    corpus is performed lazily on the first call to avoid blocking process
    startup when the API key is unavailable in a unit-test environment.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("EP_GEMINI_API_KEY")
        self._corpus_vectors: list[list[float]] | None = None
        self._lock = asyncio.Lock()

    async def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> list[dict[str, Any]]:
        """Return top-K FAQ entries ranked by semantic similarity.

        Args:
            query: Voter question in natural language.
            top_k: Maximum number of FAQ entries to return.
            threshold: Minimum cosine similarity score (0-1) for inclusion.

        Returns:
            List of dictionaries containing the original FAQ entry and a
            ``score`` field. Empty list when no entry clears the threshold.

        """
        query = (query or "").strip()
        if not query:
            return []

        if not self._api_key:
            return self._keyword_fallback(query, top_k)

        await self._ensure_corpus_embedded()
        if self._corpus_vectors is None:
            return self._keyword_fallback(query, top_k)

        query_vector = await self._embed_text(query)
        if query_vector is None:
            return self._keyword_fallback(query, top_k)

        scored: list[tuple[float, dict[str, str]]] = []
        for entry, vector in zip(FAQ_CORPUS, self._corpus_vectors, strict=True):
            score = _cosine_similarity(query_vector, vector)
            if score >= threshold:
                scored.append((score, entry))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {**entry, "score": round(score, 4)}
            for score, entry in scored[:top_k]
        ]

    async def _ensure_corpus_embedded(self) -> None:
        if self._corpus_vectors is not None:
            return

        async with self._lock:
            if self._corpus_vectors is not None:
                return

            vectors: list[list[float]] = []
            for entry in FAQ_CORPUS:
                text = f"{entry['topic']}: {entry['question']}\n{entry['answer']}"
                vector = await self._embed_text(text)
                if vector is None:
                    logger.warning(
                        "vertex_corpus_embed_failed",
                        faq_id=entry.get("id"),
                    )
                    self._corpus_vectors = None
                    return
                vectors.append(vector)

            self._corpus_vectors = vectors
            logger.info(
                "vertex_corpus_embedded",
                size=len(vectors),
                dim=len(vectors[0]) if vectors else 0,
            )

    async def _embed_text(self, text: str) -> list[float] | None:
        if not self._api_key:
            return None

        body = json.dumps(
            {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": text}]},
                "taskType": "SEMANTIC_SIMILARITY",
            }
        ).encode("utf-8")

        url = f"{EMBEDDING_API_URL}?key={self._api_key}"

        def _do_call() -> list[float] | None:
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                values = data.get("embedding", {}).get("values")
                if isinstance(values, list) and values:
                    return [float(v) for v in values]
            except (
                OSError,
                urllib.error.URLError,
                TimeoutError,
                json.JSONDecodeError,
                ValueError,
            ) as exc:
                logger.warning("vertex_embedding_failed", error=str(exc))
            return None

        return await asyncio.to_thread(_do_call)

    @staticmethod
    def _keyword_fallback(
        query: str, top_k: int
    ) -> list[dict[str, Any]]:
        """Score FAQ entries by overlapping keyword count.

        Used when embeddings are unavailable. The score is normalised to the
        [0, 1] range so downstream code can treat it identically to cosine
        similarity values.
        """
        tokens = {tok for tok in _tokenise(query) if len(tok) > 2}
        if not tokens:
            return []

        scored: list[tuple[float, dict[str, str]]] = []
        for entry in FAQ_CORPUS:
            haystack = _tokenise(
                f"{entry['topic']} {entry['question']} {entry['answer']}"
            )
            common = tokens.intersection(haystack)
            if not common:
                continue
            score = len(common) / len(tokens)
            scored.append((score, entry))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {**entry, "score": round(score, 4), "fallback": True}
            for score, entry in scored[:top_k]
        ]


def _tokenise(text: str) -> set[str]:
    return {
        token
        for token in "".join(
            ch.lower() if ch.isalnum() else " " for ch in text
        ).split()
    }


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)

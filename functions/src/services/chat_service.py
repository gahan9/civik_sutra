"""Conversational election coach with native Gemini function calling.

Architecture
------------
The coach exposes five strongly-typed tools to Gemini:

* ``check_voter_eligibility`` — local validation (Constitution Article 326).
* ``lookup_election_faq``    — Vertex AI semantic search on a curated corpus.
* ``find_polling_location``  — Google Maps + ECI fallback.
* ``get_election_timeline``  — static timeline data.
* ``search_candidates``      — candidate intelligence service.

The chat loop follows the standard Gemini function-calling pattern:

1. Send the conversation history + the system prompt + the function
   declarations to ``generateContent``.
2. If the response contains a ``functionCall`` block, execute the matching
   handler locally, append a ``functionResponse`` content part and call
   ``generateContent`` again.
3. The final natural-language reply is returned along with the structured
   tool-call records and citations harvested during the turn.

Every external dependency is wrapped in a graceful-degradation path so the
coach still produces useful output when API keys are absent or upstream
services time out.
"""

from __future__ import annotations

import os
import json
import time
import asyncio
import urllib.error
import urllib.request
from typing import Any

import structlog

from src.services.geo_service import GeoService
from src.data.election_timeline import ELECTION_EVENTS
from src.services.vertex_service import VertexFAQService
from src.services.candidate_service import CandidateService
from src.services.input_sanitiser import sanitise_chat_message
from src.services.eligibility_service import check_voter_eligibility
from src.models.chat import ChatResponse, SourceCitation, ToolCallRecord

logger = structlog.get_logger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
SESSION_TTL_SECONDS = 24 * 60 * 60
MAX_HISTORY_MESSAGES = 10
MAX_FUNCTION_CALL_HOPS = 3

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
}

SYSTEM_PROMPT = """You are CivikSutra, an impartial AI coach for Indian elections.
Your sole purpose is to educate voters about the democratic process, help
them check eligibility, find polling booths, research candidates and
understand the election timeline.

CRITICAL GUARDRAILS:
1. OUT OF SCOPE: Politely refuse anything unrelated to Indian elections,
   civic duties or the democratic process.
2. NO HALLUCINATION: When you do not know an answer based on verified data,
   say so and direct the voter to ECI / NVSP / MyNeta.
3. NEUTRALITY: Never endorse, criticise or recommend any candidate, party
   or ideology. If asked whom to vote for, which party is "best", or for
   a voting recommendation, refuse and explain you only provide neutral
   process education—never suggest a vote choice.
4. STATE AND CYCLE VARIANCE: Deadlines, Form numbers, and procedures can
   differ by state and election type. Always hedge with "confirm on the
   official State CEO / ECI notification for your election" when giving dates.
5. NO LEGAL ADVICE: You are not a lawyer; describe process at a high level
   and point to official portals for binding rules.

TOOL POLICY:
- Always call a tool when the voter asks for live data (booth, candidate,
  timeline, eligibility, deep FAQ search). Do not improvise.
- After the tool returns, integrate the structured response into a clear
  step-by-step answer with citations.
- Keep replies under 250 words and use bullet lists for steps.

CITATION POLICY:
- Cite ECI (eci.gov.in) for procedural facts.
- Cite NVSP (nvsp.in) for registration topics.
- Cite MyNeta (myneta.info) for candidate disclosures.
- Cite the Representation of the People Act for legal references."""

QUICK_QUESTIONS: dict[str, list[str]] = {
    "en": [
        "What documents do I need to carry for voting?",
        "Find my nearest polling booth",
        "Compare candidates in my constituency",
        "How do I apply for a voter ID card?",
        "When is the next election?",
        "Can I vote if I'm in a different city?",
        "What is NOTA and how does it work?",
        "How do EVM machines work?",
    ],
    "hi": [
        "\u0935\u094b\u091f \u0926\u0947\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0915\u094c\u0928 \u0938\u0947 \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c \u091a\u093e\u0939\u093f\u090f?",  # noqa: E501
        "\u092e\u0947\u0930\u093e \u0928\u091c\u0926\u0940\u0915\u0940 \u092e\u0924\u0926\u093e\u0928 \u0915\u0947\u0902\u0926\u094d\u0930 \u0916\u094b\u091c\u0947\u0902",  # noqa: E501
        "\u092e\u0947\u0930\u0947 \u0928\u093f\u0930\u094d\u0935\u093e\u091a\u0928 \u0915\u094d\u0937\u0947\u0924\u094d\u0930 \u0915\u0947 \u0909\u092e\u094d\u092e\u0940\u0926\u0935\u093e\u0930\u094b\u0902 \u0915\u0940 \u0924\u0941\u0932\u0928\u093e \u0915\u0930\u0947\u0902",  # noqa: E501
        "\u092e\u0924\u0926\u093e\u0924\u093e \u092a\u0939\u091a\u093e\u0928 \u092a\u0924\u094d\u0930 \u0915\u0948\u0938\u0947 \u092c\u0928\u0935\u093e\u090f\u0902?",  # noqa: E501
        "\u0905\u0917\u0932\u093e \u091a\u0941\u0928\u093e\u0935 \u0915\u092c \u0939\u0948?",  # noqa: E501
        "\u0915\u094d\u092f\u093e \u092e\u0948\u0902 \u0926\u0942\u0938\u0930\u0947 \u0936\u0939\u0930 \u0938\u0947 \u0935\u094b\u091f \u0915\u0930 \u0938\u0915\u0924\u093e \u0939\u0942\u0901?",  # noqa: E501
        "NOTA \u0915\u094d\u092f\u093e \u0939\u0948 \u0914\u0930 \u0915\u0948\u0938\u0947 \u0915\u093e\u092e \u0915\u0930\u0924\u093e \u0939\u0948?",  # noqa: E501
        "EVM \u092e\u0936\u0940\u0928 \u0915\u0948\u0938\u0947 \u0915\u093e\u092e \u0915\u0930\u0924\u0940 \u0939\u0948?",  # noqa: E501
    ],
}

TOOL_DECLARATIONS: list[dict[str, Any]] = [
    {
        "name": "check_voter_eligibility",
        "description": (
            "Validate whether the voter meets the constitutional and "
            "statutory requirements to register and vote in Indian "
            "elections. Use when the voter asks 'am I eligible?', mentions "
            "their age, NRI status or citizenship, or wants confirmation "
            "before applying for a voter ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "age": {
                    "type": "integer",
                    "description": "Voter's age in completed years.",
                    "minimum": 0,
                    "maximum": 150,
                },
                "citizenship": {
                    "type": "string",
                    "enum": ["indian", "nri", "foreign"],
                    "description": "Citizenship/passport status.",
                },
                "residence": {
                    "type": "string",
                    "enum": ["resident", "nri", "abroad"],
                    "description": "Current residence status.",
                },
            },
            "required": ["age", "citizenship"],
        },
    },
    {
        "name": "lookup_election_faq",
        "description": (
            "Semantic search across the curated FAQ corpus covering "
            "registration, EVMs, NOTA, the Model Code of Conduct, "
            "candidate affidavits, postal ballots, and post-vote engagement. "
            "Use when no other tool is more specific."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The voter's question, paraphrased if helpful.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "find_polling_location",
        "description": (
            "Find polling stations near the voter's current coordinates. "
            "Returns up to three booths with address, distance and travel "
            "time. Use only when latitude/longitude are available."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude in decimal degrees.",
                },
                "lng": {
                    "type": "number",
                    "description": "Longitude in decimal degrees.",
                },
                "radius_km": {
                    "type": "number",
                    "description": "Search radius in kilometres.",
                    "minimum": 0.5,
                    "maximum": 25.0,
                },
            },
            "required": ["lat", "lng"],
        },
    },
    {
        "name": "get_election_timeline",
        "description": (
            "Return the structured election calendar: roll revision, MCC, "
            "nomination, polling phases, counting and the petition window. "
            "Use when the voter asks about dates, deadlines or next steps."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "stage": {
                    "type": "string",
                    "description": (
                        "Optional filter such as 'Polling', 'Nomination', "
                        "'Result' or 'Pre-Election'. Omit for full calendar."
                    ),
                },
            },
        },
    },
    {
        "name": "search_candidates",
        "description": (
            "Look up candidates contesting in the voter's constituency. "
            "Returns names, party, education and asset summary. Use only "
            "when the voter explicitly asks about candidates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Constituency name or candidate keyword.",
                },
            },
            "required": ["query"],
        },
    },
]


class ChatService:
    """Gemini-powered election coach with native function calling."""

    def __init__(
        self,
        gemini_api_key: str | None = None,
        vertex_service: VertexFAQService | None = None,
        geo_service: GeoService | None = None,
        candidate_service: CandidateService | None = None,
    ) -> None:
        self._gemini_api_key = gemini_api_key or os.getenv("EP_GEMINI_API_KEY")
        self._vertex_service = vertex_service or VertexFAQService(self._gemini_api_key)
        self._geo_service = geo_service or GeoService()
        self._candidate_service = candidate_service or CandidateService()
        self._sessions: dict[str, list[dict[str, Any]]] = {}
        self._session_timestamps: dict[str, float] = {}
        self._last_tool_calls: list[ToolCallRecord] = []
        self._last_citations: list[SourceCitation] = []

    async def chat(
        self,
        message: str,
        session_id: str,
        language: str = "en",
        location: dict[str, float] | None = None,
    ) -> ChatResponse:
        """Process one turn in the voter's conversation with the coach."""
        sanitised = sanitise_chat_message(message)
        if not sanitised:
            return ChatResponse(
                response=_generic_fallback(language),
                session_id=session_id,
                citations=[],
                tokens_used=0,
                tool_calls=[],
            )

        history = self._load_history(session_id)
        history.append(_user_part(sanitised))

        self._last_tool_calls = []
        self._last_citations = []

        lang_name = LANGUAGE_NAMES.get(language, "English")
        lang_instruction = (
            f"\nAlways respond in {lang_name}." if language != "en" else ""
        )
        full_system = SYSTEM_PROMPT + lang_instruction
        if location:
            full_system += (
                f"\nVoter's last known location: lat={location['lat']:.4f}, "
                f"lng={location['lng']:.4f}."
            )

        response_text = await self._run_function_calling_loop(full_system, history)

        if not response_text:
            response_text = await self._fallback_with_faq(sanitised, language)

        history.append(_model_part(response_text))
        self._save_history(session_id, history)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            citations=_dedupe_citations(
                self._last_citations + _extract_citations_from_text(response_text)
            ),
            tokens_used=len(response_text.split()),
            tool_calls=list(self._last_tool_calls),
        )

    def get_quick_questions(self, language: str = "en") -> list[str]:
        """Return the localised list of suggested starter questions."""
        return QUICK_QUESTIONS.get(language, QUICK_QUESTIONS["en"])

    def _load_history(self, session_id: str) -> list[dict[str, Any]]:
        ts = self._session_timestamps.get(session_id, 0)
        if time.time() - ts > SESSION_TTL_SECONDS:
            self._sessions.pop(session_id, None)
            self._session_timestamps.pop(session_id, None)
            return []
        history = self._sessions.get(session_id, [])
        return history[-MAX_HISTORY_MESSAGES:]

    def _save_history(
        self, session_id: str, history: list[dict[str, Any]]
    ) -> None:
        self._sessions[session_id] = history[-MAX_HISTORY_MESSAGES:]
        self._session_timestamps[session_id] = time.time()

    async def _run_function_calling_loop(
        self, system_prompt: str, history: list[dict[str, Any]]
    ) -> str:
        if not self._gemini_api_key:
            logger.warning("gemini_api_key_missing_for_chat")
            return ""

        for hop in range(MAX_FUNCTION_CALL_HOPS):
            response = await self._call_gemini(system_prompt, history)
            if response is None:
                return ""

            text_part, function_calls = _split_response(response)
            if function_calls:
                tool_response_parts: list[dict[str, Any]] = []
                history.append({"role": "model", "parts": list(function_calls)})

                for call in function_calls:
                    name = call["functionCall"]["name"]
                    args = call["functionCall"].get("args", {}) or {}
                    result = await self._dispatch_tool(name, args)
                    self._last_tool_calls.append(
                        ToolCallRecord(
                            tool_name=name,
                            args=args,
                            result_summary=_summarise_result(name, result),
                        )
                    )
                    self._collect_citations(name, result)
                    tool_response_parts.append(
                        {
                            "functionResponse": {
                                "name": name,
                                "response": {"result": result},
                            }
                        }
                    )

                history.append({"role": "function", "parts": tool_response_parts})
                continue

            if text_part:
                return text_part

            logger.warning("gemini_loop_terminated_unexpectedly", hop=hop)
            return ""

        logger.warning("gemini_loop_exceeded_max_hops")
        return ""

    async def _call_gemini(
        self, system_prompt: str, history: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        model = "gemini-2.0-flash"
        url = f"{GEMINI_API_URL}/{model}:generateContent?key={self._gemini_api_key}"

        body = json.dumps(
            {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": history,
                "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
                "tool_config": {
                    "function_calling_config": {"mode": "AUTO"}
                },
                "generationConfig": {
                    "temperature": 0.3,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 1024,
                },
                "safetySettings": _SAFETY_SETTINGS,
            }
        ).encode("utf-8")

        def _do_call() -> dict[str, Any] | None:
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except (
                OSError,
                urllib.error.URLError,
                TimeoutError,
                json.JSONDecodeError,
            ) as exc:
                logger.warning("gemini_chat_failed", error=str(exc))
                return None

        return await asyncio.to_thread(_do_call)

    async def _dispatch_tool(
        self, name: str, args: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            if name == "check_voter_eligibility":
                return self._tool_check_eligibility(args)
            if name == "lookup_election_faq":
                return await self._tool_lookup_faq(args)
            if name == "find_polling_location":
                return await self._tool_find_polling(args)
            if name == "get_election_timeline":
                return self._tool_election_timeline(args)
            if name == "search_candidates":
                return await self._tool_search_candidates(args)
        except (ValueError, KeyError, TypeError) as exc:
            logger.exception("tool_execution_failed", tool=name)
            return {"error": f"Tool execution failed: {exc}"}

        return {"error": f"Unknown tool: {name}"}

    @staticmethod
    def _tool_check_eligibility(args: dict[str, Any]) -> dict[str, Any]:
        return dict(
            check_voter_eligibility(
                age=int(args.get("age", 0)),
                citizenship=args.get("citizenship", "indian"),
                residence=args.get("residence", "resident"),
            )
        )

    async def _tool_lookup_faq(self, args: dict[str, Any]) -> dict[str, Any]:
        query = str(args.get("query", "")).strip()
        if not query:
            return {"matches": [], "note": "Empty query."}
        matches = await self._vertex_service.search(query)
        return {"matches": matches, "match_count": len(matches)}

    async def _tool_find_polling(
        self, args: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            lat = float(args["lat"])
            lng = float(args["lng"])
        except (KeyError, TypeError, ValueError):
            return {
                "error": (
                    "Polling-location lookup requires both lat and lng "
                    "coordinates from the user's device."
                )
            }
        radius_km = float(args.get("radius_km", 5.0))
        nearby = await self._geo_service.find_nearby_booths(
            lat=lat, lng=lng, radius_km=radius_km
        )
        return {
            "booths": [b.model_dump() for b in nearby.booths[:3]],
            "suggested_visit_time": nearby.suggested_visit_time.model_dump(),
            "official_verification_url": nearby.official_verification_url,
        }

    @staticmethod
    def _tool_election_timeline(args: dict[str, Any]) -> dict[str, Any]:
        stage = str(args.get("stage", "")).strip().lower()
        events = ELECTION_EVENTS
        if stage:
            events = [e for e in events if stage in e["stage"].lower()]
        return {"events": events, "count": len(events)}

    async def _tool_search_candidates(
        self, args: dict[str, Any]
    ) -> dict[str, Any]:
        query = str(args.get("query", "")).strip()
        if not query:
            return {"error": "Provide a constituency name or candidate keyword."}
        try:
            payload = await self._candidate_service.search_by_constituency(
                constituency=query
            )
        except (RuntimeError, ValueError) as exc:
            logger.warning("candidate_tool_failed", error=str(exc))
            return {"error": "Candidate search is temporarily unavailable."}
        return {
            "constituency": getattr(payload, "constituency", None),
            "candidates": [
                c.model_dump() for c in getattr(payload, "candidates", [])[:5]
            ],
        }

    def _collect_citations(self, tool: str, result: dict[str, Any]) -> None:
        if tool == "lookup_election_faq":
            for match in result.get("matches", []) or []:
                source = match.get("source")
                url = match.get("source_url")
                if source:
                    self._last_citations.append(
                        SourceCitation(source=source, url=url)
                    )
        elif tool == "get_election_timeline":
            for event in result.get("events", []) or []:
                self._last_citations.append(
                    SourceCitation(
                        source=event.get("source", "Election Commission of India"),
                        url=event.get("source_url"),
                    )
                )
        elif tool == "find_polling_location":
            url = result.get("official_verification_url")
            if url:
                self._last_citations.append(
                    SourceCitation(source="Election Commission of India", url=url)
                )

    async def _fallback_with_faq(self, message: str, language: str) -> str:
        try:
            matches = await self._vertex_service.search(message, top_k=1)
        except (RuntimeError, OSError, ValueError):
            matches = []

        if matches:
            top = matches[0]
            self._last_tool_calls.append(
                ToolCallRecord(
                    tool_name="lookup_election_faq",
                    args={"query": message},
                    result_summary=f"Fallback FAQ match: {top.get('id')}",
                )
            )
            self._last_citations.append(
                SourceCitation(
                    source=top.get("source", "Election Commission of India"),
                    url=top.get("source_url"),
                )
            )
            return str(top.get("answer", _generic_fallback(language)))

        return _generic_fallback(language)


def _user_part(message: str) -> dict[str, Any]:
    return {"role": "user", "parts": [{"text": message}]}


def _model_part(message: str) -> dict[str, Any]:
    return {"role": "model", "parts": [{"text": message}]}


def _split_response(
    response: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    candidates = response.get("candidates") or []
    if not candidates:
        return "", []
    parts = candidates[0].get("content", {}).get("parts", []) or []

    text_chunks: list[str] = []
    function_calls: list[dict[str, Any]] = []
    for part in parts:
        if "functionCall" in part:
            function_calls.append({"functionCall": part["functionCall"]})
        elif "text" in part and part["text"]:
            text_chunks.append(part["text"])

    return "\n".join(text_chunks).strip(), function_calls


def _summarise_result(name: str, result: dict[str, Any]) -> str:
    if "error" in result:
        return f"{name}: {result['error']}"
    if name == "check_voter_eligibility":
        return f"eligible={result.get('eligible')}"
    if name == "lookup_election_faq":
        return f"matches={result.get('match_count', 0)}"
    if name == "find_polling_location":
        booths = result.get("booths") or []
        return f"booths={len(booths)}"
    if name == "get_election_timeline":
        return f"events={result.get('count', 0)}"
    if name == "search_candidates":
        candidates = result.get("candidates") or []
        return f"candidates={len(candidates)}"
    return name


def _extract_citations_from_text(text: str) -> list[SourceCitation]:
    citations: list[SourceCitation] = []
    eci_keywords = ["ECI", "Election Commission", "eci.gov.in"]
    nvsp_keywords = ["NVSP", "nvsp.in", "voter registration"]
    myneta_keywords = ["MyNeta", "myneta.info", "affidavit"]

    if any(kw.lower() in text.lower() for kw in eci_keywords):
        citations.append(
            SourceCitation(
                source="Election Commission of India", url="https://eci.gov.in"
            )
        )
    if any(kw.lower() in text.lower() for kw in nvsp_keywords):
        citations.append(
            SourceCitation(source="NVSP Portal", url="https://www.nvsp.in")
        )
    if any(kw.lower() in text.lower() for kw in myneta_keywords):
        citations.append(
            SourceCitation(source="MyNeta.info", url="https://myneta.info")
        )
    return citations


def _dedupe_citations(citations: list[SourceCitation]) -> list[SourceCitation]:
    seen: set[tuple[str, str | None]] = set()
    deduped: list[SourceCitation] = []
    for c in citations:
        key = (c.source, c.url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def _generic_fallback(language: str) -> str:
    if language == "hi":
        return (
            "\u092e\u0948\u0902 \u0907\u0938 \u0938\u092e\u092f \u0907\u0938 "  # noqa: E501
            "\u092a\u094d\u0930\u0936\u094d\u0928 \u0915\u093e \u0909\u0924\u094d\u0924\u0930 "  # noqa: E501
            "\u0928\u0939\u0940\u0902 \u0926\u0947 \u092a\u093e \u0930\u0939\u093e \u0939\u0942\u0901\u0964 "  # noqa: E501
            "\u0915\u0943\u092a\u092f\u093e \u0915\u0941\u091b \u0926\u0947\u0930 \u092c\u093e\u0926 "  # noqa: E501
            "\u092a\u0941\u0928\u0903 \u092a\u094d\u0930\u092f\u093e\u0938 \u0915\u0930\u0947\u0902\u0964 "  # noqa: E501
            "\u0907\u0938 \u092c\u0940\u091a, \u0906\u092a ECI (eci.gov.in) "
            "\u092f\u093e NVSP (nvsp.in) \u092a\u0930 \u091c\u093e \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964"  # noqa: E501
        )
    return (
        "I'm unable to process this question right now. Please try again "
        "in a moment. In the meantime, you can visit ECI (eci.gov.in) or "
        "NVSP (nvsp.in) for authoritative election information."
    )


_SAFETY_SETTINGS: list[dict[str, str]] = [
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

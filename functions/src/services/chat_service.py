from __future__ import annotations

import asyncio
import json
import os
import re
import time
import urllib.request
from typing import Any

import structlog

from src.models.chat import (
    ChatResponse,
    SourceCitation,
    ToolCallRecord,
)

logger = structlog.get_logger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
SESSION_TTL_SECONDS = 24 * 60 * 60
MAX_HISTORY_MESSAGES = 10

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

SYSTEM_PROMPT = """You are CivikSutra, an impartial election education assistant for
Indian elections. Your role is to help voters understand the election process,
find their polling booths, research candidates, and make informed decisions.

Rules:
- Never endorse or recommend any candidate or party
- Always cite sources when stating facts
- If unsure, say so and suggest where to find accurate information
- Keep responses concise but thorough (under 300 words)
- Use the available tools when the user asks about booths or candidates
- For voter registration questions, point to NVSP (nvsp.in) and ECI
- For candidate info, reference MyNeta.info and ECI affidavits
- For election dates/phases, reference ECI official announcements

Available knowledge domains:
1. Voter registration (EPIC, Form 6, NVSP portal)
2. Voting procedure (EVM, VVPAT, queue protocol)
3. Election timeline and phases
4. Candidate information and comparison
5. Rights and rules (Model Code of Conduct, RTI, NOTA)
6. Results and counting process
7. Polling booth discovery and directions"""

QUICK_QUESTIONS: dict[str, list[str]] = {
    "en": [
        "What documents do I need to carry for voting?",
        "Find my nearest polling booth",
        "Compare candidates in my constituency",
        "How do I apply for a voter ID card?",
        "When is the election in my state?",
        "Can I vote if I'm in a different city?",
        "What is NOTA and how does it work?",
        "How do EVM machines work?",
    ],
    "hi": [
        "\u0935\u094b\u091f \u0926\u0947\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0915\u094c\u0928 \u0938\u0947 \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c \u091a\u093e\u0939\u093f\u090f?",
        "\u092e\u0947\u0930\u093e \u0928\u091c\u0926\u0940\u0915\u0940 \u092e\u0924\u0926\u093e\u0928 \u0915\u0947\u0902\u0926\u094d\u0930 \u0916\u094b\u091c\u0947\u0902",
        "\u092e\u0947\u0930\u0947 \u0928\u093f\u0930\u094d\u0935\u093e\u091a\u0928 \u0915\u094d\u0937\u0947\u0924\u094d\u0930 \u0915\u0947 \u0909\u092e\u094d\u092e\u0940\u0926\u0935\u093e\u0930\u094b\u0902 \u0915\u0940 \u0924\u0941\u0932\u0928\u093e \u0915\u0930\u0947\u0902",
        "\u092e\u0924\u0926\u093e\u0924\u093e \u092a\u0939\u091a\u093e\u0928 \u092a\u0924\u094d\u0930 \u0915\u0948\u0938\u0947 \u092c\u0928\u0935\u093e\u090f\u0902?",
        "\u092e\u0947\u0930\u0947 \u0930\u093e\u091c\u094d\u092f \u092e\u0947\u0902 \u091a\u0941\u0928\u093e\u0935 \u0915\u092c \u0939\u0948?",
        "\u0915\u094d\u092f\u093e \u092e\u0948\u0902 \u0926\u0942\u0938\u0930\u0947 \u0936\u0939\u0930 \u0938\u0947 \u0935\u094b\u091f \u0915\u0930 \u0938\u0915\u0924\u093e \u0939\u0942\u0901?",
        "NOTA \u0915\u094d\u092f\u093e \u0939\u0948 \u0914\u0930 \u0915\u0948\u0938\u0947 \u0915\u093e\u092e \u0915\u0930\u0924\u093e \u0939\u0948?",
        "EVM \u092e\u0936\u0940\u0928 \u0915\u0948\u0938\u0947 \u0915\u093e\u092e \u0915\u0930\u0924\u0940 \u0939\u0948?",
    ],
}


class ChatService:
    """Gemini-powered election assistant with conversation memory."""

    def __init__(self, gemini_api_key: str | None = None) -> None:
        self._gemini_api_key = gemini_api_key or os.getenv("EP_GEMINI_API_KEY")
        self._sessions: dict[str, list[dict[str, str]]] = {}
        self._session_timestamps: dict[str, float] = {}

    async def chat(
        self,
        message: str,
        session_id: str,
        language: str = "en",
    ) -> ChatResponse:
        history = self._load_history(session_id)
        history.append({"role": "user", "content": message})

        lang_name = LANGUAGE_NAMES.get(language, "English")
        lang_instruction = (
            f"\nAlways respond in {lang_name}." if language != "en" else ""
        )
        full_system = SYSTEM_PROMPT + lang_instruction

        response_text = await self._call_gemini(full_system, history)

        if not response_text:
            response_text = self._fallback_response(message, language)

        citations = self._extract_citations(response_text)
        tool_calls = self._detect_tool_intents(message)

        history.append({"role": "assistant", "content": response_text})
        self._save_history(session_id, history)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            citations=citations,
            tokens_used=len(response_text.split()),
            tool_calls=tool_calls,
        )

    def get_quick_questions(self, language: str = "en") -> list[str]:
        return QUICK_QUESTIONS.get(language, QUICK_QUESTIONS["en"])

    def _load_history(self, session_id: str) -> list[dict[str, str]]:
        ts = self._session_timestamps.get(session_id, 0)
        if time.time() - ts > SESSION_TTL_SECONDS:
            self._sessions.pop(session_id, None)
            self._session_timestamps.pop(session_id, None)
            return []

        history = self._sessions.get(session_id, [])
        return history[-MAX_HISTORY_MESSAGES:]

    def _save_history(
        self, session_id: str, history: list[dict[str, str]],
    ) -> None:
        self._sessions[session_id] = history[-MAX_HISTORY_MESSAGES:]
        self._session_timestamps[session_id] = time.time()

    async def _call_gemini(
        self,
        system_prompt: str,
        history: list[dict[str, str]],
    ) -> str:
        if not self._gemini_api_key:
            logger.warning("gemini_api_key_missing_for_chat")
            return ""

        model = "gemini-2.0-flash"
        url = (
            f"{GEMINI_API_URL}/{model}:generateContent"
            f"?key={self._gemini_api_key}"
        )

        contents: list[dict[str, Any]] = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })

        body = json.dumps({
            "system_instruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 1024,
            },
            "safetySettings": [
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
            ],
        }).encode("utf-8")

        def _do_call() -> str:
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            except (OSError, TimeoutError, json.JSONDecodeError) as exc:
                logger.warning("gemini_chat_failed", error=str(exc))
            return ""

        return await asyncio.to_thread(_do_call)

    @staticmethod
    def _extract_citations(text: str) -> list[SourceCitation]:
        citations: list[SourceCitation] = []
        eci_keywords = ["ECI", "Election Commission", "eci.gov.in"]
        nvsp_keywords = ["NVSP", "nvsp.in", "voter registration"]
        myneta_keywords = ["MyNeta", "myneta.info", "affidavit"]

        if any(kw.lower() in text.lower() for kw in eci_keywords):
            citations.append(
                SourceCitation(source="Election Commission of India", url="https://eci.gov.in"),
            )
        if any(kw.lower() in text.lower() for kw in nvsp_keywords):
            citations.append(
                SourceCitation(source="NVSP Portal", url="https://www.nvsp.in"),
            )
        if any(kw.lower() in text.lower() for kw in myneta_keywords):
            citations.append(
                SourceCitation(source="MyNeta.info", url="https://myneta.info"),
            )
        return citations

    @staticmethod
    def _detect_tool_intents(message: str) -> list[ToolCallRecord]:
        tool_calls: list[ToolCallRecord] = []
        lower = message.lower()

        booth_keywords = ["polling booth", "booth", "where do i vote", "nearest booth"]
        if any(kw in lower for kw in booth_keywords):
            tool_calls.append(ToolCallRecord(
                tool_name="booth_finder",
                args={},
                result_summary="Use the Booth Finder tab for GPS-based booth discovery",
            ))

        candidate_keywords = ["candidate", "who is contesting", "compare candidates"]
        if any(kw in lower for kw in candidate_keywords):
            tool_calls.append(ToolCallRecord(
                tool_name="candidate_search",
                args={},
                result_summary="Use the Candidate Intelligence tab for detailed search",
            ))

        return tool_calls

    @staticmethod
    def _fallback_response(message: str, language: str) -> str:
        if language == "hi":
            return (
                "\u092e\u0948\u0902 \u0907\u0938 \u0938\u092e\u092f \u0907\u0938 \u092a\u094d\u0930\u0936\u094d\u0928 \u0915\u093e "
                "\u0909\u0924\u094d\u0924\u0930 \u0928\u0939\u0940\u0902 \u0926\u0947 \u092a\u093e \u0930\u0939\u093e \u0939\u0942\u0901\u0964 "
                "\u0915\u0943\u092a\u092f\u093e \u0915\u0941\u091b \u0926\u0947\u0930 \u092c\u093e\u0926 \u092a\u0941\u0928\u0903 \u092a\u094d\u0930\u092f\u093e\u0938 \u0915\u0930\u0947\u0902\u0964 "
                "\u0907\u0938 \u092c\u0940\u091a, \u0906\u092a ECI (eci.gov.in) \u092f\u093e NVSP (nvsp.in) "
                "\u092a\u0930 \u091c\u093e \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964"
            )
        return (
            "I'm unable to process this question right now. Please try again "
            "in a moment. In the meantime, you can visit ECI (eci.gov.in) or "
            "NVSP (nvsp.in) for authoritative election information."
        )

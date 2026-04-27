from __future__ import annotations


from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models.booth import LatLng


class StrictModel(BaseModel):
    """Model or service class for StrictModel."""

    model_config = ConfigDict(extra="forbid")


SupportedLanguage = Literal[
    "en",
    "hi",
    "ta",
    "te",
    "bn",
    "mr",
    "gu",
    "kn",
    "ml",
]


class ChatRequest(StrictModel):
    """Model or service class for ChatRequest."""

    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(min_length=1, max_length=128)
    language: SupportedLanguage = "en"
    location: LatLng | None = None


class ChatEvent(BaseModel):
    """Model or service class for ChatEvent."""

    event: Literal["token", "tool_call", "tool_result", "citation", "done"]
    data: dict[str, Any]


class SourceCitation(BaseModel):
    """Model or service class for SourceCitation."""

    source: str
    url: str | None = None


class ToolCallRecord(BaseModel):
    """Model or service class for ToolCallRecord."""

    tool_name: str
    args: dict[str, Any]
    result_summary: str


class ConversationMessage(BaseModel):
    """Model or service class for ConversationMessage."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    citations: list[SourceCitation] | None = None
    tool_calls: list[ToolCallRecord] | None = None


class ChatResponse(BaseModel):
    """Non-streaming response for environments that don't support SSE."""

    response: str
    session_id: str
    citations: list[SourceCitation] = Field(default_factory=list)
    tokens_used: int = 0
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)

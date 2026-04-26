from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ManifestoCompareRequest(StrictModel):
    party_names: list[str] = Field(min_length=2, max_length=4)
    categories: list[str] | None = None
    include_past_promises: bool = True


class ManifestoSource(StrictModel):
    party: str
    manifesto_url: str | None = None


class ManifestoData(StrictModel):
    party_name: str
    election_year: int = 2024
    categories: dict[str, list[str]] = Field(default_factory=dict)
    summary: str = ""
    full_text_url: str | None = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


PromiseStatus = Literal["fulfilled", "partial", "not_met", "ongoing"]


class PromiseTracker(StrictModel):
    promise: str
    status: PromiseStatus
    evidence: str
    source: str


class ManifestoComparison(StrictModel):
    parties: list[str]
    categories: dict[str, dict[str, list[str]]]
    ai_analysis: str
    past_promises: dict[str, list[PromiseTracker]] | None = None
    sources: list[ManifestoSource] = Field(default_factory=list)

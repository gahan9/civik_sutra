from __future__ import annotations


from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """Model or service class for StrictModel."""

    model_config = ConfigDict(extra="forbid")


Sentiment = Literal["positive", "negative", "neutral"]


class CandidateSearchRequest(StrictModel):
    """Search by constituency name or GPS coordinates (one required)."""

    constituency: str | None = Field(default=None, min_length=2, max_length=200)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def require_one_search_method(self) -> Self:
        """Execute require_one_search_method operation."""
        if not self.constituency and (self.lat is None or self.lng is None):
            raise ValueError("Provide constituency name or both lat/lng coordinates")
        return self


class CompareRequest(StrictModel):
    """Model or service class for CompareRequest."""

    candidate_ids: list[str] = Field(min_length=2, max_length=4)


class CandidateSummary(StrictModel):
    """Model or service class for CandidateSummary."""

    id: str
    name: str
    party: str
    party_symbol_url: str | None = None
    education: str
    age: int | None = None
    criminal_cases: int = 0
    total_assets_inr: int = 0
    total_liabilities_inr: int = 0
    past_positions: list[str] = Field(default_factory=list)


class NewsItem(StrictModel):
    """Model or service class for NewsItem."""

    title: str
    source: str
    date: str
    url: str | None = None
    sentiment: Sentiment = "neutral"


class SourceCitation(StrictModel):
    """Model or service class for SourceCitation."""

    source: str
    url: str | None = None
    query: str | None = None


class GroundingResult(StrictModel):
    """Model or service class for GroundingResult."""

    recent_news: list[NewsItem] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    controversies: list[str] = Field(default_factory=list)
    social_media_presence: str | None = None
    sources: list[SourceCitation] = Field(default_factory=list)


class CriminalCase(StrictModel):
    """Model or service class for CriminalCase."""

    case_id: str | None = None
    description: str
    status: Literal["pending", "convicted", "acquitted"] = "pending"
    court: str | None = None
    ipc_sections: list[str] = Field(default_factory=list)


class AssetBreakdown(StrictModel):
    """Model or service class for AssetBreakdown."""

    movable: int = 0
    immovable: int = 0
    vehicles: list[str] = Field(default_factory=list)


class BackgroundReport(StrictModel):
    """Model or service class for BackgroundReport."""

    candidate: CandidateSummary
    grounding: GroundingResult
    criminal_details: list[CriminalCase] = Field(default_factory=list)
    asset_breakdown: AssetBreakdown = Field(default_factory=AssetBreakdown)
    source_urls: dict[str, str] = Field(default_factory=dict)


class ComparisonResult(StrictModel):
    """Model or service class for ComparisonResult."""

    dimensions: list[str]
    candidates: dict[str, dict[str, str]]
    ai_analysis: str
    ai_analysis_citations: list[SourceCitation] = Field(default_factory=list)


class CandidateSearchResponse(StrictModel):
    """Model or service class for CandidateSearchResponse."""

    constituency: str
    election: str = "General Election"
    candidates: list[CandidateSummary]


class RawCandidateData(StrictModel):
    """Scraped data before normalization."""

    model_config = ConfigDict(extra="ignore")

    name: str
    party: str = "Independent"
    education: str = "Not declared"
    age: int | None = None
    criminal_cases: int = 0
    total_assets_inr: int = 0
    total_liabilities_inr: int = 0


class AffidavitData(StrictModel):
    """Model or service class for AffidavitData."""

    candidate_name: str
    constituency: str
    criminal_cases: list[CriminalCase] = Field(default_factory=list)
    assets: AssetBreakdown = Field(default_factory=AssetBreakdown)
    education: str = "Not declared"

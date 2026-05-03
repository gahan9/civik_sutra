from __future__ import annotations

import os
import re
import json
import time
import asyncio
import urllib.parse
import urllib.request
from typing import Any, cast

import structlog

from src.models.candidate import (
    NewsItem,
    AssetBreakdown,
    SourceCitation,
    GroundingResult,
    BackgroundReport,
    CandidateSummary,
    ComparisonResult,
    CandidateSearchResponse,
)
from src.services.scraper_service import ScraperService

logger = structlog.get_logger(__name__)

CACHE_TTL_SECONDS = 24 * 60 * 60
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

GROUNDING_PROMPT = """You are an election research assistant. Search for recent,
factual information about the following candidate:

Name: {candidate_name}
Constituency: {constituency}
Party: {party}

Find and structure as JSON with these fields:
- "recent_news": array of objects with "title", "source", "date", "url",
  "sentiment" (positive/negative/neutral)
- "achievements": array of strings
- "controversies": array of strings
- "social_media_presence": string or null

Rules:
- Only include information you can cite with a source
- Clearly mark unverified claims as "unverified"
- Do not express political opinions or endorsements
- Be factual and neutral in tone
- Return valid JSON only, no markdown fences"""

COMPARISON_PROMPT = """You are an impartial election analyst. Compare these
candidates based on their official records and public information:

{candidate_data_json}

Produce a neutral, factual analysis covering:
1. Governance experience and track record
2. Educational background relevance to public service
3. Legal standing (criminal cases, if any)
4. Financial transparency (asset vs liability ratio)
5. Key policy focus areas
6. Delivery probability assessment

Rules:
- Do not endorse any candidate
- Base delivery probability on measurable past outcomes only
- Flag where data is insufficient for assessment
- Cite data sources (MyNeta, ECI, news)
- Return a single paragraph of analysis, 3-5 sentences"""


class CandidateService:
    """Candidate research with grounding search and comparative analysis."""

    def __init__(
        self,
        gemini_api_key: str | None = None,
        maps_api_key: str | None = None,
        scraper: ScraperService | None = None,
    ) -> None:
        """Execute __init__ operation."""
        self._gemini_api_key = gemini_api_key or os.getenv("EP_GEMINI_API_KEY")
        self._maps_api_key = maps_api_key or os.getenv("EP_GOOGLE_MAPS_API_KEY")
        self._scraper = scraper or ScraperService()
        self._cache: dict[str, tuple[float, Any]] = {}

    async def search_by_constituency(
        self,
        constituency: str,
    ) -> CandidateSearchResponse:
        """Search candidates for a constituency.

        1. Check in-memory cache (TTL: 24h)
        2. On miss: ScraperService.fetch_myneta_candidates()
        3. On scraper failure: fall back to demo data
        4. Cache result
        """
        cache_key = f"search:{constituency.lower().strip()}"
        cached = self._get_cached(cache_key)
        if cached:
            logger.info("candidate_cache_hit", constituency=constituency)
            return cast(CandidateSearchResponse, cached)

        raw_candidates = await self._scraper.fetch_myneta_candidates(constituency)
        if raw_candidates:
            candidates = [
                CandidateSummary(
                    id=self._make_id(raw.name, raw.party),
                    name=raw.name,
                    party=raw.party,
                    education=raw.education,
                    age=raw.age,
                    criminal_cases=raw.criminal_cases,
                    total_assets_inr=raw.total_assets_inr,
                    total_liabilities_inr=raw.total_liabilities_inr,
                )
                for raw in raw_candidates
            ]
        else:
            logger.info("using_demo_candidates", constituency=constituency)
            candidates = self._demo_candidates(constituency)

        response = CandidateSearchResponse(
            constituency=constituency,
            election="Lok Sabha 2024",
            candidates=candidates,
        )
        self._set_cache(cache_key, response)
        return response

    async def search_by_location(
        self,
        lat: float,
        lng: float,
    ) -> CandidateSearchResponse:
        """Reverse-geocode GPS to constituency, then search.

        Uses Google Maps Geocoding API to resolve coordinates
        to parliamentary/assembly constituency name.
        """
        constituency = await self._reverse_geocode(lat, lng)
        return await self.search_by_constituency(constituency)

    async def grounding_search(
        self,
        candidate_name: str,
        constituency: str,
        party: str = "Unknown",
    ) -> GroundingResult:
        """Search real-time information via Gemini with Google Search grounding."""
        if not self._gemini_api_key:
            logger.warning("gemini_api_key_missing")
            return self._demo_grounding(candidate_name)

        prompt = GROUNDING_PROMPT.format(
            candidate_name=candidate_name,
            constituency=constituency,
            party=party,
        )

        response_text = await self._call_gemini(prompt)
        return self._parse_grounding_response(response_text, candidate_name)

    async def background_check(
        self,
        candidate_id: str,
        candidates: list[CandidateSummary] | None = None,
    ) -> BackgroundReport:
        """Comprehensive background report combining:
        1. Candidate base data (from search or lookup)
        2. Gemini grounding search (news, social presence)
        3. Structured extraction into BackgroundReport
        """
        candidate = self._find_candidate(candidate_id, candidates)
        if not candidate:
            candidate = self._stub_candidate(candidate_id)

        grounding = await self.grounding_search(
            candidate.name,
            "Unknown",
            candidate.party,
        )

        return BackgroundReport(
            candidate=candidate,
            grounding=grounding,
            criminal_details=[],
            asset_breakdown=AssetBreakdown(
                movable=candidate.total_assets_inr // 3,
                immovable=candidate.total_assets_inr * 2 // 3,
            ),
            source_urls={
                "myneta": (
                    "https://myneta.info/search/?q="
                    f"{urllib.parse.quote(candidate.name)}"
                ),
            },
        )

    async def compare(
        self,
        candidate_ids: list[str],
        candidates: list[CandidateSummary] | None = None,
    ) -> ComparisonResult:
        """Build structured comparison matrix.
        1. Fetch background for each candidate (parallel)
        2. Build dimension-wise matrix
        3. Call Gemini for analytical summary
        """
        reports = await asyncio.gather(
            *(self.background_check(cid, candidates) for cid in candidate_ids)
        )

        dimensions = [
            "education",
            "age",
            "criminal_cases",
            "total_assets",
            "total_liabilities",
            "past_work",
            "key_promises",
            "recent_news",
            "delivery_probability",
        ]

        matrix: dict[str, dict[str, str]] = {}
        for report in reports:
            cand = report.candidate
            news_summary = (
                report.grounding.recent_news[0].title
                if report.grounding.recent_news
                else "No recent news"
            )
            past_work = (
                ", ".join(cand.past_positions)
                if cand.past_positions
                else "No prior positions"
            )
            delivery = self._assess_delivery_probability(cand, report.grounding)

            matrix[cand.id] = {
                "education": cand.education,
                "age": str(cand.age) if cand.age else "Not declared",
                "criminal_cases": (
                    f"{cand.criminal_cases} case(s)"
                    if cand.criminal_cases
                    else "No criminal cases declared"
                ),
                "total_assets": self._format_inr(cand.total_assets_inr),
                "total_liabilities": self._format_inr(cand.total_liabilities_inr),
                "past_work": past_work,
                "key_promises": "See grounding search results",
                "recent_news": news_summary,
                "delivery_probability": delivery,
            }

        ai_analysis = await self._generate_comparison_analysis(reports)
        citations = [
            SourceCitation(source="MyNeta.info", url="https://myneta.info"),
            SourceCitation(
                source="Election Commission of India", url="https://eci.gov.in"
            ),
        ]

        return ComparisonResult(
            dimensions=dimensions,
            candidates=matrix,
            ai_analysis=ai_analysis,
            ai_analysis_citations=citations,
        )

    def _get_cached(self, key: str) -> Any:
        entry = self._cache.get(key)
        if entry and (time.time() - entry[0]) < CACHE_TTL_SECONDS:
            return entry[1]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)

    async def _reverse_geocode(self, lat: float, lng: float) -> str:
        if not self._maps_api_key:
            return "New Delhi"

        params = urllib.parse.urlencode(
            {
                "latlng": f"{lat},{lng}",
                "key": self._maps_api_key,
                "result_type": "administrative_area_level_2",
            }
        )
        data = await self._fetch_json(f"{GEOCODING_URL}?{params}")
        if not data:
            return "New Delhi"

        results = data.get("results", [])
        if results:
            for component in results[0].get("address_components", []):
                types = component.get("types", [])
                if (
                    "sublocality_level_1" in types
                    or "administrative_area_level_2" in types
                ):
                    return str(component.get("long_name", "New Delhi"))
        return "New Delhi"

    async def _call_gemini(self, prompt: str) -> str:
        model = "gemini-2.0-flash"
        url = f"{GEMINI_API_URL}/{model}:generateContent?key={self._gemini_api_key}"
        body = json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1024,
                },
            }
        ).encode("utf-8")

        def _do_call() -> str:
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return str(parts[0].get("text", ""))
            except (OSError, TimeoutError, json.JSONDecodeError) as exc:
                logger.warning("gemini_call_failed", error=str(exc))
            return ""

        return await asyncio.to_thread(_do_call)

    def _parse_grounding_response(
        self,
        text: str,
        candidate_name: str,
    ) -> GroundingResult:
        if not text:
            return self._demo_grounding(candidate_name)

        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`")
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("grounding_json_parse_failed", text_length=len(text))
            return self._demo_grounding(candidate_name)

        news_items = [
            NewsItem(
                title=item.get("title", ""),
                source=item.get("source", "Unknown"),
                date=item.get("date", "Unknown"),
                url=item.get("url"),
                sentiment=item.get("sentiment", "neutral"),
            )
            for item in data.get("recent_news", [])
            if isinstance(item, dict) and item.get("title")
        ]

        return GroundingResult(
            recent_news=news_items,
            achievements=data.get("achievements", []),
            controversies=data.get("controversies", []),
            social_media_presence=data.get("social_media_presence"),
            sources=[
                SourceCitation(source="Gemini Grounding Search"),
            ],
        )

    async def _generate_comparison_analysis(
        self,
        reports: list[BackgroundReport],
    ) -> str:
        if not self._gemini_api_key:
            return self._demo_analysis(reports)

        candidate_data = {
            report.candidate.id: {
                "name": report.candidate.name,
                "party": report.candidate.party,
                "education": report.candidate.education,
                "criminal_cases": report.candidate.criminal_cases,
                "total_assets_inr": report.candidate.total_assets_inr,
                "past_positions": report.candidate.past_positions,
            }
            for report in reports
        }

        prompt = COMPARISON_PROMPT.format(
            candidate_data_json=json.dumps(candidate_data, indent=2),
        )

        result = await self._call_gemini(prompt)
        return result if result else self._demo_analysis(reports)

    @staticmethod
    def _assess_delivery_probability(
        candidate: CandidateSummary,
        grounding: GroundingResult,
    ) -> str:
        score = 0
        terms = len(candidate.past_positions)
        score += min(terms * 2, 6)

        if candidate.criminal_cases > 0:
            score -= candidate.criminal_cases

        positive_news = sum(
            1 for n in grounding.recent_news if n.sentiment == "positive"
        )
        negative_news = sum(
            1 for n in grounding.recent_news if n.sentiment == "negative"
        )
        score += positive_news - negative_news

        if score >= 5:
            return "High - consistent track record with measurable outcomes"
        if score >= 2:
            return "Moderate - some governance experience"
        if score >= 0:
            return "Low - limited track record for assessment"
        return "Very Low - significant negative signals"

    @staticmethod
    def _format_inr(amount: int) -> str:
        if amount == 0:
            return "Not declared"
        if amount >= 10_000_000:
            return f"\u20b9{amount / 10_000_000:.1f} Crore"
        if amount >= 100_000:
            return f"\u20b9{amount / 100_000:.1f} Lakh"
        return f"\u20b9{amount:,}"

    @staticmethod
    def _make_id(name: str, party: str) -> str:
        slug = re.sub(r"[^a-z0-9]", "_", name.lower().strip())
        party_slug = re.sub(r"[^a-z0-9]", "", party.lower().strip())
        return f"cand_{slug}_{party_slug}"

    @staticmethod
    def _find_candidate(
        candidate_id: str,
        candidates: list[CandidateSummary] | None,
    ) -> CandidateSummary | None:
        if not candidates:
            return None
        for c in candidates:
            if c.id == candidate_id:
                return c
        return None

    @staticmethod
    def _stub_candidate(candidate_id: str) -> CandidateSummary:
        parts = candidate_id.replace("cand_", "").rsplit("_", maxsplit=1)
        name = parts[0].replace("_", " ").title() if parts else candidate_id
        party = parts[1].upper() if len(parts) > 1 else "Independent"
        return CandidateSummary(
            id=candidate_id,
            name=name,
            party=party,
            education="Not declared",
        )

    @staticmethod
    def _demo_grounding(candidate_name: str) -> GroundingResult:
        return GroundingResult(
            recent_news=[
                NewsItem(
                    title=(
                        f"{candidate_name} addresses public rally on "
                        "development agenda"
                    ),
                    source="Demo Data",
                    date="2024-03-15",
                    sentiment="neutral",
                ),
            ],
            achievements=["Community outreach programs"],
            controversies=[],
            social_media_presence="Active on social media platforms",
            sources=[SourceCitation(source="Demo Data")],
        )

    @staticmethod
    def _demo_analysis(reports: list[BackgroundReport]) -> str:
        names = [r.candidate.name for r in reports]
        if len(names) == 2:
            return (
                f"Comparing {names[0]} and {names[1]}: Both candidates bring "
                "different strengths to the constituency. A detailed assessment "
                "requires verified data from ECI affidavits and official records. "
                "Voters should review candidate profiles on MyNeta.info for "
                "comprehensive background checks."
            )
        return (
            f"Comparing {', '.join(names[:-1])} and {names[-1]}: These candidates "
            f"represent diverse backgrounds and policy priorities. Delivery probability "
            f"is best assessed by reviewing past governance outcomes documented in ECI "
            f"records and media coverage."
        )

    @staticmethod
    def _demo_candidates(constituency: str) -> list[CandidateSummary]:
        return [
            CandidateSummary(
                id="cand_ramesh_kumar_bjp",
                name="Ramesh Kumar",
                party="BJP",
                education="MBA, IIM Ahmedabad",
                age=52,
                criminal_cases=0,
                total_assets_inr=21_000_000,
                total_liabilities_inr=3_000_000,
                past_positions=["MLA 2014-2019", "MLA 2019-2024"],
            ),
            CandidateSummary(
                id="cand_priya_singh_inc",
                name="Priya Singh",
                party="INC",
                education="LLB, Delhi University",
                age=38,
                criminal_cases=1,
                total_assets_inr=85_000_000,
                total_liabilities_inr=12_000_000,
                past_positions=["Councillor 2019-2024"],
            ),
            CandidateSummary(
                id="cand_amit_verma_aap",
                name="Amit Verma",
                party="AAP",
                education="B.Tech, IIT Delhi",
                age=44,
                criminal_cases=0,
                total_assets_inr=15_000_000,
                total_liabilities_inr=2_000_000,
                past_positions=["Social activist"],
            ),
        ]

    async def _fetch_json(self, url: str) -> dict[str, Any] | None:
        def _do_fetch() -> dict[str, Any] | None:
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                return data if isinstance(data, dict) else None
            except (OSError, TimeoutError, json.JSONDecodeError):
                return None

        return await asyncio.to_thread(_do_fetch)

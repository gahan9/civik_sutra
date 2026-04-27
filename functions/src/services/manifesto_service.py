from __future__ import annotations

import os
import re
import json
import time
import asyncio
import urllib.request
from typing import Any, cast

import structlog

from src.models.manifesto import (
    ManifestoData,
    PromiseTracker,
    ManifestoSource,
    ManifestoComparison,
)

logger = structlog.get_logger(__name__)

CACHE_TTL_SECONDS = 7 * 24 * 60 * 60
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MANIFESTO_CATEGORIES = [
    "economy",
    "education",
    "healthcare",
    "infrastructure",
    "defense",
    "social_welfare",
    "environment",
    "governance",
]

EXTRACTION_PROMPT = """You are a political analyst. Extract the key promises and policy positions from
this party's manifesto into structured categories.

Party: {party_name}

Extract promises into these categories:
1. Economy & Employment
2. Education
3. Healthcare
4. Infrastructure & Urban Development
5. Defense & Security
6. Social Welfare & Inclusion
7. Environment & Climate
8. Governance & Anti-corruption

For each category, list 2-5 specific, measurable promises.
If no promises exist for a category, mark as "Not addressed".

Return valid JSON with category keys: economy, education, healthcare, infrastructure,
defense, social_welfare, environment, governance. Each key maps to an array of strings.

Rules:
- Extract exact commitments, not vague statements
- Prefer quantified promises (amounts, timelines, targets)
- Be factual -- do not interpret or editorialize
- Return valid JSON only, no markdown fences"""

COMPARISON_PROMPT = """You are an impartial political analyst. Compare the manifesto promises
of these parties:

{manifesto_data_json}

Provide a 3-5 sentence neutral analysis covering:
1. Key philosophical differences between the parties
2. Where they agree on policy direction
3. Most distinctive promise from each party
4. Overall approach (welfare vs growth, centralized vs decentralized)

Rules:
- Do not endorse or favor any party
- Be factual and cite specific promises
- Mention both strengths and gaps
- Return plain text analysis only, no JSON"""

PROMISE_TRACKING_PROMPT = """You are a fact-checker. For each promise made by {party_name} in their
{election_year} manifesto, search for evidence of delivery.

Promises:
{promises_json}

For each promise, determine:
1. Status: fulfilled / partial / not_met / ongoing
2. Evidence: specific data, statistics, or reports
3. Source: news article, government report, or official data

Return valid JSON as an array of objects with "promise", "status", "evidence", "source" fields.

Rules:
- Only use verifiable sources
- "Partial" means measurable progress but target not fully met
- "Ongoing" means active implementation with no deadline passed
- Do not speculate on intent; only assess outcomes
- Return valid JSON only, no markdown fences"""


class ManifestoService:
    """Party manifesto comparison with AI-powered extraction and analysis."""

    def __init__(self, gemini_api_key: str | None = None) -> None:
        """Execute __init__ operation."""
        self._gemini_api_key = gemini_api_key or os.getenv("EP_GEMINI_API_KEY")
        self._cache: dict[str, tuple[float, Any]] = {}

    async def compare_manifestos(
        self,
        party_names: list[str],
        categories: list[str] | None = None,
        include_past_promises: bool = True,
    ) -> ManifestoComparison:
        """Execute compare_manifestos operation."""
        manifesto_tasks = [self.fetch_manifesto(party) for party in party_names]
        manifestos = await asyncio.gather(*manifesto_tasks)

        aligned = self._align_categories(manifestos, categories)

        analysis = await self._generate_analysis(manifestos)

        past_promises: dict[str, list[PromiseTracker]] | None = None
        if include_past_promises:
            incumbent_parties = self._identify_incumbents(party_names)
            if incumbent_parties:
                promise_tasks = [
                    self.track_past_promises(party, 2019) for party in incumbent_parties
                ]
                results = await asyncio.gather(*promise_tasks)
                past_promises = dict(zip(incumbent_parties, results))

        sources = [
            ManifestoSource(
                party=m.party_name,
                manifesto_url=m.full_text_url,
            )
            for m in manifestos
        ]

        return ManifestoComparison(
            parties=party_names,
            categories=aligned,
            ai_analysis=analysis,
            past_promises=past_promises,
            sources=sources,
        )

    async def fetch_manifesto(self, party_name: str) -> ManifestoData:
        """Execute fetch_manifesto operation."""
        cache_key = f"manifesto:{party_name.lower().strip()}"
        cached = self._get_cached(cache_key)
        if cached:
            logger.info("manifesto_cache_hit", party=party_name)
            return cast(ManifestoData, cached)

        if self._gemini_api_key:
            prompt = EXTRACTION_PROMPT.format(party_name=party_name)
            response_text = await self._call_gemini(prompt)
            categories = self._parse_categories(response_text)
        else:
            categories = self._demo_manifesto_data(party_name)

        manifesto = ManifestoData(
            party_name=party_name,
            categories=categories,
            summary=f"Manifesto analysis for {party_name}",
            full_text_url=self._get_manifesto_url(party_name),
        )
        self._set_cache(cache_key, manifesto)
        return manifesto

    async def track_past_promises(
        self,
        party_name: str,
        election_year: int,
    ) -> list[PromiseTracker]:
        """Execute track_past_promises operation."""
        cache_key = f"promises:{party_name.lower()}:{election_year}"
        cached = self._get_cached(cache_key)
        if cached:
            return cast(list[PromiseTracker], cached)

        if self._gemini_api_key:
            past_data = self._demo_past_promises(party_name)
            promises_json = json.dumps(
                [p.promise for p in past_data],
            )
            prompt = PROMISE_TRACKING_PROMPT.format(
                party_name=party_name,
                election_year=election_year,
                promises_json=promises_json,
            )
            response_text = await self._call_gemini(prompt)
            promises = self._parse_promises(response_text, party_name)
        else:
            promises = self._demo_past_promises(party_name)

        self._set_cache(cache_key, promises)
        return promises

    def _align_categories(
        self,
        manifestos: list[ManifestoData],
        filter_categories: list[str] | None,
    ) -> dict[str, dict[str, list[str]]]:
        all_cats: set[str] = set()
        for m in manifestos:
            all_cats.update(m.categories.keys())

        if filter_categories:
            all_cats = all_cats.intersection(
                c.lower().replace(" ", "_") for c in filter_categories
            )

        aligned: dict[str, dict[str, list[str]]] = {}
        for cat in sorted(all_cats):
            aligned[cat] = {}
            for m in manifestos:
                aligned[cat][m.party_name] = m.categories.get(
                    cat,
                    ["Not addressed"],
                )

        return aligned

    async def _generate_analysis(
        self,
        manifestos: list[ManifestoData],
    ) -> str:
        if not self._gemini_api_key:
            return self._demo_analysis(manifestos)

        data = {m.party_name: m.categories for m in manifestos}
        prompt = COMPARISON_PROMPT.format(
            manifesto_data_json=json.dumps(data, indent=2),
        )
        result = await self._call_gemini(prompt)
        return result if result else self._demo_analysis(manifestos)

    def _parse_categories(self, text: str) -> dict[str, list[str]]:
        if not text:
            return {cat: ["Not addressed"] for cat in MANIFESTO_CATEGORIES}

        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`")
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return {
                    k: (v if isinstance(v, list) else [str(v)]) for k, v in data.items()
                }
        except json.JSONDecodeError:
            logger.warning("manifesto_json_parse_failed", text_length=len(text))

        return {cat: ["Not addressed"] for cat in MANIFESTO_CATEGORIES}

    def _parse_promises(
        self,
        text: str,
        party_name: str,
    ) -> list[PromiseTracker]:
        if not text:
            return self._demo_past_promises(party_name)

        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`")
        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return [
                    PromiseTracker(
                        promise=item.get("promise", "Unknown"),
                        status=item.get("status", "ongoing"),
                        evidence=item.get("evidence", "No data available"),
                        source=item.get("source", "Unknown"),
                    )
                    for item in data
                    if isinstance(item, dict)
                ]
        except json.JSONDecodeError:
            logger.warning("promise_json_parse_failed", text_length=len(text))

        return self._demo_past_promises(party_name)

    async def _call_gemini(self, prompt: str) -> str:
        model = "gemini-2.0-flash"
        url = f"{GEMINI_API_URL}/{model}:generateContent" f"?key={self._gemini_api_key}"
        body = json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
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
                with urllib.request.urlopen(req, timeout=20) as resp:
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

    def _get_cached(self, key: str) -> Any:
        entry = self._cache.get(key)
        if entry and (time.time() - entry[0]) < CACHE_TTL_SECONDS:
            return entry[1]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)

    @staticmethod
    def _identify_incumbents(party_names: list[str]) -> list[str]:
        incumbent_parties = {"BJP", "INC"}
        return [p for p in party_names if p.upper() in incumbent_parties]

    @staticmethod
    def _get_manifesto_url(party_name: str) -> str | None:
        urls: dict[str, str] = {
            "bjp": "https://www.bjp.org/manifesto",
            "inc": "https://www.inc.in/manifesto",
            "aap": "https://aamaadmiparty.org/manifesto",
        }
        return urls.get(party_name.lower().strip())

    @staticmethod
    def _demo_manifesto_data(party_name: str) -> dict[str, list[str]]:
        demos: dict[str, dict[str, list[str]]] = {
            "BJP": {
                "economy": [
                    "Make in India expansion to 25 sectors",
                    "\u20b95 Lakh Crore infrastructure investment",
                ],
                "education": [
                    "NEP 2020 full implementation",
                    "100 new universities in tier-2 cities",
                ],
                "healthcare": [
                    "Ayushman Bharat 2.0 expanded to 70 Crore citizens",
                    "1 district 1 medical college",
                ],
                "infrastructure": [
                    "Bullet train network expansion",
                    "100 smart cities completion",
                ],
                "defense": [
                    "75% indigenous defense procurement",
                    "Strengthened border infrastructure",
                ],
                "social_welfare": [
                    "Women reservation bill implementation",
                    "PM-KISAN expanded coverage",
                ],
                "environment": [
                    "500 GW renewable energy by 2030",
                    "Green hydrogen mission",
                ],
                "governance": [
                    "One Nation One Election",
                    "Digital governance expansion",
                ],
            },
            "INC": {
                "economy": [
                    "NYAY scheme - \u20b972K/year to poorest 20%",
                    "Legal MSP guarantee for farmers",
                ],
                "education": [
                    "6% GDP allocation on education",
                    "Restore UGC autonomy",
                ],
                "healthcare": [
                    "Universal healthcare coverage",
                    "\u20b91 Lakh/year health insurance for all",
                ],
                "infrastructure": [
                    "Affordable housing push for 2 Crore families",
                    "Rural road connectivity to all villages",
                ],
                "defense": [
                    "Modernize armed forces equipment",
                    "Increase veteran welfare budget",
                ],
                "social_welfare": [
                    "Caste census and OBC sub-quota",
                    "Urban employment guarantee scheme",
                ],
                "environment": [
                    "National clean air programme",
                    "River rejuvenation for 5 major rivers",
                ],
                "governance": [
                    "Strengthen RTI Act",
                    "Judicial appointment reforms",
                ],
            },
        }
        return demos.get(
            party_name.upper().strip(),
            {
                cat: ["Manifesto details pending analysis"]
                for cat in MANIFESTO_CATEGORIES
            },
        )

    @staticmethod
    def _demo_past_promises(party_name: str) -> list[PromiseTracker]:
        demos: dict[str, list[PromiseTracker]] = {
            "BJP": [
                PromiseTracker(
                    promise="Build 5 Crore houses by 2024",
                    status="partial",
                    evidence="2.1 Crore completed as of 2024",
                    source="PMAY dashboard",
                ),
                PromiseTracker(
                    promise="Double farmer income by 2022",
                    status="not_met",
                    evidence="Farm income grew ~15% in real terms",
                    source="NSSO survey data",
                ),
                PromiseTracker(
                    promise="100 smart cities",
                    status="ongoing",
                    evidence="60 of 100 cities at advanced stage",
                    source="Smart Cities Mission dashboard",
                ),
            ],
            "INC": [
                PromiseTracker(
                    promise="Farm loan waiver (2018 states)",
                    status="partial",
                    evidence="Implemented in 3 states won in 2018",
                    source="State government reports",
                ),
            ],
        }
        return demos.get(party_name.upper().strip(), [])

    @staticmethod
    def _demo_analysis(manifestos: list[ManifestoData]) -> str:
        names = [m.party_name for m in manifestos]
        if len(names) == 2:
            return (
                f"{names[0]} focuses on infrastructure-led growth and continuation "
                f"of existing flagship schemes, while {names[1]} proposes direct "
                f"income transfer programs and institutional reforms. Key divergence: "
                f"centralized development model vs. welfare redistribution approach. "
                f"Both parties emphasize healthcare expansion but differ on delivery "
                f"mechanism -- insurance-based vs. universal public healthcare."
            )
        return (
            f"Comparing {', '.join(names[:-1])} and {names[-1]}: These parties "
            f"represent diverse policy philosophies ranging from market-driven growth "
            f"to welfare-first redistribution. Voters should examine specific "
            f"commitments in categories most relevant to their priorities."
        )

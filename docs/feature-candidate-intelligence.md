# Feature: Candidate Intelligence

**Module**: `candidate` | **Phase**: 2 (Intelligence) | **Priority**: P0

Rigorous background search on election candidates with grounding search, structured comparative analysis, and tabular output for education, criminal record, assets, past work, and future work probability.

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| CI-1 | Voter | Search candidates by my constituency | I see who is contesting from my area |
| CI-2 | Voter | Auto-detect my constituency from GPS | I don't have to know the constituency name |
| CI-3 | Voter | See a candidate's education, criminal cases, and assets | I know their background objectively |
| CI-4 | Voter | Read recent news about a candidate via grounding search | I get up-to-date, verified information |
| CI-5 | Voter | Compare 2-4 candidates side-by-side in a table | I can make an informed comparison |
| CI-6 | Voter | See a probability assessment of future work delivery | I get an analytical view beyond promises |

## UI Wireframe

### Search View

```
┌─────────────────────────────────────┐
│  🔍 Find Your Candidates            │
│                                     │
│  ┌─────────────────────┐ ┌────────┐│
│  │ Constituency name   │ │ Search ││
│  └─────────────────────┘ └────────┘│
│  [📍 Use my location]              │
│                                     │
│  Results: South Delhi (3 candidates)│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ☐ Ramesh Kumar (BJP)            ││
│  │   🎓 MBA, IIM-A │ ⚖️ 0 cases   ││
│  │   💰 ₹2.1 Cr │ 🏛️ MLA 2 terms ││
│  │   [Full Profile] [Select]       ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ ☐ Priya Singh (INC)             ││
│  │   🎓 LLB, DU │ ⚖️ 1 case      ││
│  │   💰 ₹8.5 Cr │ 🏛️ First time  ││
│  │   [Full Profile] [Select]       ││
│  └─────────────────────────────────┘│
│                                     │
│  [Compare Selected (0/4)]           │
└─────────────────────────────────────┘
```

### Comparison View

```
┌──────────────────────────────────────────────────────────┐
│  📊 Candidate Comparison                                  │
│                                                          │
│  ┌──────────────┬──────────────┬──────────────┐          │
│  │              │ Ramesh Kumar │ Priya Singh  │          │
│  │              │ BJP          │ INC          │          │
│  ├──────────────┼──────────────┼──────────────┤          │
│  │ Education    │ MBA, IIM-A   │ LLB, Delhi U │          │
│  │ Age          │ 52           │ 38           │          │
│  │ Criminal     │ 0 cases      │ 1 case       │          │
│  │  Cases       │              │ (pending)    │          │
│  │ Total Assets │ ₹2.1 Crore   │ ₹8.5 Crore  │          │
│  │ Liabilities  │ ₹0.3 Crore   │ ₹1.2 Crore  │          │
│  │ Past Work    │ MLA 2 terms  │ Councillor   │          │
│  │              │ Built 3      │ 1 term       │          │
│  │              │ schools      │              │          │
│  │ Key Promises │ Metro ext.   │ Women safety │          │
│  │              │ Clean water  │ Free buses   │          │
│  │ Recent News  │ Inaugurated  │ Led protest  │          │
│  │  (30 days)   │ hospital     │ on pollution │          │
│  │ Delivery     │ ★★★★☆       │ ★★★☆☆       │          │
│  │  Probability │ High (past   │ Moderate     │          │
│  │              │ track record)│ (new entrant)│          │
│  └──────────────┴──────────────┴──────────────┘          │
│                                                          │
│  📝 AI Analysis:                                         │
│  "Ramesh Kumar has a stronger track record with 2 terms  │
│   as MLA and measurable infrastructure delivery. Priya   │
│   Singh brings legal expertise but limited governance    │
│   experience. Key differentiator: urban development vs.  │
│   social justice focus."                                 │
│                                                          │
│  [Share Comparison] [Download PDF]                       │
└──────────────────────────────────────────────────────────┘
```

## Backend API

### `POST /candidate/search`

Search candidates by constituency name or GPS coordinates.

**Request**:
```json
{
  "constituency": "South Delhi",
  "lat": null,
  "lng": null
}
```
Or GPS-based:
```json
{
  "constituency": null,
  "lat": 28.5245,
  "lng": 77.2066
}
```

**Response**:
```json
{
  "constituency": "South Delhi",
  "election": "Lok Sabha 2024",
  "candidates": [
    {
      "id": "cand_ramesh_kumar_bjp",
      "name": "Ramesh Kumar",
      "party": "BJP",
      "party_symbol_url": "https://...",
      "education": "MBA, IIM Ahmedabad",
      "age": 52,
      "criminal_cases": 0,
      "total_assets_inr": 21000000,
      "total_liabilities_inr": 3000000,
      "past_positions": ["MLA South Delhi 2014-2019", "MLA South Delhi 2019-2024"]
    }
  ]
}
```

### `GET /candidate/{id}/background`

Deep background check with grounding search.

**Response**:
```json
{
  "candidate": { "...base profile..." },
  "grounding_results": {
    "recent_news": [
      {
        "title": "MLA inaugurates new hospital wing",
        "source": "Times of India",
        "date": "2024-03-15",
        "url": "https://...",
        "sentiment": "positive"
      }
    ],
    "achievements": ["Built 3 govt schools", "Metro extension advocacy"],
    "controversies": [],
    "social_media_presence": "Active on X/Twitter, 50K followers"
  },
  "criminal_details": [],
  "asset_breakdown": {
    "movable": 8000000,
    "immovable": 13000000,
    "vehicles": ["Toyota Innova 2022"]
  },
  "source_urls": {
    "myneta": "https://myneta.info/...",
    "eci_affidavit": "https://..."
  }
}
```

### `POST /candidate/compare`

Side-by-side comparison with AI analysis.

**Request**:
```json
{
  "candidate_ids": ["cand_ramesh_kumar_bjp", "cand_priya_singh_inc"]
}
```

**Response**:
```json
{
  "comparison_matrix": {
    "dimensions": ["education", "age", "criminal_cases", "total_assets", "total_liabilities", "past_work", "key_promises", "recent_news", "delivery_probability"],
    "candidates": {
      "cand_ramesh_kumar_bjp": {
        "education": "MBA, IIM Ahmedabad",
        "age": 52,
        "criminal_cases": "0 cases",
        "total_assets": "₹2.1 Crore",
        "total_liabilities": "₹0.3 Crore",
        "past_work": "MLA 2 terms. Built 3 schools, advocated metro extension.",
        "key_promises": "Metro extension to Mehrauli, clean water for 50 wards",
        "recent_news": "Inaugurated hospital wing (ToI, Mar 2024)",
        "delivery_probability": "High - consistent infrastructure delivery over 2 terms"
      },
      "cand_priya_singh_inc": { "..." }
    }
  },
  "ai_analysis": "Ramesh Kumar has a stronger track record...",
  "ai_analysis_citations": [
    { "source": "MyNeta.info", "url": "https://..." },
    { "source": "Google Search", "query": "Ramesh Kumar MLA South Delhi" }
  ]
}
```

## Service Layer

### `CandidateService` (`functions/src/services/candidate_service.py`)

```python
class CandidateService:
    """Candidate research with grounding search and comparative analysis."""

    async def search_by_constituency(
        self, constituency: str
    ) -> list[CandidateSummary]:
        """Search candidates for a constituency.

        1. Check Firestore cache (TTL: 24h)
        2. On miss: ScraperService.fetch_myneta_candidates()
        3. Parse and normalize data
        4. Cache in Firestore
        """

    async def search_by_location(
        self, lat: float, lng: float
    ) -> list[CandidateSummary]:
        """Reverse-geocode GPS to constituency, then search.

        Uses Google Maps Geocoding API to resolve coordinates
        to parliamentary/assembly constituency name.
        """

    async def grounding_search(
        self, candidate_name: str, constituency: str
    ) -> GroundingResult:
        """Search real-time information via Gemini with Google Search grounding.

        Prompt: "Find recent news, achievements, and controversies for
        {candidate_name} who is contesting from {constituency} constituency.
        Focus on the last 6 months. Cite sources."

        Uses: Gemini 2.0 Flash with grounding config enabled.
        """

    async def background_check(
        self, candidate_id: str
    ) -> BackgroundReport:
        """Comprehensive background report combining:

        1. MyNeta structured data (criminal, assets, education)
        2. Gemini grounding search (news, social presence)
        3. Structured extraction into BackgroundReport model
        """

    async def compare(
        self, candidate_ids: list[str]
    ) -> ComparisonResult:
        """Build structured comparison matrix.

        1. Fetch background for each candidate (parallel)
        2. Build dimension-wise matrix
        3. Call Gemini for analytical summary
        4. Assess delivery probability based on:
           - Past terms served and measurable outcomes
           - Criminal record (negative signal)
           - Asset growth rate (proxy for governance focus)
           - Grounding search sentiment
        """
```

### `ScraperService` (`functions/src/services/scraper_service.py`)

```python
class ScraperService:
    """Extracts structured candidate data from public sources."""

    async def fetch_myneta_candidates(
        self, constituency: str
    ) -> list[RawCandidateData]:
        """Fetch candidate list from MyNeta.info for a constituency.

        MyNeta URL pattern: https://myneta.info/{election}/{constituency}
        Parse HTML table for: name, party, education, criminal cases,
        total assets, total liabilities.

        Defensive: if HTML structure changes, fall back to
        Gemini grounding search for the same data.
        """

    async def fetch_eci_affidavit(
        self, candidate_id: str
    ) -> AffidavitData | None:
        """Fetch candidate's election affidavit from ECI.

        Returns structured data from the affidavit PDF if available.
        Uses Vision API for OCR on non-digital affidavits (future).
        """
```

## Data Models

### Pydantic Models (`functions/src/models/candidate.py`)

```python
class CandidateSearchRequest(BaseModel):
    constituency: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def require_one_search_method(self) -> Self:
        if not self.constituency and (self.lat is None or self.lng is None):
            raise ValueError("Provide constituency name or lat/lng coordinates")
        return self

class CompareRequest(BaseModel):
    candidate_ids: list[str] = Field(min_length=2, max_length=4)

class CandidateSummary(BaseModel):
    id: str
    name: str
    party: str
    party_symbol_url: str | None
    education: str
    age: int | None
    criminal_cases: int
    total_assets_inr: int
    total_liabilities_inr: int
    past_positions: list[str]

class GroundingResult(BaseModel):
    recent_news: list[NewsItem]
    achievements: list[str]
    controversies: list[str]
    social_media_presence: str | None
    sources: list[SourceCitation]

class BackgroundReport(BaseModel):
    candidate: CandidateSummary
    grounding: GroundingResult
    criminal_details: list[CriminalCase]
    asset_breakdown: AssetBreakdown
    source_urls: dict[str, str]

class ComparisonResult(BaseModel):
    dimensions: list[str]
    candidates: dict[str, dict[str, str]]
    ai_analysis: str
    ai_analysis_citations: list[SourceCitation]

class NewsItem(BaseModel):
    title: str
    source: str
    date: str
    url: str | None
    sentiment: Literal["positive", "negative", "neutral"]
```

## Gemini Prompts

### Grounding Search Prompt

```
You are an election research assistant. Search for recent, factual information
about the following candidate:

Name: {candidate_name}
Constituency: {constituency}
Party: {party}

Find and structure:
1. News from the last 6 months (with source and date)
2. Key achievements in public service
3. Controversies or legal issues
4. Social media presence and public engagement

Rules:
- Only include information you can cite with a source
- Clearly mark unverified claims as "unverified"
- Do not express political opinions or endorsements
- Be factual and neutral in tone
```

### Comparative Analysis Prompt

```
You are an impartial election analyst. Compare these candidates based on
their official records and public information:

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
```

## Unit Tests

### `functions/tests/test_candidate_service.py`

```python
class TestCandidateService:

    async def test_search_by_constituency_returns_candidates(self):
        """Valid constituency should return candidate list."""

    async def test_search_by_constituency_uses_cache(self):
        """Cached data within 24h should skip scraper."""

    async def test_search_by_location_resolves_constituency(self):
        """GPS coordinates should resolve to constituency name."""

    async def test_grounding_search_calls_gemini(self):
        """Grounding search should call Gemini with search config."""

    async def test_grounding_search_returns_structured_result(self):
        """Response should parse into GroundingResult model."""

    async def test_background_check_combines_sources(self):
        """Background should merge MyNeta data + grounding results."""

    async def test_compare_builds_matrix(self):
        """Comparison should produce dimension-wise matrix."""

    async def test_compare_limits_to_4_candidates(self):
        """More than 4 candidates should raise validation error."""

    async def test_compare_includes_ai_analysis(self):
        """Comparison should include Gemini analytical summary."""

    async def test_cache_ttl_24h(self):
        """Candidate data older than 24h should be refetched."""
```

### `functions/tests/test_scraper_service.py`

```python
class TestScraperService:

    async def test_myneta_parses_candidate_table(self):
        """HTML fixture should parse into RawCandidateData list."""

    async def test_myneta_handles_missing_fields(self):
        """Missing optional fields should default gracefully."""

    async def test_myneta_fallback_on_structure_change(self):
        """Unrecognized HTML should fall back without crashing."""

    async def test_affidavit_returns_none_when_unavailable(self):
        """Missing affidavit should return None, not error."""
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Constituency not found | Suggest similar names via fuzzy match |
| No candidates in cache or scraper | Fall back to Gemini grounding search only |
| MyNeta HTML changes | Defensive parsing; log warning; use Gemini fallback |
| Candidate has no criminal record | Display "No criminal cases declared" (not blank) |
| Assets = 0 | Display "Not declared" rather than ₹0 |
| GPS resolves to non-election area | Show nearest constituency with explanation |
| Same candidate name, different constituency | Disambiguate by party + constituency |

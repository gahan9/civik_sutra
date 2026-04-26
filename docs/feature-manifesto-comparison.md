# Feature: Manifesto Comparison

**Module**: `manifesto` (part of `candidate` service) | **Phase**: 3 (Depth) | **Priority**: P1

Side-by-side party manifesto analysis with category-wise breakdown, promise tracking, and AI-generated summary of policy differences.

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| MC-1 | Voter | Compare manifestos of 2-4 parties side-by-side | I understand policy differences |
| MC-2 | Voter | See manifesto broken down by category (economy, health, etc.) | I can focus on issues I care about |
| MC-3 | Voter | Read an AI summary of key differences | I get a quick neutral overview |
| MC-4 | Voter | See past promises vs. delivery for incumbent parties | I know if they follow through |
| MC-5 | Voter | Share the comparison with others | I can help friends/family decide |

## UI Wireframe

```
┌────────────────────────────────────────────────────────────┐
│  📜 Manifesto Comparison                                    │
│                                                            │
│  Select parties: [BJP ☑] [INC ☑] [AAP ☐] [+ Add]         │
│                                                            │
│  Category Filter: [All] [Economy] [Education] [Health]...  │
│                                                            │
│  ┌──────────────┬──────────────────┬──────────────────┐    │
│  │ Category     │ BJP              │ INC              │    │
│  ├──────────────┼──────────────────┼──────────────────┤    │
│  │ Economy      │ • Make in India  │ • NYAY scheme    │    │
│  │              │   expansion      │   ₹72K/yr to     │    │
│  │              │ • ₹5L Cr infra   │   poorest 20%    │    │
│  │              │   investment     │ • MSP guarantee  │    │
│  ├──────────────┼──────────────────┼──────────────────┤    │
│  │ Education    │ • NEP 2020       │ • 6% GDP on      │    │
│  │              │   implementation │   education      │    │
│  │              │ • 100 new        │ • Restore UGC    │    │
│  │              │   universities   │   autonomy       │    │
│  ├──────────────┼──────────────────┼──────────────────┤    │
│  │ Healthcare   │ • Ayushman 2.0   │ • Universal      │    │
│  │              │   expanded       │   healthcare     │    │
│  │              │ • 1 district     │ • ₹1L/yr health  │    │
│  │              │   1 hospital     │   cover          │    │
│  ├──────────────┼──────────────────┼──────────────────┤    │
│  │ Infra        │ • Bullet train   │ • Affordable     │    │
│  │              │   network        │   housing push   │    │
│  │              │ • Smart cities   │ • Rural roads    │    │
│  ├──────────────┼──────────────────┼──────────────────┤    │
│  │ Social       │ • Women          │ • Caste census   │    │
│  │ Welfare      │   reservation    │ • OBC sub-quota  │    │
│  │              │   in Parliament  │                  │    │
│  └──────────────┴──────────────────┴──────────────────┘    │
│                                                            │
│  📝 AI Analysis:                                           │
│  "BJP focuses on infrastructure-led growth and             │
│   continuation of existing schemes. INC proposes direct    │
│   income transfer programs and institutional reforms.      │
│   Key divergence: centralized development vs. welfare      │
│   redistribution approach."                                │
│                                                            │
│  📊 Past Promise Delivery (incumbent only):                │
│  ┌──────────────────┬──────────┬──────────┐               │
│  │ Promise (2019)   │ Status   │ Evidence │               │
│  ├──────────────────┼──────────┼──────────┤               │
│  │ ₹5 Cr houses     │ Partial  │ 2.1 Cr  │               │
│  │ Double farmers   │ Not met  │ ~15%    │               │
│  │ Smart cities     │ Ongoing  │ 60/100  │               │
│  └──────────────────┴──────────┴──────────┘               │
│                                                            │
│  [Share on WhatsApp] [Download PDF]                        │
└────────────────────────────────────────────────────────────┘
```

## Backend API

### `POST /manifesto/compare`

**Request**:
```json
{
  "party_names": ["BJP", "INC"],
  "categories": null,
  "include_past_promises": true
}
```

**Response**:
```json
{
  "parties": ["BJP", "INC"],
  "categories": {
    "economy": {
      "BJP": ["Make in India expansion", "₹5L Crore infrastructure investment"],
      "INC": ["NYAY scheme - ₹72K/year to poorest 20%", "Legal MSP guarantee"]
    },
    "education": { "..." },
    "healthcare": { "..." },
    "infrastructure": { "..." },
    "defense": { "..." },
    "social_welfare": { "..." },
    "environment": { "..." },
    "governance": { "..." }
  },
  "ai_analysis": "BJP focuses on infrastructure-led growth...",
  "past_promises": {
    "BJP": [
      {
        "promise": "Build 5 Crore houses by 2024",
        "status": "partial",
        "evidence": "2.1 Crore completed as of 2024",
        "source": "PMAY dashboard"
      }
    ]
  },
  "sources": [
    { "party": "BJP", "manifesto_url": "https://..." },
    { "party": "INC", "manifesto_url": "https://..." }
  ]
}
```

## Service Layer

### Manifesto Methods on `CandidateService`

```python
class CandidateService:

    async def fetch_manifesto(self, party_name: str) -> ManifestoData:
        """Fetch and parse a party's manifesto.

        Strategy:
        1. Check Firestore cache (TTL: 7 days)
        2. On miss:
           a. Search for official manifesto PDF/page URL via Gemini grounding
           b. Send manifesto content to Gemini for category-wise extraction
           c. Cache structured result in Firestore
        """

    async def compare_manifestos(
        self, party_names: list[str], categories: list[str] | None = None
    ) -> ManifestoComparison:
        """Compare manifestos across parties.

        1. Fetch manifesto for each party (parallel)
        2. Align categories across parties
        3. Generate AI comparative analysis
        4. If include_past_promises: fetch promise tracking for incumbents
        """

    async def track_past_promises(
        self, party_name: str, election_year: int
    ) -> list[PromiseTracker]:
        """Track delivery on past manifesto promises.

        Uses Gemini grounding to search for evidence of promise
        fulfillment. Classifies as: fulfilled / partial / not_met / ongoing.
        """
```

## Data Models

```python
class ManifestoCompareRequest(BaseModel):
    party_names: list[str] = Field(min_length=2, max_length=4)
    categories: list[str] | None = None
    include_past_promises: bool = True

class ManifestoData(BaseModel):
    party_name: str
    election_year: int
    categories: dict[str, list[str]]
    summary: str
    full_text_url: str | None
    fetched_at: datetime

class PromiseTracker(BaseModel):
    promise: str
    status: Literal["fulfilled", "partial", "not_met", "ongoing"]
    evidence: str
    source: str

class ManifestoComparison(BaseModel):
    parties: list[str]
    categories: dict[str, dict[str, list[str]]]
    ai_analysis: str
    past_promises: dict[str, list[PromiseTracker]] | None
    sources: list[ManifestoSource]
```

## Gemini Prompts

### Manifesto Extraction

```
You are a political analyst. Extract the key promises and policy positions from
this party manifesto into structured categories.

Party: {party_name}
Manifesto content: {manifesto_text_or_url}

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

Rules:
- Extract exact commitments, not vague statements
- Prefer quantified promises (amounts, timelines, targets)
- Be factual -- do not interpret or editorialize
```

### Promise Tracking

```
You are a fact-checker. For each promise made by {party_name} in their
{election_year} manifesto, search for evidence of delivery.

Promises:
{promises_json}

For each promise, determine:
1. Status: fulfilled / partial / not_met / ongoing
2. Evidence: specific data, statistics, or reports
3. Source: news article, government report, or official data

Rules:
- Only use verifiable sources
- "Partial" means measurable progress but target not fully met
- "Ongoing" means active implementation with no deadline passed
- Do not speculate on intent; only assess outcomes
```

## Unit Tests

### `functions/tests/test_candidate_service.py` (manifesto section)

```python
class TestManifestoComparison:

    async def test_fetch_manifesto_returns_categories(self):
        """Fetched manifesto should have standard category keys."""

    async def test_fetch_manifesto_uses_cache(self):
        """Cached manifesto within 7 days should skip fetch."""

    async def test_compare_manifestos_aligns_categories(self):
        """All parties should have the same category keys in output."""

    async def test_compare_manifestos_generates_analysis(self):
        """Comparison should include AI-generated neutral analysis."""

    async def test_compare_limits_to_4_parties(self):
        """More than 4 parties should raise validation error."""

    async def test_past_promises_classifies_status(self):
        """Each promise should have a valid status classification."""

    async def test_past_promises_skips_non_incumbent(self):
        """Non-incumbent parties should return empty promise tracking."""
```

## Manifesto Categories (Standard Set)

| Category | Covers |
|----------|--------|
| Economy & Employment | GDP targets, job creation, industry policy, taxation, MSP |
| Education | School/university policy, NEP, budget allocation, skill development |
| Healthcare | Insurance, hospitals, public health, pharma, mental health |
| Infrastructure | Roads, railways, housing, smart cities, digital infrastructure |
| Defense & Security | Military, border, internal security, cybersecurity |
| Social Welfare | Poverty, reservations, pensions, food security, women/child |
| Environment & Climate | Renewable energy, pollution, forest cover, climate targets |
| Governance | Anti-corruption, judicial reform, police reform, decentralization |

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Manifesto not published yet | Show "Manifesto not yet released" with last known positions |
| Party has no manifesto (regional party) | Use grounding search for policy statements |
| Manifesto in regional language only | Gemini translates before extraction |
| Very long manifesto (100+ pages) | Summarize chapter-wise, extract top 5 per category |
| Past promises unmeasurable | Mark as "Cannot verify -- no measurable target set" |

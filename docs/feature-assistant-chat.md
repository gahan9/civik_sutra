# Feature: Assistant Chat

**Module**: `assistant` | **Phase**: 3 (Depth) | **Priority**: P1

Gemini-powered conversational election guide with Google Search grounding, tool calling (booth finder, candidate search), streaming responses, and conversation memory.

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| AC-1 | Voter | Ask questions about the election process in natural language | I get answers without navigating complex menus |
| AC-2 | Voter | Get answers grounded in real search results with citations | I can trust and verify the information |
| AC-3 | Voter | Ask "find my polling booth" in chat and get map results | The chat integrates with other app features |
| AC-4 | Voter | Continue a conversation across multiple messages | The assistant remembers context |
| AC-5 | Voter | See streaming responses as they generate | I don't wait for the full response |
| AC-6 | Voter | Chat in my preferred language | I understand everything clearly |
| AC-7 | Voter | Get suggested questions to start with | I know what to ask even if I'm unsure |

## UI Wireframe

```
┌─────────────────────────────────────┐
│  💬 Election Assistant               │
│  ─────────────────────────────────  │
│                                     │
│  Quick Questions:                   │
│  ┌───────────────────┐              │
│  │ What documents do  │              │
│  │ I need to vote?    │              │
│  └───────────────────┘              │
│  ┌───────────────────┐              │
│  │ Find my polling    │              │
│  │ booth              │              │
│  └───────────────────┘              │
│  ┌───────────────────┐              │
│  │ Compare candidates │              │
│  │ in my constituency │              │
│  └───────────────────┘              │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 👤 What documents do I need     ││
│  │    to carry for voting?         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 🤖 You need one of the          ││
│  │ following valid photo IDs:      ││
│  │                                 ││
│  │ 1. EPIC (Voter ID Card)        ││
│  │ 2. Aadhaar Card                ││
│  │ 3. Passport                    ││
│  │ 4. Driving License             ││
│  │ 5. PAN Card                    ││
│  │ ...6 more accepted IDs         ││
│  │                                 ││
│  │ The EPIC card is preferred.     ││
│  │ If you don't have one, you can  ││
│  │ apply at NVSP portal.           ││
│  │                                 ││
│  │ 📎 Source: ECI Guidelines       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌──────────────────────┐ ┌──────┐ │
│  │ Type your question...│ │ Send │ │
│  └──────────────────────┘ └──────┘ │
│                                     │
│  🌐 Language: [English ▼]          │
└─────────────────────────────────────┘
```

## Backend API

### `POST /assistant/chat`

Streaming chat endpoint using Server-Sent Events (SSE).

**Request**:
```json
{
  "message": "What documents do I need to carry for voting?",
  "session_id": "sess_abc123",
  "language": "en",
  "location": { "lat": 28.6139, "lng": 77.2090 }
}
```

**Response** (SSE stream):
```
event: token
data: {"text": "You need "}

event: token
data: {"text": "one of the following "}

event: token
data: {"text": "valid photo IDs:\n\n"}

event: tool_call
data: {"tool": "none", "status": "direct_response"}

event: citation
data: {"source": "ECI Guidelines", "url": "https://eci.gov.in/..."}

event: done
data: {"session_id": "sess_abc123", "tokens_used": 156}
```

When tool calling is triggered:
```
event: token
data: {"text": "Let me find polling booths near you..."}

event: tool_call
data: {"tool": "booth_finder", "args": {"lat": 28.6139, "lng": 77.2090}}

event: tool_result
data: {"booths": [{"name": "Govt School Ward 42", "distance": "0.8 km"}]}

event: token
data: {"text": "I found 3 booths near you. The closest is "}

event: done
data: {"session_id": "sess_abc123", "tokens_used": 210}
```

## Service Layer

### `ChatService` (`functions/src/services/chat_service.py`)

```python
class ChatService:
    """Gemini-powered election assistant with tools and grounding."""

    SYSTEM_PROMPT = """You are an impartial election education assistant for
    Indian elections. Your role is to help voters understand the election
    process, find their polling booths, research candidates, and make
    informed decisions.

    Rules:
    - Never endorse or recommend any candidate or party
    - Always cite sources when stating facts
    - If unsure, say so and suggest where to find accurate information
    - Respond in the user's preferred language
    - Keep responses concise but thorough
    - Use the available tools when the user asks about booths or candidates
    """

    TOOLS = [
        {
            "name": "booth_finder",
            "description": "Find nearby polling booths based on GPS location",
            "parameters": {"lat": "float", "lng": "float", "radius_km": "float"}
        },
        {
            "name": "candidate_search",
            "description": "Search candidates by constituency name or location",
            "parameters": {"constituency": "str | None", "lat": "float | None", "lng": "float | None"}
        },
        {
            "name": "verify_voter",
            "description": "Verify voter registration using EPIC number",
            "parameters": {"epic_number": "str"}
        }
    ]

    async def stream_chat(
        self,
        message: str,
        session_id: str,
        language: str = "en",
        location: LatLng | None = None,
    ) -> AsyncIterator[ChatEvent]:
        """Stream a chat response with grounding and tool calling.

        Flow:
        1. Load conversation history from Firestore (session_id)
        2. Build Gemini request with system prompt, history, tools, grounding
        3. Stream response tokens
        4. If tool call: execute tool, feed result back, continue streaming
        5. Save updated conversation to Firestore
        6. Yield ChatEvent objects (token, tool_call, tool_result, citation, done)
        """

    async def _execute_tool(
        self, tool_name: str, args: dict
    ) -> dict:
        """Execute a tool call from Gemini and return result.

        Routes to GeoService or CandidateService based on tool_name.
        """

    async def _load_history(self, session_id: str) -> list[dict]:
        """Load conversation history from Firestore.

        Returns last 10 messages to stay within context window.
        Creates new session document if session_id doesn't exist.
        """

    async def _save_message(
        self, session_id: str, role: str, content: str
    ) -> None:
        """Append message to Firestore session document."""
```

## Data Models

```python
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(min_length=1, max_length=128)
    language: Literal["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml"] = "en"
    location: LatLng | None = None

class ChatEvent(BaseModel):
    event: Literal["token", "tool_call", "tool_result", "citation", "done"]
    data: dict

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    citations: list[SourceCitation] | None = None
    tool_calls: list[ToolCallRecord] | None = None

class ToolCallRecord(BaseModel):
    tool_name: str
    args: dict
    result_summary: str
```

## Gemini Configuration

```python
generation_config = {
    "temperature": 0.3,        # Low for factual accuracy
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024, # Per .env config
}

safety_settings = {
    HarmCategory.HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

grounding_config = {
    "google_search_retrieval": {
        "dynamic_retrieval_config": {
            "mode": "MODE_DYNAMIC",
            "dynamic_threshold": 0.3  # Ground when confidence is low
        }
    }
}
```

## Suggested Quick Questions

```python
QUICK_QUESTIONS = {
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
        "वोट देने के लिए कौन से दस्तावेज चाहिए?",
        "मेरा नजदीकी मतदान केंद्र खोजें",
        "मेरे निर्वाचन क्षेत्र के उम्मीदवारों की तुलना करें",
        "मतदाता पहचान पत्र कैसे बनवाएं?",
        ...
    ]
}
```

## Unit Tests

### `functions/tests/test_chat_service.py`

```python
class TestChatService:

    async def test_stream_returns_token_events(self):
        """Basic message should stream token events."""

    async def test_stream_ends_with_done_event(self):
        """Stream should always end with a done event."""

    async def test_grounding_returns_citations(self):
        """Factual questions should include citation events."""

    async def test_tool_call_booth_finder(self):
        """'Find my booth' should trigger booth_finder tool call."""

    async def test_tool_call_candidate_search(self):
        """'Compare candidates' should trigger candidate_search tool."""

    async def test_history_loaded_from_firestore(self):
        """Existing session should load previous messages."""

    async def test_history_limited_to_10_messages(self):
        """Only last 10 messages should be loaded for context."""

    async def test_new_session_created(self):
        """Unknown session_id should create new Firestore document."""

    async def test_message_saved_after_response(self):
        """Both user message and assistant response should be saved."""

    async def test_language_respected_in_response(self):
        """Setting language='hi' should produce Hindi response."""

    async def test_rate_limit_enforced(self):
        """Exceeding daily Gemini quota should return error event."""

    async def test_safety_settings_applied(self):
        """Harmful content should be blocked by safety settings."""
```

## Conversation Flow Examples

### Example 1: Booth discovery via chat

```
User: "Find my polling booth"
Assistant: [tool_call: booth_finder with user's GPS]
           "I found 3 booths near you! The closest is Govt. Primary School,
            Ward 42 (0.8 km, 12 min walk). Current traffic is low.
            Would you like directions?"
User: "Yes, walking directions"
Assistant: [tool_call: booth_directions]
           "Here's your route: Head north on MG Road (200m), turn right
            at Hanuman Mandir (600m). Total: 12 minutes walking."
```

### Example 2: Candidate research via chat

```
User: "Who is contesting from South Delhi?"
Assistant: [tool_call: candidate_search for South Delhi]
           "Here are the candidates from South Delhi:
            1. Ramesh Kumar (BJP) - MBA, 0 criminal cases, ₹2.1 Cr assets
            2. Priya Singh (INC) - LLB, 1 case, ₹8.5 Cr assets
            Would you like me to compare them in detail?"
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Prompt injection attempt | System prompt has strict boundaries; safety settings block |
| User asks for political opinion | "I'm designed to provide facts, not opinions. Here's what the data shows..." |
| Tool call fails (API down) | "I couldn't fetch that data right now. Try the Booth Finder tab directly." |
| Session expired (> 24h) | Start new session, acknowledge: "Starting a fresh conversation." |
| Very long user message | Truncate to 2000 chars with notice |
| Non-election question | Redirect: "I specialize in election information. Can I help with voting?" |

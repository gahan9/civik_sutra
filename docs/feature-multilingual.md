# Feature: Multilingual Support

**Module**: `i18n` | **Phase**: 4 (Polish) | **Priority**: P2

Hindi, English, and regional language support for the entire application. Static UI strings use `react-i18next` translation files. AI-generated content (chat, analysis) uses Gemini's built-in multilingual capability.

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| ML-1 | Voter | Switch the app language to Hindi | I understand everything in my mother tongue |
| ML-2 | Voter | Get AI chat responses in my language | I don't need to translate mentally |
| ML-3 | Voter | See candidate comparison in my language | Data is accessible regardless of language |
| ML-4 | Voter | Share content in my language | My friends/family can also understand it |

## Supported Languages

### Phase 4 (Launch)

| Language | Code | Script | Coverage |
|----------|------|--------|----------|
| English | `en` | Latin | Full UI + AI |
| Hindi | `hi` | Devanagari | Full UI + AI |

### Post-Launch (Phase 5+)

| Language | Code | Script | Coverage |
|----------|------|--------|----------|
| Tamil | `ta` | Tamil | AI responses (Gemini) |
| Telugu | `te` | Telugu | AI responses (Gemini) |
| Bengali | `bn` | Bengali | AI responses (Gemini) |
| Marathi | `mr` | Devanagari | AI responses (Gemini) |
| Gujarati | `gu` | Gujarati | AI responses (Gemini) |
| Kannada | `kn` | Kannada | AI responses (Gemini) |
| Malayalam | `ml` | Malayalam | AI responses (Gemini) |

Post-launch languages get AI responses in the selected language but UI chrome remains in English/Hindi until translation files are added.

## Architecture

### Two-Layer Translation Strategy

```
┌─────────────────────────────────────────┐
│ Layer 1: Static UI Strings              │
│ (react-i18next + JSON files)            │
│                                         │
│ • Buttons, labels, headers, menus       │
│ • Checklist items, form labels          │
│ • Error messages, tooltips              │
│ • Fully translated for en + hi          │
│ • Loaded at build time (bundled)        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Layer 2: Dynamic AI Content             │
│ (Gemini native multilingual)            │
│                                         │
│ • Chat responses                        │
│ • Candidate analysis text               │
│ • Manifesto summaries                   │
│ • Grounding search results              │
│ • Generated at runtime in user's lang   │
└─────────────────────────────────────────┘
```

### Why Not Translate Everything with Gemini?

| Approach | Latency | Cost | Quality | Offline |
|----------|---------|------|---------|---------|
| Static JSON (react-i18next) | 0ms | Free | Perfect (human-reviewed) | Yes |
| Gemini per request | 500-2000ms | Per token | Good but variable | No |

Static for UI chrome, Gemini for dynamic content. Best of both worlds.

## Implementation

### Frontend: `react-i18next` Setup

#### Configuration (`frontend/src/i18n/index.ts`)

```typescript
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./locales/en.json";
import hi from "./locales/hi.json";

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, hi: { translation: hi } },
  lng: localStorage.getItem("language") || "en",
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
```

#### Translation Files

**`frontend/src/i18n/locales/en.json`**:
```json
{
  "app": {
    "title": "Election Assistant",
    "subtitle": "Your guide to informed voting"
  },
  "nav": {
    "booth": "Find Booth",
    "candidates": "Candidates",
    "chat": "Ask AI",
    "checklist": "Checklist"
  },
  "booth": {
    "title": "Find Your Polling Booth",
    "searchPlaceholder": "Enter pincode or address",
    "useGps": "Use my location",
    "nearby": "Nearby Booths",
    "directions": "Get Directions",
    "verify": "Verify Booth",
    "traffic": {
      "low": "Low traffic",
      "moderate": "Moderate traffic",
      "heavy": "Heavy traffic"
    },
    "bestTime": "Best time to visit"
  },
  "candidate": {
    "title": "Find Your Candidates",
    "search": "Search constituency",
    "compare": "Compare Selected",
    "education": "Education",
    "criminal": "Criminal Cases",
    "assets": "Total Assets",
    "background": "Full Background",
    "noResults": "No candidates found"
  },
  "voter": {
    "eligibility": "Am I Eligible?",
    "checklist": "Voting Day Checklist",
    "applyCard": "Apply for Voter ID",
    "age": "Your age",
    "citizen": "Indian citizen?",
    "registered": "Registered voter?",
    "eligible": "You ARE eligible to vote!",
    "notEligible": "You are not eligible to vote",
    "needRegister": "You need to register first"
  },
  "chat": {
    "title": "Election Assistant",
    "placeholder": "Type your question...",
    "send": "Send",
    "quickQuestions": "Quick Questions",
    "language": "Language"
  },
  "common": {
    "loading": "Loading...",
    "error": "Something went wrong",
    "retry": "Try again",
    "share": "Share",
    "download": "Download"
  }
}
```

**`frontend/src/i18n/locales/hi.json`**:
```json
{
  "app": {
    "title": "चुनाव सहायक",
    "subtitle": "सूचित मतदान के लिए आपका मार्गदर्शक"
  },
  "nav": {
    "booth": "बूथ खोजें",
    "candidates": "उम्मीदवार",
    "chat": "AI से पूछें",
    "checklist": "चेकलिस्ट"
  },
  "booth": {
    "title": "अपना मतदान केंद्र खोजें",
    "searchPlaceholder": "पिनकोड या पता दर्ज करें",
    "useGps": "मेरा स्थान उपयोग करें",
    "nearby": "नजदीकी बूथ",
    "directions": "दिशा-निर्देश",
    "verify": "बूथ सत्यापित करें",
    "traffic": {
      "low": "कम यातायात",
      "moderate": "मध्यम यातायात",
      "heavy": "भारी यातायात"
    },
    "bestTime": "जाने का सबसे अच्छा समय"
  },
  "candidate": {
    "title": "अपने उम्मीदवार खोजें",
    "search": "निर्वाचन क्षेत्र खोजें",
    "compare": "चयनित की तुलना करें",
    "education": "शिक्षा",
    "criminal": "आपराधिक मामले",
    "assets": "कुल संपत्ति",
    "background": "पूरी पृष्ठभूमि",
    "noResults": "कोई उम्मीदवार नहीं मिला"
  },
  "voter": {
    "eligibility": "क्या मैं पात्र हूँ?",
    "checklist": "मतदान दिवस चेकलिस्ट",
    "applyCard": "मतदाता पहचान पत्र के लिए आवेदन",
    "age": "आपकी उम्र",
    "citizen": "भारतीय नागरिक?",
    "registered": "पंजीकृत मतदाता?",
    "eligible": "आप मतदान के पात्र हैं!",
    "notEligible": "आप मतदान के पात्र नहीं हैं",
    "needRegister": "आपको पहले पंजीकरण करना होगा"
  },
  "chat": {
    "title": "चुनाव सहायक",
    "placeholder": "अपना प्रश्न लिखें...",
    "send": "भेजें",
    "quickQuestions": "त्वरित प्रश्न",
    "language": "भाषा"
  },
  "common": {
    "loading": "लोड हो रहा है...",
    "error": "कुछ गलत हो गया",
    "retry": "पुनः प्रयास करें",
    "share": "साझा करें",
    "download": "डाउनलोड"
  }
}
```

### Language Selector Component

```typescript
// frontend/src/components/ui/LanguageSelector.tsx
const LANGUAGES = [
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "hi", label: "Hindi", nativeLabel: "हिन्दी" },
] as const;
```

### Backend: Language in Chat Requests

The `language` field in `ChatRequest` tells `ChatService` to instruct Gemini to respond in the user's language:

```python
system_prompt_suffix = f"\nAlways respond in {LANGUAGE_NAMES[language]}."
```

Gemini handles Hindi, Tamil, Telugu, Bengali, and other Indian languages natively -- no separate translation API needed.

## Unit Tests

### `frontend/src/i18n/__tests__/i18n.test.ts`

```typescript
describe("i18n", () => {
  it("defaults to English", () => {});
  it("loads Hindi translations", () => {});
  it("falls back to English for missing keys", () => {});
  it("persists language choice to localStorage", () => {});
  it("all English keys exist in Hindi translation", () => {
    // Structural test: ensure no missing translation keys
  });
});
```

### `frontend/src/components/ui/__tests__/LanguageSelector.test.tsx`

```typescript
describe("LanguageSelector", () => {
  it("renders all available languages", () => {});
  it("highlights current language", () => {});
  it("changes language on selection", () => {});
  it("persists selection to localStorage", () => {});
});
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Missing Hindi translation key | Fallback to English (i18next default) |
| Mixed script in candidate names | Render as-is; names are proper nouns |
| RTL language (Urdu, future) | CSS `dir="rtl"` support planned but not in MVP |
| Gemini responds in wrong language | Retry with explicit language instruction |
| User switches language mid-chat | New messages in new language; history stays as-is |

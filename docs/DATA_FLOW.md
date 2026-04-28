# Data flow and trust boundary (judge-facing)

This diagram shows **what leaves the browser** versus what stays in **Google Cloud** for CivikSutra. EPIC numbers and full voter roll data are **not** stored by the app; users are directed to **ECI / NVSP** for authoritative checks.

```mermaid
flowchart TB
  subgraph client [Browser]
    UI[React SPA]
    MapsKey[Maps JS key restricted by HTTP referrer]
    UI --> MapsKey
  end

  subgraph edge [HTTPS]
    API[FastAPI on Cloud Functions or Cloud Run]
  end

  subgraph data [Data and AI]
    FS[(Firestore cache)]
    Gem[Gemini API]
    Vtx[Vertex FAQ embeddings]
    Tr[Cloud Translation]
    MapsSrv[Maps server-side APIs]
  end

  UI -->|"JSON: booth, chat, candidate, manifesto"| API
  API --> FS
  API --> Gem
  API --> Vtx
  API --> Tr
  API --> MapsSrv
```

**Principle:** Treat the model as **education**, not legal advice. Official rules and dates always come from **ECI / state CEO** portals linked in the in-app trust banner.

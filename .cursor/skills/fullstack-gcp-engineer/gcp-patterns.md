# GCP Architecture Patterns

Reference material for the fullstack-gcp-engineer skill.

## 1. Event-Driven Architecture

```
[Client] → [Cloud Run API] → [Pub/Sub] → [Cloud Function] → [Firestore]
                                       → [Cloud Function] → [BigQuery]
```

- Decouple producers from consumers via Pub/Sub topics.
- Use push subscriptions to Cloud Run; pull subscriptions for batch workers.
- Dead-letter topics for failed messages -- always configure, never lose data.
- Idempotent consumers: use Firestore transactions or message deduplication IDs.

### When to Use
- Async workflows (email, notifications, analytics ingestion).
- Fan-out processing (one event triggers multiple downstream actions).
- Cross-service communication without direct coupling.

## 2. API Gateway Pattern

```
[Client] → [API Gateway / Cloud Load Balancer]
               ├── /api/v1/*   → [Cloud Run: Backend]
               ├── /ai/*       → [Cloud Run: AI Service]
               └── /*          → [Cloud Storage: Frontend SPA]
```

- Single entry point with path-based routing.
- Cloud Armor WAF rules on the load balancer for DDoS and OWASP Top 10.
- SSL termination at the load balancer, not in application code.
- Identity-Aware Proxy (IAP) for internal tools.

## 3. AI/ML Inference Pattern

```
[Client] → [Cloud Run API]
               ├── Lightweight: Gemini API (direct)
               ├── Custom model: Vertex AI Endpoint
               └── Vision/NLP: Pre-trained API
```

### Choosing the Right Service

| Need | Service | Latency | Cost |
|------|---------|---------|------|
| Text generation, summarization | Gemini API | ~1-3s | Per token |
| Image analysis, OCR | Vision API | ~0.5-2s | Per image |
| Custom trained model | Vertex AI Endpoint | Varies | Per node-hour |
| Prototyping prompts | AI Studio | N/A | Free tier |
| Embeddings + search | Vertex AI Vector Search | ~100ms | Per query |

### Best Practices
- Cache repeated inference results in Firestore with TTL.
- Circuit breaker pattern: fall back gracefully when AI services are slow.
- Rate limit AI endpoints per user to control cost.
- Log prompt/response pairs (sans PII) for evaluation and fine-tuning.

## 4. Data Pipeline Pattern

```
[Source] → [Pub/Sub] → [Dataflow / Cloud Function] → [BigQuery]
                                                    → [Firestore (hot path)]
```

- BigQuery for analytics and reporting (cold path).
- Firestore for low-latency application reads (hot path).
- Dual-write via Pub/Sub fan-out, not application-level dual writes.
- BigQuery scheduled queries for materialized views and aggregations.

## 5. Multi-Environment Deployment

```
dev/    → project: myapp-dev    (auto-deploy on PR)
staging → project: myapp-stage  (deploy on merge to main)
prod/   → project: myapp-prod   (manual approval gate)
```

- Separate GCP projects per environment for blast radius isolation.
- Terraform or Pulumi for infrastructure-as-code (committed to repo).
- Cloud Build triggers per environment with appropriate IAM.
- Feature flags via Firebase Remote Config, not code branches.

## 6. Authentication Flow

```
[React App] → Firebase Auth (client SDK)
    ↓ ID Token
[Cloud Run API] → Verify token → Extract claims → Authorize
```

### Implementation

```python
from firebase_admin import auth as firebase_auth

async def verify_firebase_token(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        decoded = firebase_auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    return decoded
```

- Verify tokens server-side on every request -- never trust client-side auth alone.
- Use custom claims for role-based access control (RBAC).
- Token refresh handled by Firebase client SDK transparently.
- Session cookies for SSR (Next.js) via `firebase-admin` session cookie API.

## 7. File Upload Pattern

```
[Client] → [Cloud Run: Generate Signed URL] → [Client uploads direct to GCS]
    ↓ Pub/Sub notification
[Cloud Function: Process file] → [Vision API / Transcription]
    ↓
[Firestore: Update metadata]
```

- Never proxy large files through your API. Use signed URLs for direct GCS upload.
- Set content-type restrictions and max file size in the signed URL policy.
- GCS object notifications via Pub/Sub trigger downstream processing.
- Virus scanning via Cloud Functions before making files accessible.

## 8. Cost Optimization Patterns

| Pattern | Savings |
|---------|---------|
| Cloud Run min-instances=0 for non-critical services | Idle cost → $0 |
| Committed use discounts for stable workloads | 20-57% |
| Firestore TTL policies for transient data | Storage reduction |
| BigQuery partitioned tables + clustering | Query cost reduction |
| Regional vs multi-regional storage | 2x cost difference |
| Preemptible/Spot VMs for batch jobs | 60-91% |
| AI API caching (identical prompts) | Linear with hit rate |

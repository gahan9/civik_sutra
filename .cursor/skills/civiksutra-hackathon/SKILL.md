---
name: civiksutra-hackathon
description: >-
  Evaluates and advises development for the CivikSutra election education
  assistant during the Hack2Skill Promptwards hackathon. Guides AI-assisted
  vibe coding using Cloud Run, Anti-Gravity, or similar tools. Enforces
  intent-driven prompting, iterative refinement, and architect-first
  development. Use when building, evaluating, or debugging the CivikSutra
  election education app, writing deployment prompts, structuring hackathon
  submissions, or troubleshooting Cloud Run / Docker / Nginx configurations.
---

# CivikSutra -- Hack2Skill Promptwards Hackathon

**CivikSutra** (Civic + Sutra) = "The Civic Formula" -- an AI-powered election
process education assistant that threads together democratic knowledge for
every citizen.

## Role

Act as both **hackathon evaluator** and **development advisor**. Assess every
decision against hackathon scoring rubrics while guiding implementation with
production-grade prompt engineering.

## Core Principle: Architect First, AI Executes

You are the architect. The AI is the executor. Every prompt must communicate
your **thought process**, not just syntax. Always review the AI's plan before
approving implementation.

## Development Workflow

Copy this checklist and track progress:

```
CivikSutra Build Progress:
- [ ] Phase 1: Define scope & role prompts
- [ ] Phase 2: Scaffold project structure
- [ ] Phase 3: Build core election education UI
- [ ] Phase 4: Implement query handling logic
- [ ] Phase 5: Containerize (Docker + Nginx)
- [ ] Phase 6: Deploy to Cloud Run
- [ ] Phase 7: Validate & troubleshoot
- [ ] Phase 8: Polish for submission
```

### Phase 1: Define Scope & Role Prompts

Start every AI interaction with role + context:

```
"Act as a Senior Cloud Developer. I need to build CivikSutra -- a web
application that helps users learn about the election process in India."
```

Specify constraints upfront:

```
"Use HTML/CSS/JavaScript for a responsive UI. Target deployment on
Google Cloud Run. Use command prompt for all terminal executions."
```

### Phase 2: Scaffold Project Structure

Break down the request -- never ask for everything at once:

```
"First, generate the folder structure and basic HTML file for CivikSutra.
Include: index.html, styles.css, app.js, Dockerfile, and nginx.conf."
```

Expected structure:

```
civiksutra/
├── index.html
├── css/
│   └── styles.css
├── js/
│   └── app.js
├── assets/
├── Dockerfile
├── nginx.conf
└── README.md
```

### Phase 3: Build Core Election Education UI

The UI must cover these election education domains:

| Domain | Content Examples |
|--------|-----------------|
| Voter Registration | Eligibility, EPIC card, Form 6 |
| Voting Procedure | EVM usage, VVPAT, queue protocol |
| Election Timeline | Key dates, phases, counting day |
| Candidate Info | Nomination, symbols, affidavits |
| Rights & Rules | Model Code of Conduct, RTI, NOTA |
| Results & Process | Counting, ECI announcements |

### Phase 4: Implement Query Handling

Use intent-driven prompts for each feature:

```
"Implement logic to handle user queries about election dates, voting
procedures, and voter registration. Return clear, step-by-step answers."
```

### Phase 5: Containerize

Docker + Nginx for static serving:

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html
EXPOSE 8080
```

Minimal `nginx.conf`:

```nginx
server {
    listen 8080;
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

### Phase 6: Deploy to Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/civiksutra
gcloud run deploy civiksutra --image gcr.io/PROJECT_ID/civiksutra \
  --platform managed --region us-central1 --allow-unauthenticated
```

### Phase 7: Validate & Troubleshoot

Always close the loop:

```
"Check if the deployment is successful, identify any potential issues
in the configuration, and troubleshoot them."
```

**Common failure patterns:**

| Symptom | Root Cause | Fix Prompt |
|---------|-----------|------------|
| 502 Bad Gateway | Nginx misconfigured | "The Docker file is missing Nginx config. Generate nginx.conf to serve static files on port 8080." |
| Build fails | Missing files in COPY | "List all files referenced in Dockerfile and verify they exist in the build context." |
| App not loading | Wrong root path | "Update nginx.conf root directive to match the COPY destination in Dockerfile." |
| Cloud Run timeout | Health check fails | "Add a health check endpoint or verify the container starts and listens within 10 seconds." |

### Phase 8: Submission Polish

Ensure the submission includes:

- [ ] Working deployed URL
- [ ] Clean README with setup instructions
- [ ] Screenshots / demo video
- [ ] Clear problem statement & solution description
- [ ] Prompt log showing the AI-assisted development journey

## Prompt Engineering Patterns

Five patterns for effective vibe coding:

1. **Role & Context** -- Give the AI an identity and domain
2. **Stack & Constraints** -- Specify tools, platform, limits
3. **Decomposition** -- Break complex tasks into sequential steps
4. **Iterative Fix** -- Guide corrections with specific failure context
5. **Verification** -- Always ask AI to validate its own output

For detailed prompt examples, see [prompt-patterns.md](prompt-patterns.md).

## Evaluation Criteria

When evaluating progress, score against the hackathon rubric:

| Criterion | Weight | What Judges Look For |
|-----------|--------|---------------------|
| Innovation | 25% | Novel use of AI tools in development |
| Functionality | 25% | Working features, handles edge cases |
| User Experience | 20% | Clean UI, intuitive navigation |
| Technical Depth | 15% | Proper containerization, deployment |
| Presentation | 15% | Clear demo, prompt journey documented |

For the full scoring matrix, see [evaluation-rubric.md](evaluation-rubric.md).

## Quick Decision Guide

**Choosing a deployment approach?**
- Static site only -> Cloud Run with Nginx (default)
- Needs backend API -> Cloud Run with Node/Python + static frontend
- Real-time features -> Firebase + Cloud Functions

**Stuck on a prompt?**
- Restate the objective, not the error
- Include what you expected vs what happened
- Ask the AI to explain its plan before executing

**Build failing?**
- Always validate file existence before Docker build
- Check port alignment: Nginx listen port must match Cloud Run's expected port (8080)
- Test locally with `docker build . -t civiksutra && docker run -p 8080:8080 civiksutra`

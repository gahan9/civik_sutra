# CivikSutra -- Hackathon Evaluation Rubric

Scoring matrix for self-assessment and final submission readiness.

## Overall Scoring

| Criterion | Weight | 1 (Poor) | 3 (Average) | 5 (Excellent) |
|-----------|--------|----------|-------------|---------------|
| **Innovation** | 25% | Standard tutorial app | Some unique features | Novel AI-coding workflow + civic-tech twist |
| **Functionality** | 25% | Broken / partial features | Core features work | All features polished, edge cases handled |
| **User Experience** | 20% | Raw HTML, no styling | Decent layout, some responsiveness | Beautiful, accessible, mobile-first |
| **Technical Depth** | 15% | Runs locally only | Dockerized | Cloud Run deployed, CI/CD aware |
| **Presentation** | 15% | No demo materials | Basic README | Full prompt journey + video demo |

## Detailed Breakdown

### Innovation (25%)

What judges want to see:

- **AI-assisted development journey** -- not just the final product, but
  HOW you used AI tools to build it (prompt logs, iterations, refinements)
- **Vibe coding showcase** -- demonstrate the architect-executor model where
  you think, AI builds, you review
- **Election domain novelty** -- go beyond a basic FAQ; add interactive
  elements like eligibility checkers, timeline visualizers, or mock ballot UIs

Self-check:
- [ ] Can you show 5+ distinct AI prompts that shaped the app?
- [ ] Is there at least one feature a generic tutorial wouldn't have?
- [ ] Did you document a moment where AI got it wrong and you corrected it?

### Functionality (25%)

Required features for CivikSutra:

| Feature | Must Have | Nice to Have |
|---------|-----------|-------------|
| Election info display | Static content pages | Searchable knowledge base |
| Voter eligibility | Age/citizenship check | State-specific rules |
| Voting procedure | Step-by-step guide | Interactive walkthrough |
| Navigation | Working sidebar/menu | Keyboard accessible |
| Error handling | Graceful fallbacks | User-friendly error messages |
| Offline support | -- | Service worker caching |

Self-check:
- [ ] Every navigation link works
- [ ] No JavaScript console errors
- [ ] Content is factually accurate
- [ ] App handles empty states and edge cases

### User Experience (20%)

| Aspect | Minimum | Target |
|--------|---------|--------|
| Responsiveness | Readable on mobile | Fully adaptive layout |
| Load time | Under 5s on 4G | Under 2s on 4G |
| Accessibility | Readable text | WCAG 2.1 AA compliant |
| Visual design | Consistent colors | Professional civic theme |
| Interaction | Click-based | Smooth transitions, feedback |

Self-check:
- [ ] Tested on mobile viewport (375px, 768px, 1024px)
- [ ] Text contrast ratio meets 4.5:1 minimum
- [ ] Interactive elements have hover/focus states
- [ ] No horizontal scrolling on any viewport

### Technical Depth (15%)

| Level | What It Means |
|-------|---------------|
| Basic | HTML/CSS/JS running locally |
| Intermediate | Dockerized with proper Nginx config |
| Advanced | Deployed to Cloud Run, port 8080 aligned |
| Expert | Health checks, caching headers, gzip, CI/CD pipeline |

Self-check:
- [ ] Dockerfile builds without errors
- [ ] `docker run` serves the app locally on 8080
- [ ] Cloud Run deployment URL is live and accessible
- [ ] No secrets or credentials in source code

### Presentation (15%)

Submission package must include:

| Item | Format | Purpose |
|------|--------|---------|
| README.md | Markdown | Setup, architecture, prompt journey |
| Demo URL | Live link | Working deployed application |
| Prompt log | Markdown/PDF | AI interaction history showing iterations |
| Screenshots | PNG/JPG | Key screens on desktop and mobile |
| Demo video | MP4/link | 2-3 min walkthrough (optional but high-impact) |

Self-check:
- [ ] README has clear setup instructions (clone, build, deploy)
- [ ] Prompt log shows at least 3 iteration cycles
- [ ] Screenshots cover all major sections
- [ ] Problem statement is clearly articulated

## Quick Readiness Score

Rate each criterion 1-5, multiply by weight, sum for a total out of 5.0:

```
Innovation:      ___ x 0.25 = ___
Functionality:   ___ x 0.25 = ___
User Experience: ___ x 0.20 = ___
Technical Depth: ___ x 0.15 = ___
Presentation:    ___ x 0.15 = ___
                 TOTAL:       ___  / 5.0
```

**Target: 3.5+ to be competitive, 4.0+ to place.**

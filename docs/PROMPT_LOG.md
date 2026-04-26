# Prompt Journey

This log documents the AI-assisted development path for the CivikSutra
hackathon submission.

## Build Decisions

1. **Architect first, then implement**
   - Chose one monolithic Firebase deployment: Hosting, Python Cloud Functions,
     and Firestore rules ship together with `firebase deploy`.
   - Kept frontend and function code in separate directories only as source-code
     boundaries, not separate deployments.

2. **Booth Finder first**
   - Implemented the highest-impact voter journey before broader candidate and
     manifesto features.
   - Built GPS/manual search, nearby booth cards, directions, traffic level, and
     best visit window.

3. **Responsible civic accuracy**
   - Explicitly separated "nearby polling place" from "official assigned booth."
   - Added ECI Electoral Search handoff instead of scraping voter-roll data.
   - Avoided storing EPIC or voter personal data.

4. **Verification loop**
   - Backend tests: `python -m pytest tests -q`
   - Frontend tests: `npm test`
   - Production build: `npm run build`
   - Live smoke tests against Firebase Hosting and function rewrites.

## Current Demo URL

https://civiksutra-2604261729.web.app

## Next Prompt Targets

- Ingest public state CEO polling-station PDFs/pages into Firestore.
- Add candidate intelligence with grounded citations.
- Add Hindi language support and voter readiness checklist.

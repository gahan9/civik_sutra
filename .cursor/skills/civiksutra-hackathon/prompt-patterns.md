# CivikSutra -- Prompt Patterns Reference

Detailed prompt examples for each phase of the vibe-coding workflow.

## Pattern 1: Role & Context

Set the AI's identity before any technical request.

**Scaffolding:**
```
Act as a Senior Cloud Developer specializing in civic-tech applications.
I am building CivikSutra, an election process education assistant for
Indian citizens. The app must be accessible, mobile-responsive, and
deployable on Google Cloud Run.
```

**Content generation:**
```
Act as an Election Commission subject matter expert. Generate accurate,
simplified content explaining the EVM voting process for first-time voters.
Include step-by-step instructions from entering the booth to pressing the
button and verifying via VVPAT slip.
```

## Pattern 2: Stack & Constraints

Always specify what you're working with and what the boundaries are.

**Good:**
```
Create a responsive web UI using vanilla HTML5, CSS3, and ES6 JavaScript.
No frameworks. The app must work offline-first and load under 3 seconds
on a 3G connection. Use semantic HTML for accessibility.
```

**Bad:**
```
Make me a website for elections.
```

## Pattern 3: Decomposition

Never ask for the entire app at once. Build layer by layer.

**Step 1 -- Structure:**
```
Generate the project folder structure for CivikSutra. Include: HTML entry
point, CSS directory, JS directory, assets folder, Dockerfile, and
nginx.conf. Do not write any application logic yet.
```

**Step 2 -- Layout:**
```
Now create the index.html with a navigation sidebar listing these sections:
Voter Registration, Voting Day Guide, Election Timeline, Know Your Rights,
NOTA Information. Use semantic HTML5 elements. Leave content areas empty
with placeholder comments.
```

**Step 3 -- Styling:**
```
Style the CivikSutra app with a professional civic theme. Use the Indian
tricolor palette (#FF9933 saffron, #FFFFFF white, #138808 green) as accent
colors on a clean neutral background. Make the sidebar collapsible on
mobile screens.
```

**Step 4 -- Logic:**
```
Implement the JavaScript module for the "Voter Registration" section.
When a user selects their state and age, show eligibility status and
list required documents for Form 6 submission. Use a local JSON data
file, no API calls needed.
```

## Pattern 4: Iterative Fix

When something breaks, tell the AI exactly what went wrong and what you expected.

**Docker build failure:**
```
The Docker build failed with: "COPY failed: file not found in build context."
The Dockerfile references nginx.conf but the file is in the config/ subdirectory.
Update the COPY instruction to use the correct relative path, or move nginx.conf
to the project root.
```

**Deployment failure:**
```
Cloud Run deployment succeeded but the app shows a blank page. The container
logs show "nginx: [emerg] bind() to 0.0.0.0:80 failed (13: Permission denied)".
Cloud Run requires port 8080. Update nginx.conf to listen on 8080 instead of 80.
```

**UI bug:**
```
The sidebar navigation works on desktop but on mobile (375px width) the menu
items overflow outside the viewport. Add a hamburger toggle button and hide
the sidebar behind a slide-in panel on screens below 768px.
```

## Pattern 5: Verification

Always close the loop by asking AI to validate its own work.

**Post-deployment:**
```
The app is deployed at https://civiksutra-xxxxx.run.app. Verify:
1. The homepage loads without console errors
2. All navigation links resolve correctly
3. The Docker container responds to health checks on /
4. Static assets (CSS, JS, images) are served with correct MIME types
```

**Pre-submission:**
```
Review the entire CivikSutra project for hackathon readiness:
1. Is the README complete with setup instructions?
2. Are all features functional and error-free?
3. Is the prompt journey documented?
4. Are there any hardcoded secrets or credentials?
5. Does the UI look professional on both mobile and desktop?
```

## Compound Prompt Examples

Combine multiple patterns for complex tasks:

**Full-stack feature request:**
```
Act as a Full Stack Developer. [ROLE]

I need to add a "Know Your Candidate" feature to CivikSutra. [CONTEXT]

Technical requirements: [CONSTRAINTS]
- Fetch candidate data from a local JSON file (no external APIs)
- Display candidate name, party, symbol, and constituency
- Add a search bar to filter by constituency name
- Use vanilla JavaScript, no libraries

Implementation order: [DECOMPOSITION]
1. First, create the candidates.json data file with 10 sample entries
2. Then, build the HTML section with search input and results grid
3. Finally, implement the filter logic with debounced input handling

After implementation, verify the search works with partial matches
and handles the "no results" case gracefully. [VERIFICATION]
```

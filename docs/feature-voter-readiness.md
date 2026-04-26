# Feature: Voter Readiness

**Module**: `voter` | **Phase**: 3 (Depth) | **Priority**: P1

Voter eligibility checker, election card (EPIC) application guide, voting day checklist with documents, and step-by-step booth procedure walkthrough.

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| VR-1 | Citizen | Check if I'm eligible to vote | I know my voting rights |
| VR-2 | Citizen | Get step-by-step guide to apply for a voter ID card | I can register before the deadline |
| VR-3 | Voter | See a checklist of things to do/bring on voting day | I don't forget anything important |
| VR-4 | First-time voter | Understand the EVM/VVPAT voting procedure | I know exactly what to expect at the booth |
| VR-5 | Voter | Know the accepted photo ID documents | I carry the right identification |
| VR-6 | Voter with disability | Know about accessibility facilities at my booth | I can plan for any assistance needed |

## UI Wireframe

### Eligibility Checker

```
┌─────────────────────────────────────┐
│  ✅ Am I Eligible to Vote?           │
│                                     │
│  Answer a few questions:            │
│                                     │
│  1. What is your age?               │
│  ┌─────────┐                        │
│  │ 19      │ years                  │
│  └─────────┘                        │
│                                     │
│  2. Are you an Indian citizen?      │
│  (●) Yes  ( ) No  ( ) NRI          │
│                                     │
│  3. Are you registered as a voter?  │
│  ( ) Yes  (●) No  ( ) Not sure     │
│                                     │
│  4. State of residence:             │
│  ┌──────────────────┐              │
│  │ Delhi          ▼ │              │
│  └──────────────────┘              │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ✅ You ARE eligible to vote!     ││
│  │                                 ││
│  │ But you need to register first. ││
│  │ Deadline: 15 days before        ││
│  │ election date.                  ││
│  │                                 ││
│  │ [Apply for Voter ID →]          ││
│  │ [Check if already registered →] ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Voting Day Checklist

```
┌─────────────────────────────────────┐
│  📋 Voting Day Checklist             │
│                                     │
│  Before You Leave                   │
│  ☑ Carry valid photo ID (see list)  │
│  ☑ Know your booth number & address │
│  ☑ Check polling hours (7 AM-6 PM)  │
│  ☐ Charge your phone (for maps)     │
│  ☐ Carry water & umbrella           │
│                                     │
│  Accepted Photo IDs (any one):      │
│  ┌─────────────────────────────────┐│
│  │ • EPIC (Voter ID Card) ★        ││
│  │ • Aadhaar Card                  ││
│  │ • Passport                      ││
│  │ • Driving License               ││
│  │ • PAN Card                      ││
│  │ • MNREGA Job Card               ││
│  │ • Bank/Post Office Passbook     ││
│  │   with photo                    ││
│  │ • Govt employee ID              ││
│  │ • Student ID (govt institution) ││
│  │ • Disability ID (UDID)          ││
│  │ • Pension document with photo   ││
│  │                                 ││
│  │ ★ = Preferred, carries e-EPIC   ││
│  └─────────────────────────────────┘│
│                                     │
│  At The Booth                       │
│  ☐ Queue at your assigned booth     │
│  ☐ Show photo ID to officer         │
│  ☐ Get indelible ink mark on finger │
│  ☐ Receive ballot slip              │
│  ☐ Enter voting compartment ALONE   │
│  ☐ Press button next to candidate   │
│  ☐ Wait for BEEP + VVPAT slip      │
│  ☐ Verify printed name on VVPAT     │
│  ☐ Exit                            │
│                                     │
│  ⚠️ Do NOT:                         │
│  • Take phone into voting booth     │
│  • Take photos of EVM/ballot        │
│  • Show your vote to anyone         │
│  • Wear party symbols/colors        │
│                                     │
│  ♿ Accessibility:                   │
│  • Wheelchair ramps at most booths  │
│  • Braille-enabled EVMs available   │
│  • Companion allowed for PWD voters │
│  • Priority queue for elderly/PWD   │
│                                     │
│  [Find My Booth →] [Share Checklist]│
└─────────────────────────────────────┘
```

### EPIC Application Guide

```
┌─────────────────────────────────────┐
│  🪪 Apply for Voter ID (EPIC)       │
│                                     │
│  Step 1 of 5: Visit NVSP Portal     │
│  ┌─────────────────────────────────┐│
│  │ Go to:                          ││
│  │ https://www.nvsp.in             ││
│  │                                 ││
│  │ Click "New Voter Registration"  ││
│  │ (Form 6)                        ││
│  │                                 ││
│  │ [Open NVSP Portal →]            ││
│  └─────────────────────────────────┘│
│                                     │
│  Step 2 of 5: Fill Form 6           │
│  ┌─────────────────────────────────┐│
│  │ Required information:           ││
│  │ • Full name (as on Aadhaar)     ││
│  │ • Date of birth                 ││
│  │ • Current address               ││
│  │ • Relation (father/husband)     ││
│  │ • Photo (passport size, <50KB)  ││
│  │ • Age proof document            ││
│  │ • Address proof document        ││
│  └─────────────────────────────────┘│
│                                     │
│  ... steps 3-5 ...                  │
│                                     │
│  Important Dates:                   │
│  • Apply at least 15 days before    │
│    election date                    │
│  • Processing: 7-15 working days    │
│  • Track status: NVSP portal        │
│                                     │
│  Already applied?                   │
│  [Track Application Status →]       │
└─────────────────────────────────────┘
```

## Implementation

This feature is **primarily frontend** with static content and minimal backend logic. The eligibility checker runs client-side. External links point to ECI/NVSP portals.

### Frontend Components

#### `EligibilityCheck` (`frontend/src/components/voter/EligibilityCheck.tsx`)

Interactive questionnaire:
- Age input (number)
- Citizenship radio (Citizen / NRI / Non-citizen)
- Registration status radio (Yes / No / Not sure)
- State dropdown
- Result: eligible/not-eligible with next steps

Logic runs entirely client-side:
```typescript
function checkEligibility(age: number, citizen: string, registered: string): EligibilityResult {
  if (age < 18) return { eligible: false, reason: "Must be 18+ on qualifying date" };
  if (citizen === "non-citizen") return { eligible: false, reason: "Must be Indian citizen" };
  if (citizen === "nri") return { eligible: true, note: "NRIs can vote. Register as overseas voter via Form 6A." };
  if (registered === "no") return { eligible: true, action: "register", note: "You need to register first." };
  if (registered === "not_sure") return { eligible: true, action: "check", note: "Verify your registration on NVSP." };
  return { eligible: true, action: "ready" };
}
```

#### `VotingChecklist` (`frontend/src/components/voter/VotingChecklist.tsx`)

Static checklist with local storage persistence:
- Checkboxes save state to `localStorage`
- Grouped by: "Before You Leave" / "At The Booth" / "Don'ts"
- Accessible offline (PWA cached)
- Share button generates text summary for WhatsApp

#### `CardApplication` (`frontend/src/components/voter/CardApplication.tsx`)

Step-by-step wizard:
- 5 steps with progress bar
- Each step shows what to do + screenshot/description
- External links to NVSP portal
- "Track Application" button with NVSP status URL

#### `BoothProcedure` (`frontend/src/components/voter/BoothProcedure.tsx`)

Visual guide to the voting process:
- Step-by-step with icons/illustrations
- EVM and VVPAT explanation
- NOTA explanation
- Accessibility information

### Static Data (`frontend/src/data/voter-readiness.ts`)

```typescript
export const ACCEPTED_PHOTO_IDS = [
  { name: "EPIC (Voter ID Card)", preferred: true, eEpic: true },
  { name: "Aadhaar Card", preferred: false },
  { name: "Passport", preferred: false },
  { name: "Driving License", preferred: false },
  { name: "PAN Card", preferred: false },
  { name: "MNREGA Job Card", preferred: false },
  { name: "Bank/Post Office Passbook with photo", preferred: false },
  { name: "Government Employee ID", preferred: false },
  { name: "Student ID (govt institution)", preferred: false },
  { name: "Disability ID (UDID)", preferred: false },
  { name: "Pension document with photo", preferred: false },
  { name: "MP/MLA/MLC ID", preferred: false },
] as const;

export const NVSP_URLS = {
  portal: "https://www.nvsp.in",
  newRegistration: "https://www.nvsp.in/Forms/Forms/form6",
  trackApplication: "https://www.nvsp.in/Forms/Forms/trackstatus",
  searchName: "https://electoralsearch.eci.gov.in/",
  eEpic: "https://www.nvsp.in/Forms/Forms/DownloadeEPIC",
} as const;

export const APPLICATION_STEPS = [
  {
    step: 1,
    title: "Visit NVSP Portal",
    description: "Go to nvsp.in and click 'New Voter Registration' (Form 6)",
    url: "https://www.nvsp.in/Forms/Forms/form6",
  },
  {
    step: 2,
    title: "Fill Form 6",
    description: "Enter personal details, address, and upload photo + documents",
    requiredDocs: ["Passport photo (<50KB)", "Age proof", "Address proof"],
  },
  {
    step: 3,
    title: "Submit & Note Reference",
    description: "Submit the form and save the reference number for tracking",
  },
  {
    step: 4,
    title: "Verification Visit",
    description: "BLO (Booth Level Officer) will visit your address for verification",
    timeline: "Usually within 7-15 days",
  },
  {
    step: 5,
    title: "Receive EPIC",
    description: "Collect physical card or download e-EPIC from NVSP portal",
    url: "https://www.nvsp.in/Forms/Forms/DownloadeEPIC",
  },
] as const;
```

## Unit Tests

### `frontend/src/components/voter/__tests__/EligibilityCheck.test.tsx`

```typescript
describe("EligibilityCheck", () => {
  it("shows ineligible for age below 18", () => {});
  it("shows eligible for age 18 and above", () => {});
  it("shows ineligible for non-citizens", () => {});
  it("shows NRI voting guidance for NRI selection", () => {});
  it("prompts registration for unregistered eligible voters", () => {});
  it("suggests NVSP check for 'not sure' registration", () => {});
  it("shows 'ready to vote' for registered eligible voters", () => {});
});
```

### `frontend/src/components/voter/__tests__/Checklist.test.tsx`

```typescript
describe("VotingChecklist", () => {
  it("renders all checklist items", () => {});
  it("persists checked state to localStorage", () => {});
  it("restores checked state from localStorage", () => {});
  it("groups items by category", () => {});
  it("generates shareable text summary", () => {});
});
```

### `frontend/src/components/voter/__tests__/CardApplication.test.tsx`

```typescript
describe("CardApplication", () => {
  it("renders all 5 steps", () => {});
  it("navigates between steps", () => {});
  it("shows progress bar", () => {});
  it("opens NVSP link for step 1", () => {});
  it("lists required documents for step 2", () => {});
});
```

## Data Sources

| Information | Source | Update Frequency |
|-------------|--------|-----------------|
| Accepted photo IDs | ECI official list | Static (changes only via gazette notification) |
| NVSP portal URLs | nvsp.in | Static (stable URLs) |
| Eligibility rules | Representation of People Act, 1950 | Static |
| EVM/VVPAT procedure | ECI voter guide | Static |
| Accessibility facilities | Per-booth data from ECI | Per election |

## Edge Cases

| Scenario | Handling |
|----------|----------|
| User exactly 18 on election day | Eligible -- qualifying date is Jan 1 of election year |
| NRI voter | Show Form 6A process, overseas voter registration |
| User has applied but not received EPIC | Show tracking link + list of alternative IDs |
| User's EPIC shows wrong address | Guide to Form 8 (correction) on NVSP |
| Booth has no accessibility data | Show "Contact your local election office for accessibility details" |
| Election dates not announced | Show "Dates not yet announced for your state" |

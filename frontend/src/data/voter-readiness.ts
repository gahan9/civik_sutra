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
    description:
      "Go to nvsp.in and click 'New Voter Registration' (Form 6)",
    url: "https://www.nvsp.in/Forms/Forms/form6",
  },
  {
    step: 2,
    title: "Fill Form 6",
    description:
      "Enter personal details, address, and upload photo + documents",
    requiredDocs: ["Passport photo (<50KB)", "Age proof", "Address proof"],
  },
  {
    step: 3,
    title: "Submit & Note Reference",
    description:
      "Submit the form and save the reference number for tracking",
  },
  {
    step: 4,
    title: "Verification Visit",
    description:
      "BLO (Booth Level Officer) will visit your address for verification",
    timeline: "Usually within 7-15 days",
  },
  {
    step: 5,
    title: "Receive EPIC",
    description:
      "Collect physical card or download e-EPIC from NVSP portal",
    url: "https://www.nvsp.in/Forms/Forms/DownloadeEPIC",
  },
] as const;

export const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
  "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
  "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
  "West Bengal", "Delhi", "Jammu & Kashmir", "Ladakh", "Puducherry",
  "Chandigarh", "Andaman & Nicobar Islands", "Dadra & Nagar Haveli",
  "Lakshadweep",
] as const;

export interface ChecklistItem {
  id: string;
  label: string;
  category: "before" | "at_booth" | "dont";
}

export const CHECKLIST_ITEMS: ChecklistItem[] = [
  { id: "photo_id", label: "Carry valid photo ID (see accepted list)", category: "before" },
  { id: "booth_address", label: "Know your booth number & address", category: "before" },
  { id: "polling_hours", label: "Check polling hours (7 AM - 6 PM)", category: "before" },
  { id: "charge_phone", label: "Charge your phone (for maps)", category: "before" },
  { id: "water_umbrella", label: "Carry water & umbrella", category: "before" },
  { id: "queue_booth", label: "Queue at your assigned booth", category: "at_booth" },
  { id: "show_id", label: "Show photo ID to presiding officer", category: "at_booth" },
  { id: "ink_mark", label: "Get indelible ink mark on finger", category: "at_booth" },
  { id: "ballot_slip", label: "Receive ballot slip", category: "at_booth" },
  { id: "enter_alone", label: "Enter voting compartment ALONE", category: "at_booth" },
  { id: "press_button", label: "Press button next to your candidate", category: "at_booth" },
  { id: "wait_beep", label: "Wait for BEEP + VVPAT slip", category: "at_booth" },
  { id: "verify_vvpat", label: "Verify printed name on VVPAT", category: "at_booth" },
  { id: "exit", label: "Exit the booth", category: "at_booth" },
  { id: "no_phone", label: "Do NOT take phone into voting compartment", category: "dont" },
  { id: "no_photos", label: "Do NOT take photos of EVM/ballot", category: "dont" },
  { id: "no_show_vote", label: "Do NOT show your vote to anyone", category: "dont" },
  { id: "no_party_symbols", label: "Do NOT wear party symbols/colors", category: "dont" },
];

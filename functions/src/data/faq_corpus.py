"""Curated FAQ corpus for the CivikSutra semantic search pipeline.

Each entry covers a recurring Indian voter question. The corpus is embedded
once at startup using ``text-embedding-004`` and cached for the process
lifetime. Subsequent voter queries only require embedding the question and a
single cosine-similarity scan over the cached vectors.

Sources are limited to ECI, NVSP and the Representation of the People Act so
we never present unverified content to the voter.
"""

from __future__ import annotations

from typing import Final

FAQEntry = dict[str, str]

FAQ_CORPUS: Final[list[FAQEntry]] = [
    {
        "id": "eligibility-age",
        "topic": "Eligibility",
        "question": "What is the minimum age to vote in Indian elections?",
        "answer": (
            "An Indian citizen must be at least 18 years old on the qualifying "
            "date (1 January of the year of the electoral roll revision) to be "
            "eligible to vote, as defined by Article 326 of the Constitution."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "eligibility-citizenship",
        "topic": "Eligibility",
        "question": "Can NRIs (Non-Resident Indians) vote?",
        "answer": (
            "Yes. NRIs holding an Indian passport can register as overseas "
            "electors via Form 6A on the NVSP portal and vote in person at the "
            "polling station of their registered constituency."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "eligibility-disqualification",
        "topic": "Eligibility",
        "question": "Who is disqualified from voting?",
        "answer": (
            "Persons of unsound mind declared by a competent court, and persons "
            "convicted of specific offences listed in Section 16 of the "
            "Representation of the People Act, 1950 may be disqualified."
        ),
        "source": "Representation of the People Act, 1950",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "registration-form6",
        "topic": "Registration",
        "question": "How do I register as a new voter?",
        "answer": (
            "Submit Form 6 either online through the NVSP portal "
            "(www.nvsp.in) or in person at your local Electoral Registration "
            "Officer. You will need proof of age, identity and Indian "
            "residence."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "registration-correction",
        "topic": "Registration",
        "question": "How do I correct details on my voter ID?",
        "answer": (
            "Use Form 8 on the NVSP portal to correct entries such as name, "
            "date of birth, address, photo or relation. Upload supporting "
            "documents and track the application via the reference ID."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "registration-transfer",
        "topic": "Registration",
        "question": "I moved cities — how do I transfer my voter registration?",
        "answer": (
            "Submit Form 8A within the same constituency, or a fresh Form 6 if "
            "moving to a different constituency. Your previous entry will be "
            "deleted automatically once the new entry is approved."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "registration-epic",
        "topic": "Registration",
        "question": "What is an EPIC card?",
        "answer": (
            "EPIC stands for Elector's Photo Identity Card. It is the "
            "government-issued photo ID linked to your entry on the electoral "
            "roll and is the primary identification document for voting."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "registration-documents",
        "topic": "Registration",
        "question": "What documents do I need to register as a voter?",
        "answer": (
            "Proof of age (birth certificate, school certificate, passport or "
            "Aadhaar), proof of address (utility bill, bank passbook, ration "
            "card or rental agreement) and a passport-size photograph."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "voting-evm",
        "topic": "Voting Procedure",
        "question": "How does an EVM (Electronic Voting Machine) work?",
        "answer": (
            "An EVM has a Control Unit operated by the polling officer and a "
            "Ballot Unit where the voter presses the blue button against their "
            "chosen candidate. Each press is acknowledged by a beep and "
            "recorded on a tamper-sealed memory."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-vvpat",
        "topic": "Voting Procedure",
        "question": "What is VVPAT and why does it matter?",
        "answer": (
            "Voter Verifiable Paper Audit Trail prints a paper slip with the "
            "candidate's serial number, name and party symbol. The slip is "
            "visible behind a glass for seven seconds before dropping into a "
            "sealed compartment, allowing audit verification."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-nota",
        "topic": "Voting Procedure",
        "question": "What is NOTA and how do I use it?",
        "answer": (
            "NOTA (None of the Above) is the last option on the EVM ballot "
            "unit. Selecting it records your participation while indicating "
            "you do not endorse any contesting candidate. NOTA votes are "
            "counted but cannot win the seat."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-postal",
        "topic": "Voting Procedure",
        "question": "Who is allowed to vote by postal ballot?",
        "answer": (
            "Service voters, electors on election duty, voters above 80, "
            "persons with disabilities and those under preventive detention "
            "may apply for postal ballots subject to ECI guidelines."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-secrecy",
        "topic": "Voting Procedure",
        "question": "How is the secrecy of my vote protected?",
        "answer": (
            "The polling booth has a privacy compartment, the EVM does not "
            "store identifying information about the voter, and Section 128 "
            "of the Representation of the People Act criminalises any breach "
            "of voting secrecy."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-id-documents",
        "topic": "Polling Day",
        "question": "Which IDs are accepted at the polling station?",
        "answer": (
            "EPIC is the primary identification. Alternatives accepted include "
            "Aadhaar, PAN, passport, driving licence, service ID with photo, "
            "MNREGA job card, bank/post-office passbook with photo, pension "
            "document, and the unique photo voter slip."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-hours",
        "topic": "Polling Day",
        "question": "What are polling station opening hours?",
        "answer": (
            "Polling stations are typically open from 7:00 AM to 6:00 PM, "
            "though hours may vary by constituency and security situation. "
            "Voters in queue at the closing time are allowed to cast their "
            "vote."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-disability",
        "topic": "Polling Day",
        "question": "What accessibility support is available for disabled voters?",
        "answer": (
            "Polling stations provide ramps, wheelchair access, Braille EVM "
            "ballot units and priority queueing for persons with disabilities, "
            "senior citizens and pregnant women under the ECI Accessible "
            "Elections framework."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "voting-different-city",
        "topic": "Polling Day",
        "question": "Can I vote if I am in a different city on polling day?",
        "answer": (
            "You can only vote at the polling station where your name is on "
            "the electoral roll. Domestic migrants must either travel back or "
            "transfer their registration via Form 6/8A in advance. Postal "
            "ballots are not available for general electors."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "candidate-affidavit",
        "topic": "Candidate Information",
        "question": "How do I read a candidate's affidavit?",
        "answer": (
            "Affidavits are filed in Form 26 and disclose criminal cases, "
            "assets, liabilities and educational qualifications. They are "
            "available on the ECI website and aggregator MyNeta.info."
        ),
        "source": "MyNeta.info",
        "source_url": "https://myneta.info",
    },
    {
        "id": "candidate-symbol",
        "topic": "Candidate Information",
        "question": "How are election symbols allotted to candidates?",
        "answer": (
            "National parties have reserved symbols. Independent and "
            "unrecognised candidates choose from the ECI's free symbols list "
            "in order of nomination. The symbol cannot be transferred between "
            "elections."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "candidate-nomination",
        "topic": "Candidate Information",
        "question": "How does a candidate file nomination?",
        "answer": (
            "Nomination is filed in Form 2A/2B with the Returning Officer "
            "during the notification window. The candidate must submit the "
            "affidavit, security deposit, proposers and oath."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "candidate-criminal",
        "topic": "Candidate Information",
        "question": "Can a candidate with criminal cases contest elections?",
        "answer": (
            "Yes, until convicted. A candidate convicted and sentenced to two "
            "or more years of imprisonment is disqualified for the duration "
            "of the sentence plus six years under Section 8 of the "
            "Representation of the People Act, 1951."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "timeline-loksabha",
        "topic": "Election Timeline",
        "question": "When are Lok Sabha elections held?",
        "answer": (
            "Lok Sabha general elections are held every five years unless the "
            "House is dissolved earlier. The ECI announces the schedule, "
            "phases and dates approximately 4-6 weeks before polling begins."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "timeline-mcc",
        "topic": "Election Timeline",
        "question": "When does the Model Code of Conduct come into force?",
        "answer": (
            "The Model Code of Conduct (MCC) comes into force the moment the "
            "ECI announces the election schedule, and remains in force until "
            "the results are declared. It binds parties, candidates and the "
            "ruling government."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "timeline-counting",
        "topic": "Election Timeline",
        "question": "When are votes counted?",
        "answer": (
            "Votes are counted on the date announced by the ECI, which is the "
            "same across all constituencies in a multi-phase election. "
            "Counting begins at 8:00 AM with postal ballots, followed by EVM "
            "rounds."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "rules-mcc",
        "topic": "Rights & Rules",
        "question": "What is the Model Code of Conduct?",
        "answer": (
            "The MCC is a set of guidelines issued by the ECI that governs "
            "speeches, polling-day arrangements, manifestos, processions, and "
            "the use of government machinery during the election period."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "rules-rti",
        "topic": "Rights & Rules",
        "question": "Can I file an RTI to get election-related information?",
        "answer": (
            "Yes. The ECI is a public authority under the RTI Act, 2005. You "
            "can file an RTI request for non-confidential election records, "
            "subject to Section 8 exemptions related to security and personal "
            "information."
        ),
        "source": "Right to Information Act, 2005",
        "source_url": "https://rti.gov.in",
    },
    {
        "id": "rules-complaint",
        "topic": "Rights & Rules",
        "question": "How do I report an MCC violation?",
        "answer": (
            "Use the cVIGIL mobile app to upload time-stamped, geo-tagged "
            "evidence of MCC violations. Field officers respond within 100 "
            "minutes per ECI service-level commitments."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "rules-bribery",
        "topic": "Rights & Rules",
        "question": "Is offering money or gifts to voters illegal?",
        "answer": (
            "Yes. Section 171B of the Indian Penal Code criminalises bribery "
            "in elections. Both the giver and receiver are liable for "
            "imprisonment up to one year, a fine, or both."
        ),
        "source": "Indian Penal Code, Section 171B",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "results-counting",
        "topic": "Results",
        "question": "How are results declared?",
        "answer": (
            "Each round of counting is verified by the Returning Officer and "
            "uploaded to the ECI Suvidha portal. After all rounds, the "
            "winning candidate receives Form 21C/21D. Final results are "
            "published on results.eci.gov.in."
        ),
        "source": "Election Commission of India",
        "source_url": "https://results.eci.gov.in",
    },
    {
        "id": "results-margin",
        "topic": "Results",
        "question": "What is a recount and when can I request one?",
        "answer": (
            "Candidates may request a recount in writing to the Returning "
            "Officer if the margin is narrow or counting irregularities are "
            "suspected. The RO decides based on prima-facie merits before "
            "result declaration."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "results-petition",
        "topic": "Post-Vote",
        "question": "How can a candidate challenge results?",
        "answer": (
            "An election petition must be filed in the High Court within 45 "
            "days of the result under Section 81 of the Representation of "
            "the People Act, 1951. The Supreme Court hears appeals against "
            "the High Court's verdict."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "post-mp-engagement",
        "topic": "Post-Vote",
        "question": "How can I engage with my elected representative?",
        "answer": (
            "MPs and MLAs hold constituency office hours, accept letters via "
            "their parliamentary email, and most maintain verified social "
            "media handles. Their MP-LADS work and attendance are tracked on "
            "PRS India and PMINDIA portals."
        ),
        "source": "PRS Legislative Research",
        "source_url": "https://prsindia.org",
    },
    {
        "id": "post-attendance",
        "topic": "Post-Vote",
        "question": "Where can I check my MP's attendance and questions?",
        "answer": (
            "PRS Legislative Research and the official Sansad portal publish "
            "MP attendance, questions asked, and debates. State legislative "
            "assemblies maintain similar dashboards for MLAs."
        ),
        "source": "PRS Legislative Research",
        "source_url": "https://prsindia.org",
    },
    {
        "id": "general-types",
        "topic": "General",
        "question": "What types of elections are held in India?",
        "answer": (
            "India holds elections for the Lok Sabha, Rajya Sabha, State "
            "Legislative Assemblies (Vidhan Sabha) and Councils (Vidhan "
            "Parishad), Panchayats, Municipalities, and the offices of "
            "President and Vice-President."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-rajyasabha",
        "topic": "General",
        "question": "How are Rajya Sabha members elected?",
        "answer": (
            "Rajya Sabha members are elected indirectly by the elected "
            "members of State Legislative Assemblies via the Single "
            "Transferable Vote (STV) proportional representation system. "
            "Members serve six-year staggered terms."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-byelection",
        "topic": "General",
        "question": "What is a by-election?",
        "answer": (
            "A by-election is held to fill a vacancy in the Lok Sabha or a "
            "Legislative Assembly caused by death, resignation, "
            "disqualification, or expulsion. It must be conducted within six "
            "months of the vacancy under Section 151A."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-young-voter",
        "topic": "General",
        "question": "I will turn 18 next year. What should I do now?",
        "answer": (
            "You can apply in advance using Form 6 on NVSP up to three months "
            "before the qualifying date. Track the application via your "
            "reference ID and download your e-EPIC after approval."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "general-women-voter",
        "topic": "General",
        "question": "Are there special provisions for women voters?",
        "answer": (
            "Yes. Polling stations may have all-women teams ('Pink Booths'), "
            "priority queues for pregnant women, and the SVEEP programme "
            "actively encourages women's electoral participation across "
            "states."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-evm-tampering",
        "topic": "General",
        "question": "Are EVMs hackable or tamper-proof?",
        "answer": (
            "EVMs are stand-alone devices that are not connected to any "
            "network. Independent technical evaluations and judicial reviews "
            "have upheld their integrity. VVPAT slip auditing in randomly "
            "selected booths provides additional verification."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-svedp",
        "topic": "General",
        "question": "What is SVEEP?",
        "answer": (
            "Systematic Voters' Education and Electoral Participation is the "
            "ECI's voter awareness programme. It targets registration drives, "
            "first-time voters, women, urban apathy and persons with "
            "disabilities."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-cvigil",
        "topic": "General",
        "question": "What is the cVIGIL app?",
        "answer": (
            "cVIGIL is the ECI's citizen-vigilance mobile app. It accepts "
            "photo, video and audio evidence of MCC violations with auto "
            "geo-tagging. Field officers must respond within 100 minutes."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-electoral-bond",
        "topic": "General",
        "question": "What were electoral bonds?",
        "answer": (
            "Electoral bonds were a financial instrument for political party "
            "donations introduced in 2018. The Supreme Court struck down the "
            "scheme in February 2024 as unconstitutional and ordered "
            "disclosure of past purchases."
        ),
        "source": "Supreme Court of India",
        "source_url": "https://main.sci.gov.in",
    },
    {
        "id": "general-young-democracy",
        "topic": "General",
        "question": "Why is voting important for young Indians?",
        "answer": (
            "Voters aged 18-29 represent over a quarter of India's electorate. "
            "Their participation directly shapes economic, education and "
            "climate policy decisions, and signals political accountability "
            "across constituencies."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-firsttime-checklist",
        "topic": "General",
        "question": "What's the checklist for a first-time voter on polling day?",
        "answer": (
            "Carry your EPIC or accepted alternative ID, the voter slip from "
            "the BLO, water, sun protection, and confirm your booth number "
            "online. Avoid carrying mobile phones inside the polling "
            "compartment."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-eci-helpline",
        "topic": "General",
        "question": "Where can I get help on election day?",
        "answer": (
            "Call the ECI Voter Helpline at 1950 (prefix your STD code), use "
            "the Voter Helpline mobile app, or contact your Booth Level "
            "Officer (BLO) whose details are listed on the electoral roll."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-noform-found",
        "topic": "General",
        "question": "My name is missing from the voter list — what now?",
        "answer": (
            "Search electoralsearch.eci.gov.in by EPIC number or details. If "
            "still missing, file Form 6 immediately and contact your BLO. "
            "After the rolls are frozen for an election, you cannot vote in "
            "that election."
        ),
        "source": "Election Commission of India",
        "source_url": "https://electoralsearch.eci.gov.in",
    },
    {
        "id": "post-petition-window",
        "topic": "Post-Vote",
        "question": "How long after results can a petition be filed?",
        "answer": (
            "An election petition must be filed within 45 days of the date of "
            "election (declaration of result) under Section 81 of the "
            "Representation of the People Act, 1951."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "post-civic-action",
        "topic": "Post-Vote",
        "question": "How can citizens stay engaged between elections?",
        "answer": (
            "Track the legislative work of MPs/MLAs on PRS India and the "
            "Sansad portal, attend public consultations on government "
            "policies, file RTIs for transparency, and engage with civic-tech "
            "platforms like ADR and MyNeta."
        ),
        "source": "PRS Legislative Research",
        "source_url": "https://prsindia.org",
    },
    {
        "id": "general-edi-link",
        "topic": "General",
        "question": "What is the e-EPIC and how do I download it?",
        "answer": (
            "e-EPIC is the digital version of your voter ID card. Log in to "
            "the NVSP/Voter Helpline app, authenticate via OTP, and download "
            "the password-protected PDF, which is legally accepted as proof "
            "of ID."
        ),
        "source": "NVSP Portal",
        "source_url": "https://www.nvsp.in",
    },
    {
        "id": "rules-repoll",
        "topic": "Rights & Rules",
        "question": "When does the ECI order a re-poll?",
        "answer": (
            "The ECI may order a re-poll under Section 58A of the "
            "Representation of the People Act, 1951 if booth capturing, "
            "destruction of EVMs, natural calamity, or serious procedural "
            "irregularities are reported. The decision is taken before the "
            "counting date on the basis of observer reports."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "results-election-petition",
        "topic": "Results",
        "question": "What is an election petition and how does it work?",
        "answer": (
            "An election petition is a statutory remedy under Sections 80-100 "
            "of the Representation of the People Act, 1951 to challenge the "
            "result of a constituency. It is tried by the High Court and "
            "grounds include corrupt practices, non-compliance with the Act, "
            "or improper acceptance/rejection of nomination."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-delimitation",
        "topic": "General",
        "question": "What is the Delimitation Commission?",
        "answer": (
            "The Delimitation Commission is a constitutional body (Article 82) "
            "appointed after each census to redraw Lok Sabha and Assembly "
            "constituency boundaries to ensure roughly equal population per "
            "seat. Its orders have the force of law and are not justiciable."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-panchayat-municipal",
        "topic": "General",
        "question": "How are Panchayat and Municipal elections different from general elections?",
        "answer": (
            "Panchayat (73rd Amendment) and Municipal (74th Amendment) "
            "elections are conducted by State Election Commissions, not the "
            "ECI. They use paper ballots in many states, have reserved seats "
            "for SC/ST/OBC/women based on state rules, and follow state-"
            "specific electoral laws rather than the Representation of the "
            "People Act."
        ),
        "source": "Constitution of India, Articles 243K & 243ZA",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-expenditure-limit",
        "topic": "General",
        "question": "What is the election expenditure limit for candidates?",
        "answer": (
            "The ECI sets maximum expenditure limits per candidate per "
            "constituency. For Lok Sabha 2024, the limit was INR 95 lakh in "
            "larger states and INR 75 lakh in smaller states. Candidates must "
            "file a true account of expenses within 30 days of results."
        ),
        "source": "Election Commission of India",
        "source_url": "https://eci.gov.in",
    },
    {
        "id": "general-political-party-registration",
        "topic": "General",
        "question": "How is a political party registered in India?",
        "answer": (
            "A party applies to the ECI under Section 29A of the "
            "Representation of the People Act, 1951 with its constitution, "
            "rules, leadership list, and a 100-rupee application fee. "
            "Recognition as a state or national party requires winning a "
            "minimum number of seats or vote share in elections."
        ),
        "source": "Representation of the People Act, 1951",
        "source_url": "https://eci.gov.in",
    },
]

# BRIEFING TO THE MINISTER OF JUSTICE

**Portfolio:** Justice / Electoral

**Date:** January 2026

**Title:** Adoption of a Political Image Verification System for the 2026 General Election: Strengthening Public Trust in Political Communications

**Security Classification:** In Confidence

**Priority:** High

---

## PROPOSAL

1. This briefing seeks the Minister's agreement to support the adoption of a Political Image Verification System (PIVS) for the 2026 General Election, enabling registered political parties to authenticate campaign imagery and providing the public with a tool to verify whether political images are genuine.

2. Advances in generative AI mean that anyone — including foreign state actors, interest groups, or individuals — can now create realistic political imagery that falsely appears to originate from a New Zealand political party. This fundamentally threatens voters' ability to trust the political communications they encounter. The system provides a practical mechanism for parties to authenticate their genuine content and for voters to verify it.

---

## RELATION TO GOVERNMENT PRIORITIES

3. This proposal supports the Government's:

   - **National Security Strategy**, which identifies disinformation as a core national security issue and intelligence priority;
   - **commitment to election integrity**, reflected in Budget 2025 allocations of \$18.7 million for integrity improvements and $61.9 million for 2026 General Election delivery and modernisation;
   - **New Zealand's Strategy for Artificial Intelligence** (July 2025), which adopts a proportionate, risk-based approach to AI governance while leveraging existing mechanisms.

---

## EXECUTIVE SUMMARY

4. Advances in generative artificial intelligence now allow the rapid creation of realistic synthetic images, audio, and video. Globally, AI-generated political content has been used to mislead voters in elections in the United States, Romania, Slovakia, India, Taiwan, Canada, and the Netherlands. In Romania, the Constitutional Court annulled a presidential election in December 2024, in part due to coordinated AI-generated content and cyberattacks against electoral infrastructure.

5. New Zealand is not immune. Generative AI tools are freely available, and anyone can create convincing political imagery that falsely appears to originate from a New Zealand political party. Voters encountering such content have no way to verify whether it is genuine. The Electoral Commission does not regulate the content of election advertisements, and no verification infrastructure currently exists to help the public assess the authenticity of political imagery.

6. The Political Image Verification System provides a practical, technology-based safeguard. Political parties register campaign images through authenticated accounts. The system stores cryptographic and perceptual hashes of each image. Members of the public, media organisations, and platform operators can verify any political image against this registry. The system uses a privacy-first encrypted architecture and requires no personal information from users performing verification.

7. This briefing recommends that the Minister invite the Electoral Commission to evaluate the system for deployment ahead of the 2026 General Election, and that officials report back on funding and operational requirements.

---

## BACKGROUND

### AI-generated content and the erosion of public trust

8. Generative AI tools capable of producing photorealistic images, convincing audio deepfakes, and synthetic video are now widely accessible at low or no cost. Anyone — including foreign state actors, domestic interest groups, or individuals — can now create political imagery that convincingly appears to originate from a specific party. This fundamentally undermines voters' ability to trust the political communications they encounter.

9. Globally, more than 80 percent of countries with elections in 2024 experienced AI-generated content that eroded public trust in electoral processes. Key incidents demonstrating the impact on voter trust include:

   a. **United States (2024):** An AI-generated robocall mimicking President Biden's voice told New Hampshire voters not to vote. The perpetrator was fined USD $6 million and criminally indicted. Russian operatives created deepfake videos of Vice President Harris making fabricated statements. AI-generated images falsely depicted Black Americans supporting a candidate.

   b. **Romania (2024):** The Constitutional Court annulled the presidential first-round election results on 6 December 2024, the first European country to cancel a presidential election due to cyber and information warfare. Investigations uncovered over 85,000 cyberattacks against electoral IT infrastructure, coordinated AI content, bot networks, and troll farms. The far-right candidate's TikTok account accumulated 646,000 followers and 7.2 million likes with suspected artificial amplification.

   c. **Slovakia (2023):** An AI-generated audio recording fabricated a phone call between a journalist and an opposition leader, purportedly discussing election rigging. The opposition lost the subsequent election.

   d. **Canada (2025):** A deepfake video of Prime Minister Carney reached over one million views. Canada's election watchdog classified AI use as a "high" risk.

   e. **Taiwan (2024):** Microsoft identified China-based deepfake operations as the first confirmed use of AI-generated material by a nation-state to influence a foreign election.

### The "liar's dividend"

10. Academic researchers have identified a secondary threat to trust: the "liar's dividend." The mere existence of deepfake technology allows public figures to dismiss authentic evidence as AI-generated, evading accountability. Trust is eroded in both directions: voters cannot trust that content is genuine, and genuine content can be dismissed as fake. A verification system that can positively confirm the provenance of genuine political images helps restore trust in both directions.

### Public trust in New Zealand's electoral process

11. Public trust in electoral communications is a foundation of New Zealand's democracy. That trust is now at risk. The Department of the Prime Minister and Cabinet's national security surveys in 2022 and 2023 found that more than 80 percent of New Zealanders are concerned about the impacts of disinformation. Ipsos polling shows 63 percent of New Zealanders are nervous about AI, though only 35 percent understand where it is being used.

12. The risk to trust is straightforward: any person or entity can now create realistic political imagery that falsely appears to originate from a New Zealand political party. A fabricated campaign image, indistinguishable from a genuine one, could be circulated on social media and attributed to any party. Voters encountering this content have no way to verify whether it is genuine. This erodes confidence not only in the specific content but in political communications generally.

13. Cybersecurity experts have warned that the 2026 election will face serious challenges as bad actors leverage AI to increase the realism and volume of misinformation. Without a verification mechanism, voters are left to judge authenticity on their own — a task that is increasingly impossible as AI-generated content becomes more sophisticated.

### Absence of trust infrastructure

14. New Zealand currently has no mechanism for voters to verify whether political imagery is genuinely from the party it claims to represent. The key gaps are:

    a. The Electoral Commission has stated: "We do not regulate the content of election advertisements, so do not have a position on the use of AI in election ads." This means the body responsible for electoral integrity has no role in helping voters assess the authenticity of political imagery.

    b. No verification infrastructure exists. Promoter statements (section 204F, Electoral Act 1993) identify who is responsible for an advertisement, but do not verify that the visual content is genuinely from that party. A fabricated image can carry a real promoter statement.

    c. The DPMC-funded monitoring initiatives (Hate and Extremism Insights Aotearoa, Logically, the Disinformation Project) have ended, creating a monitoring gap ahead of the 2026 election.

    d. New Zealand's AI Strategy (July 2025) adopted a "light-touch" regulatory approach, placing responsibility on existing agencies and mechanisms. No new trust infrastructure was established.

15. Internationally, jurisdictions have recognised the threat to electoral trust and taken steps to protect the integrity of political communications:

    a. **South Korea** amended the Public Official Election Act to ban election-related deepfakes within 90 days of election day, recognising that fabricated content destroys voter trust.

    b. **Singapore** passed the Elections (Integrity of Online Advertising) Amendment Bill, protecting voters from digitally generated content that could mislead them about candidates' positions.

    c. **The European Union** classified AI systems used for influencing elections as high-risk under the AI Act (fully enforceable from August 2026), requiring transparency measures to maintain public trust.

    d. In the **United States**, 28 states have enacted laws addressing deepfakes in political communications, driven by concern for voter trust and electoral integrity.

---

## ANALYSIS

### The proposed system

16. The Political Image Verification System (PIVS) is an open-source, privacy-first platform that allows political parties to register authentic campaign imagery and enables the public to verify that imagery. The system consists of three components:

    a. **Party submission portal:** Authorised party representatives submit campaign images through authenticated accounts with multi-factor authentication. The system computes cryptographic and perceptual hashes of each image before encrypting and storing it.

    b. **Public verification portal:** Any member of the public can upload a political image or scan a QR code to check whether it has been registered by a political party. No personal information or account is required.

    c. **Verification API:** Media organisations and platform operators can integrate verification into their own systems through a documented programming interface.

### How verification works

17. The system uses a dual-hashing approach to handle the practical reality that political images are modified as they circulate:

    a. **Cryptographic hash (SHA-256):** Provides exact-match verification for unmodified original images. This is fast and deterministic.

    b. **Perceptual hash (PDQ, developed by Meta):** Provides fuzzy matching that tolerates visual modifications commonly introduced by social media platforms, including JPEG recompression, resizing, minor cropping, screenshot capture, and the addition of verification badges or QR codes. PDQ uses a 256-bit hash with a Hamming distance threshold; images scoring within this threshold are identified as matching. pHash provides a secondary fallback algorithm.

18. This dual approach means that an image originally registered by a party will still be verified even after it has been shared on Facebook, screenshotted, or printed on a hoarding with a QR verification code added.

### Privacy and security

19. The system is designed with a privacy-first architecture:

    a. All stored images are encrypted with AES-256-GCM using envelope encryption, where each image has a unique data encryption key.

    b. The public verification process exposes only hash comparisons, never the stored images themselves.

    c. Verification is anonymous. No login, personal information, or tracking is required.

    d. IP addresses are hashed in system logs and cannot be reversed.

    e. Party user personal information (email addresses) is encrypted at rest.

    f. The system is designed to comply with the Privacy Act 2020, notwithstanding the political party exemption.

### Verification badges and QR codes

20. When a party registers an image, the system generates:

    a. A small verification badge (under 5 percent of image area) that can be overlaid on the image. The badge is deliberately sized to remain within the perceptual hash tolerance so that badged images still verify against the original.

    b. A QR code encoding a verification URL. This is particularly useful for physical media such as hoardings and billboards, enabling voters to scan and verify on their mobile device.

    c. A unique verification ID and URL for each registered image.

### Promoter statement management

21. The system includes integrated support for Electoral Act promoter statements (section 204F). Each party account can store a promoter statement, and the system provides tools to:

    a. **Add promoter statements to images:** Authorised party users can overlay their party's promoter statement onto campaign images during registration. The overlay uses contrast-aware text placement (meeting WCAG 2.1 AA legibility standards with a minimum 4.5:1 contrast ratio) and configurable corner positioning, with automatic adjustment for portrait and landscape orientations.

    b. **Verify promoter statements using OCR:** The system can scan submitted images using optical character recognition to check whether a promoter statement is already present and whether it matches the party's registered statement, using fuzzy text matching to account for OCR imprecision.

    c. **Batch processing:** Party users can add promoter statements to images in batch mode (upload and download directly) or via email, without registering images as verified assets. This supports high-volume campaign workflows.

    d. **Email interface:** Images can be submitted as email attachments to a processing address. Anti-spoofing verification ensures that images are processed only after the registered user confirms the submission via a verification email sent to their authenticated address.

### Complementary role to existing regulation

22. PIVS does not replace regulatory oversight. It complements existing requirements under the Electoral Act 1993:

    a. The promoter statement requirement (section 204F) establishes who is responsible for an advertisement. PIVS establishes whether the visual content of that advertisement is genuinely from the claimed party, and now directly assists parties in meeting the promoter statement requirement by providing tools to add legible, contrast-aware promoter statements to campaign imagery.

    b. The Advertising Standards Authority's fast-track complaints process addresses misleading content after the fact. PIVS provides proactive, real-time verification before complaints are made.

    c. The Electoral Commission's voter education programme can direct the public to the verification tool as a practical action they can take when they encounter political imagery.

### Risks and mitigations

22. The following risks have been identified:

| Risk | Mitigation |
|---|---|
| Low party adoption reduces usefulness | Early engagement with major parties; simple onboarding process; system pre-seeded with seven registered NZ parties |
| False positive matches (incorrect verification) | Multiple hash algorithms with configurable thresholds; confidence scoring; human review pathway |
| System targeted by cyberattack | Rate limiting; web application firewall; encrypted storage; security audit before launch; nginx reverse proxy with rate limiting zones |
| Election-day traffic spike overwhelms system | CDN deployment; auto-scaling infrastructure; load testing before election |
| Public confusion about what verification means | Clear user interface messaging; verification means "registered by a party" not "factually accurate" |
| Adversarial image manipulation to evade detection | PDQ is resistant to common transforms; multiple hash algorithms reduce evasion; DINOv2-based hashing available for future enhancement |

---

## POPULATION IMPLICATIONS

23. The system is designed to benefit all New Zealanders who engage with political advertising. Specific population implications include:

    a. **Maori:** AI models trained on Western data present specific risks of culturally offensive or stereotyping content in political contexts. Fabricated imagery purporting to represent Maori positions or interests could be created by any actor and circulated without accountability. The verification system helps Maori communities confirm whether political imagery purporting to represent Maori interests is genuinely from the claimed party.

    b. **Pacific peoples:** Similar risks of AI-generated stereotyping apply. Verification provides a practical tool for Pacific communities to check political imagery targeting them.

    c. **Older New Zealanders:** Research indicates lower digital literacy among older populations, making them more susceptible to AI-generated misinformation. The QR code system on physical media (hoardings, printed material) provides an accessible verification method.

    d. **Rural communities:** Political advertising on physical media (hoardings, billboards) is prevalent in rural areas. QR code verification is particularly relevant for these communities.

    e. **Disabled people:** The web portal will be designed to meet WCAG 2.1 AA accessibility standards.

---

## HUMAN RIGHTS

24. The proposal is consistent with the New Zealand Bill of Rights Act 1990 and the Human Rights Act 1993. The system:

    a. does not restrict the publication of any content (section 14, freedom of expression);

    b. is voluntary for political parties to adopt;

    c. does not collect or process personal information from members of the public performing verification;

    d. supports informed participation in elections by enabling voters to assess the authenticity of political communications (section 12, right to vote).

---

## FINANCIAL IMPLICATIONS

25. The system is built on open-source technology and can be hosted on government cloud infrastructure. The system has been fully developed; the project team is open to discussing arrangements for intellectual property transfer and/or technical support during the campaign period. The costs below relate to the operational hosting and deployment requirements.

26. **Recommended hosting platform:** Catalyst Cloud, the only All-of-Government Cloud Framework provider with 100% New Zealand-based infrastructure (ISO 27001 and ISO 27017 certified, PCI DSS compliant). Government agencies receive aggregated volume discounts under the framework. Hosting on Catalyst Cloud guarantees data sovereignty under New Zealand law. The cost estimates below are based on Catalyst Cloud's published pricing (effective 1 June 2025, NZD exclusive of GST).

27. **Estimated image volumes:** Based on 2023 General Election data — in which the six main parties ran approximately 9,000 paid Facebook advertisements and produced thousands of physical hoardings, flyers, and social media graphics (Victoria University of Wellington; RNZ; Electoral Commission 2023 Party Expenses Returns) — the system would store an estimated 2,000–5,000 unique registered images across all participating parties. Each image generates up to four encrypted variants (original, badge, QR code, promoter-stamped), totalling approximately 60 GB of encrypted object storage at the upper estimate.

28. Indicative cost estimates for hosting and deployment are:

    a. **Infrastructure hosting:** $1,000–$2,500 per month on Catalyst Cloud, comprising: application compute for the verification API, hash computation, OCR processing, and image overlay (2–3 Catalyst Cloud C1 instances from $95–$190/month each); managed PostgreSQL database ($180–$360/month); geo-replicated encrypted object storage for registered images at $0.10/GiB/month (~$6/month for 60 GB); network, load balancing, and bandwidth ($75–$150/month); and a 15% operational overhead contingency for monitoring, backups, SSL/TLS, and traffic scaling. The primary cost driver is compute, not storage — image storage at New Zealand election volumes is under $10/month on Catalyst Cloud.

    b. **Security audit:** A pre-launch penetration test and independent security audit, estimated at $30,000–$50,000.

    c. **Testing:** Acceptance testing, integration testing, load testing, and WCAG 2.1 AA accessibility audit, estimated at $20,000–$40,000. *

    d. **Privacy Impact Assessment:** Required under the Privacy Act 2020. A draft PIA is provided with the system. Estimated at $0–$5,000 if reviewed or completed in-house. *

    e. **Total estimated operational cost for the 2026 election cycle:** $58,000–$110,000 (including 8 months of Catalyst Cloud hosting at $8,000–$20,000), well within the Budget 2025 integrity improvement allocation of $18.7 million.

    \* Items marked with an asterisk could be conducted in-house by Commission or Ministry staff with existing capabilities, reducing costs to staff time only. The privacy impact assessment, acceptance testing, load testing, and accessibility audit do not require external contractors if qualified personnel are available.

29. These costs are modest compared to the potential cost of an electoral integrity incident. Romania's annulled election required a full re-run at significant public expense and lasting damage to democratic legitimacy.

---

## LEGISLATIVE IMPLICATIONS

27. No legislation is required to deploy the system. The system operates within existing regulatory settings as a voluntary verification tool. However, the Minister may wish to note that:

    a. Future legislative consideration could make registration of political advertising images mandatory rather than voluntary, providing stronger assurance to the public.

    b. The Independent Electoral Review recommended expanding the undue influence offence and considering microtargeting regulations. A verification system would complement any such future legislative changes.

---

## CONSULTATION

28. The following agencies have interests relevant to this proposal:

    - **Electoral Commission:** As the body responsible for election administration and voter education.
    - **Department of the Prime Minister and Cabinet:** As the lead agency for national security and disinformation resilience.
    - **Government Communications Security Bureau:** For cybersecurity review of the system.
    - **Ministry of Justice:** As the policy agency for electoral law.
    - **Office of the Privacy Commissioner:** To confirm the privacy-by-design approach meets best practice.
    - **Department of Internal Affairs:** As the lead for the Government's digital strategy and AI framework.

29. Engagement with registered political parties would be required before deployment to ensure uptake.

---

## COMMUNICATIONS

30. If the Minister agrees to progress this proposal, officials recommend:

    a. An announcement framed around election integrity and public trust, referencing the Government's existing investments in election modernisation.

    b. Engagement with major media organisations to encourage integration of the verification tool.

    c. Inclusion in the Electoral Commission's 2026 voter education programme.

    d. A public-facing website with clear, plain-language guidance on how to use the verification system.

---

## PROACTIVE RELEASE

31. The Minister is advised to proactively release this briefing, with any redactions necessary to protect security-sensitive technical details, within 30 business days of decisions being confirmed.

---

## RECOMMENDATIONS

The Minister of Justice is recommended to:

**Context**

32. **note** that advances in generative AI now allow the rapid creation of realistic synthetic political images, audio, and video at low cost and with minimal technical skill;

33. **note** that AI-generated political content has been used to mislead voters in elections in the United States, Romania, Slovakia, India, Taiwan, Canada, and the Netherlands, and that Romania annulled a presidential election in December 2024 due in part to AI-enabled interference;

34. **note** that no mechanism currently exists for voters to verify whether political imagery is genuinely from the party it claims to represent, and that anyone can now create convincing fake political content at minimal cost;

35. **note** that the absence of verification infrastructure poses a direct risk to public trust in electoral communications, and that the Electoral Amendment Act 2025 did not address this gap;

36. **note** that New Zealand's National Security Strategy identifies disinformation as a core national security issue, and that DPMC surveys show more than 80 percent of New Zealanders are concerned about the impacts of disinformation;

37. **note** that Budget 2025 allocated $18.7 million over four years for election integrity improvements and $61.9 million for 2026 General Election delivery and modernisation;

**Decisions**

38. **agree** that a practical, technology-based safeguard for verifying the authenticity of political campaign imagery is necessary to protect electoral integrity for the 2026 General Election;

39. **agree** that the Political Image Verification System, which enables parties to register authentic campaign images and the public to verify them using cryptographic and perceptual hashing with a privacy-first encrypted architecture, is a suitable solution;

40. **agree** that the system should be deployed as a voluntary tool available to all registered political parties ahead of the 2026 General Election;

**Next steps**

41. **invite** the Minister of Justice to direct officials to engage with the Electoral Commission on operational requirements for deploying the Political Image Verification System for the 2026 General Election;

42. **invite** the Minister of Justice to direct officials to consult with the Government Communications Security Bureau on a security review of the system before deployment;

43. **invite** the Minister of Justice to direct officials to engage with registered political parties on voluntary adoption of the system;

44. **invite** the Minister of Justice to direct officials to report back to the Minister by April 2026 on funding requirements, operational readiness, and a proposed deployment timeline.

---

**Prepared by:** Political Image Verification Project Team

**Approved by:** [Senior Official Name and Title]

---

## APPENDIX A: Technical Summary of the Political Image Verification System

### System Architecture

The system comprises a FastAPI (Python) backend with PostgreSQL database, a Next.js web frontend, and containerised deployment via Docker. The architecture follows a three-tier model:

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js (React) | Public verification portal and party submission portal |
| API | FastAPI (Python) | RESTful API with OpenAPI documentation |
| Data | PostgreSQL + encrypted file storage | Party registry, hash index, encrypted image storage |

### Hashing Approach

| Method | Purpose | Detail |
|---|---|---|
| SHA-256 | Exact match | 256-bit cryptographic hash; detects unmodified originals |
| PDQ (Meta) | Perceptual match | 256-bit perceptual hash; tolerates compression, resizing, badge overlays; Hamming distance threshold of 31 or fewer differing bits for a confident match |
| pHash | Fallback match | 64-bit perceptual hash; secondary matching algorithm |

### Encryption

- **Envelope encryption:** Each image encrypted with a unique AES-256-GCM data encryption key (DEK), which is itself encrypted by a key encryption key (KEK).
- **PII encryption:** Party user email addresses and contact details encrypted at rest.
- **Transport:** TLS for all connections.

### Authentication

- JWT-based authentication for party users.
- TOTP multi-factor authentication mandatory for party administrators.
- Role-based access control (admin, submitter, viewer).

### API Endpoints

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/v1/verify/image` | None | Upload image for verification |
| `POST /api/v1/verify/hash` | None | Verify by pre-computed hash |
| `GET /api/v1/verify/{id}` | None | QR code / verification ID lookup |
| `GET /api/v1/parties` | None | List registered parties |
| `POST /api/v1/assets` | Party | Submit image for registration (with optional promoter statement overlay and OCR check) |
| `POST /api/v1/assets/add-promoter` | Party | Add promoter statement to image and return (batch mode) |
| `GET /api/v1/assets` | Party | List registered assets |
| `PUT /api/v1/parties/{id}/promoter-statement` | Admin | Set or update party promoter statement |
| `POST /api/v1/email/verify/{job_id}` | Token | Confirm an email-submitted processing job |

### Production Deployment

The system is containerised with Docker Compose and includes:

- Gunicorn application server with Uvicorn workers
- Nginx reverse proxy with rate limiting (30 verifications/minute, 10 submissions/minute)
- Security headers (X-Frame-Options, Content-Security-Policy, X-Content-Type-Options)
- TLS termination at the reverse proxy
- PostgreSQL with encrypted connections

### Pre-seeded Parties

The system is pre-configured with New Zealand's seven registered parliamentary parties:

1. New Zealand Labour Party
2. New Zealand National Party
3. Green Party of Aotearoa New Zealand
4. ACT New Zealand
5. New Zealand First
6. Te Pati Maori
7. The Opportunities Party (TOP)

---

## APPENDIX B: International Comparisons

| Jurisdiction | Measures to Protect Electoral Trust | Status |
|---|---|---|
| **South Korea** | Ban on election deepfakes within 90 days of polling; up to 7 years' imprisonment | In force (2023) |
| **Singapore** | Prohibition on digitally generated content depicting candidates during elections | In force (2024) |
| **European Union** | AI Act classifies election-influencing AI as high-risk; Digital Services Act requires platforms to label manipulated content | Full enforcement August 2026 |
| **United States** | No federal legislation; 28 states have enacted laws; FCC fines for AI robocalls | Patchwork |
| **Australia** | No binding AI-specific laws; AEC acknowledges it cannot combat AI misinformation; "Stop and Consider" campaign only | Voluntary |
| **Canada** | No AI-specific election legislation; election watchdog rates AI as "high" risk | Gap |
| **New Zealand** | No verification infrastructure; Electoral Commission does not regulate ad content; no trust mechanisms | **Significant gap** |

---

## APPENDIX C: Key Statistics

| Statistic | Source |
|---|---|
| 80%+ of countries with elections in 2024 experienced AI-related electoral incidents | Harvard Ash Center |
| 63% of New Zealanders are nervous about AI | Ipsos |
| 80%+ of New Zealanders are concerned about disinformation impacts | DPMC National Security Survey |
| 550% increase in known deepfake videos globally since 2019 | Deepstrike |
| 57% of Americans are worried about AI generating false political content | Pew Research Center |
| 97% of Americans agree AI should be subject to safety rules | Gallup/SCSP |
| 87% of voters support AI disclosure requirements for political ads | Public Citizen |
| Up to 8 million deepfake videos projected on social media by 2025 | Industry projections |
| $18.7 million allocated in Budget 2025 for election integrity improvements | NZ Budget 2025 |
| $61.9 million allocated for 2026 election delivery and modernisation | NZ Budget 2025 |

---

## REFERENCES

1. Department of the Prime Minister and Cabinet. *Strengthening resilience to disinformation in Aotearoa New Zealand.* https://www.dpmc.govt.nz/our-programmes/national-security/strengthening-resilience-disinformation

2. Electoral Commission of New Zealand. *Ensuring election integrity for 2026 and the future.* https://elections.nz/media-and-news/2025/ensuring-election-integrity-for-2026-and-the-future/

3. Electoral Commission of New Zealand. *About election advertising.* https://elections.nz/guidance-and-rules/advertising-and-campaigning/about-election-advertising/

4. Ministry of Justice. *Electoral law changes.* https://www.justice.govt.nz/about/news-and-media/news/electoral-law-changes/

5. Ministry of Business, Innovation and Employment. *New Zealand's Strategy for Artificial Intelligence: Investing with confidence.* July 2025.

6. DPMC Multi-Stakeholder Group. *Strengthening civil society resilience to mis- and disinformation in Aotearoa New Zealand.* March 2024.

7. Ministry of Justice. *Independent Electoral Review: Final Report.* November 2023.

8. International Foundation for Electoral Systems. *The Romanian 2024 Election Annulment.* https://www.ifes.org/publications/romanian-2024-election-annulment-addressing-emerging-threats-electoral-integrity

9. NPR. *How deepfakes and AI memes affected global elections in 2024.* December 2024.

10. Centre for Governance Innovation. *Then and Now: AI Electoral Interference in 2025.* https://www.cigionline.org/articles/then-and-now-how-does-ai-electoral-interference-compare-in-2025/

11. Harvard Ash Center. *The Apocalypse That Wasn't: AI in 2024 Elections.* https://ash.harvard.edu/articles/the-apocalypse-that-wasnt/

12. University of Waikato. *Playing politics with AI: Why NZ needs rules on the use of fake images in election campaigns.* https://www.waikato.ac.nz/news-events/news/playing-politics-with-ai/

13. Pew Research Center. *Views of AI Around the World.* October 2025.

14. Elections NZ. *2026 General Election.* https://elections.nz/about/about-the-electoral-commission/our-work/2026-general-election/

15. Advertising Standards Authority. *Spotlight on General Election Advertising.* https://asa.co.nz/2023/08/09/spotlight-on-general-election-advertising/

16. Broadcasting Standards Authority. *Election Programmes Code.* https://www.bsa.govt.nz/broadcasting-standards/election-code/

17. Carnegie Endowment for International Peace. *Can Democracy Survive the Disruptive Power of AI?* December 2024.

18. Brennan Center for Justice. *Gauging the AI Threat to Free and Fair Elections.* March 2025.

19. Catalyst Cloud. *Price List.* https://catalystcloud.nz/pricing/price-list/ (Prices effective 1 June 2025.)

20. Catalyst Cloud. *All-of-Government Cloud Framework Agreement.* https://catalystcloud.nz/customers/public-sector1/

21. New Zealand Government Procurement. *Catalyst Cloud Framework Agreement.* https://www.procurement.govt.nz/contracts/catalyst-cloud-framework-agreement/

22. Krewel, M. (Victoria University of Wellington). *Five weeks, 4,000 Facebook posts: social media campaigning in the 2023 election.* November 2023. https://www.wgtn.ac.nz/news/2023/11/five-weeks-4-000-facebook-posts-social-media-campaigning-in-the-2023-election

23. RNZ. *The campaign for social media supremacy in Election 2023.* October 2023. https://www.rnz.co.nz/news/political/500672/the-campaign-for-social-media-supremacy-in-election-2023-who-the-parties-targeted-and-their-key-messages

24. Electoral Commission of New Zealand. *2023 General Election Party Expenses.* https://elections.nz/democracy-in-nz/historical-events/2023-general-election/party-expenses/

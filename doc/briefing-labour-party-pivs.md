# BRIEFING TO THE NEW ZEALAND LABOUR PARTY

**From:** Political Image Verification Project Team

**Date:** February 2026

**Title:** The Political Image Verification System: Protecting Public Trust in Political Communications for the 2026 General Election

**Classification:** Party Confidential

**Priority:** High

---

## PURPOSE

1. This briefing provides the New Zealand Labour Party with information on the Political Image Verification System (PIVS), a practical tool that enables political parties to authenticate their campaign imagery and provides the public with a mechanism to verify whether political images are genuine.

2. The system addresses a direct and growing threat to public trust: advances in generative AI mean that anyone — including foreign state actors, opposition-aligned interest groups, or individuals — can now create realistic political imagery that falsely appears to originate from the Labour Party. Without a verification mechanism, voters have no way to distinguish genuine Labour communications from fabrications. The system gives the Party a tool to protect its brand, its message, and voters' trust.

---

## THE TRUST PROBLEM

### AI-generated content erodes trust in political communications

3. Generative AI tools capable of producing photorealistic images, convincing audio deepfakes, and synthetic video are now widely accessible at low or no cost. Anyone can now create political imagery that convincingly appears to originate from the Labour Party — campaign posters, social media graphics, candidate statements — and circulate it online. Voters encountering this content have no way to verify whether it is genuine.

4. This is not a hypothetical risk. Globally, more than 80 percent of countries with elections in 2024 experienced AI-generated content that eroded public trust in electoral processes:

   a. **United States (2024):** An AI-generated robocall mimicking President Biden's voice told New Hampshire voters not to vote. The perpetrator was fined USD $6 million and criminally indicted. Russian operatives created deepfake videos of Vice President Harris making fabricated statements. AI-generated images falsely depicted Black Americans supporting a candidate.

   b. **Romania (2024):** The Constitutional Court annulled the presidential first-round election results on 6 December 2024 — the first European country to cancel a presidential election due to cyber and information warfare. Investigations uncovered over 85,000 cyberattacks against electoral IT infrastructure, coordinated AI content, bot networks, and troll farms.

   c. **Slovakia (2023):** An AI-generated audio recording fabricated a phone call between a journalist and an opposition leader, purportedly discussing election rigging. The content was released days before the election. The opposition lost.

   d. **Canada (2025):** A deepfake video of Prime Minister Carney reached over one million views. Canada's election watchdog classified AI use as a "high" risk to electoral integrity.

   e. **Taiwan (2024):** Microsoft identified China-based deepfake operations as the first confirmed use of AI-generated material by a nation-state to influence a foreign election.

### The "liar's dividend"

5. Academic researchers have identified a secondary threat to trust: the "liar's dividend." The mere existence of deepfake technology allows political figures to dismiss authentic evidence as AI-generated, evading accountability. Trust is eroded in both directions: voters cannot trust that content is genuine, and genuine content can be dismissed as fake. A verification system that can positively confirm the provenance of genuine political images helps restore trust in both directions.

### AI has already been used without disclosure in New Zealand elections

6. AI-generated content has already been used in New Zealand political campaigning without disclosure. During the 2023 General Election:

    a. The **National Party** used AI in attack advertisements. When questioned, the party did not commit to disclosing AI use in future campaigns.

    b. The **ACT Party** published AI-generated social media posts, including an AI-generated image of a Maori couple sourced from Adobe's stock collection, which was criticised for lack of transparency and cultural insensitivity.

    c. Neither party disclosed the use of AI to the public.

7. These incidents demonstrate that AI-generated political content is already present in New Zealand's electoral environment. The concern is not limited to parties' own use of AI — the greater risk is that external actors can fabricate content that appears to come from any party. A fabricated Labour Party campaign image, indistinguishable from a genuine one, could be circulated on social media and attributed to the Party without its knowledge or consent.

### New Zealanders are concerned

8. The Department of the Prime Minister and Cabinet's national security surveys in 2022 and 2023 found that more than 80 percent of New Zealanders are concerned about the impacts of disinformation. Ipsos polling shows 63 percent of New Zealanders are nervous about AI, though only 35 percent understand where it is being used.

9. Cybersecurity experts have warned that the 2026 election will face serious challenges as bad actors leverage AI to increase the realism and volume of misinformation. Without a verification mechanism, voters are left to judge authenticity on their own — a task that is increasingly impossible as AI-generated content becomes more sophisticated.

### No trust infrastructure exists

10. New Zealand currently has no mechanism for voters to verify whether political imagery is genuinely from the party it claims to represent:

    a. The Electoral Commission has stated: "We do not regulate the content of election advertisements, so do not have a position on the use of AI in election ads." The body responsible for electoral integrity has no role in helping voters assess the authenticity of political imagery.

    b. No verification infrastructure exists. Promoter statements (section 204F, Electoral Act 1993) identify who is responsible for an advertisement, but do not verify that the visual content is genuinely from that party. A fabricated image can carry a real promoter statement.

    c. The DPMC-funded monitoring initiatives (Hate and Extremism Insights Aotearoa, Logically, the Disinformation Project) have ended, creating a monitoring gap ahead of the 2026 election.

    d. New Zealand's AI Strategy (July 2025) adopted a "light-touch" regulatory approach. No new trust infrastructure was established.

    e. The Electoral Amendment Act 2025 did not introduce AI-specific provisions or verification mechanisms.

---

## THE SOLUTION

### What the system does

11. The Political Image Verification System (PIVS) is an open-source, privacy-first platform that gives the Labour Party two capabilities:

    a. **Authenticate your content:** Authorised Labour Party representatives submit campaign images through authenticated accounts with multi-factor authentication. The system computes cryptographic and perceptual hashes of each image before encrypting and storing it. This creates a verifiable registry of genuine Labour Party imagery.

    b. **Enable voters to verify:** Any member of the public can upload a political image or scan a QR code to check whether it has been registered by the Labour Party (or any other participating party). No personal information or account is required.

    c. **Media and platform integration:** Media organisations and platform operators can integrate verification into their own systems through a documented API, enabling automated verification at scale.

### How verification works

12. The system uses a dual-hashing approach to handle the practical reality that political images are modified as they circulate:

    a. **Cryptographic hash (SHA-256):** Provides exact-match verification for unmodified original images. This is fast and deterministic.

    b. **Perceptual hash (PDQ, developed by Meta):** Provides fuzzy matching that tolerates visual modifications commonly introduced by social media platforms, including JPEG recompression, resizing, minor cropping, screenshot capture, and the addition of verification badges or QR codes. pHash provides a secondary fallback algorithm.

13. This dual approach means that an image originally registered by the Labour Party will still be verified even after it has been shared on Facebook, screenshotted, compressed, or printed on a hoarding with a QR verification code added.

### Verification badges and QR codes

14. When the Party registers an image, the system generates:

    a. A small verification badge (under 5 percent of image area) that can be overlaid on the image. The badge is deliberately sized to remain within the perceptual hash tolerance so that badged images still verify against the original.

    b. A QR code encoding a verification URL. This is particularly useful for physical media such as hoardings and billboards, enabling voters to scan and verify on their mobile device.

    c. A unique verification ID and URL for each registered image.

### Promoter statement tools

15. The system includes integrated support for Electoral Act promoter statements (section 204F), reducing the administrative burden of compliance:

    a. **Add promoter statements to images:** Authorised Party users can overlay the Party's promoter statement onto campaign images during registration. The overlay uses contrast-aware text placement (meeting WCAG 2.1 AA legibility standards) and configurable corner positioning, with automatic adjustment for portrait and landscape orientations. This ensures that promoter statements are consistently legible regardless of the image content.

    b. **OCR verification:** The system can scan images using optical character recognition to check whether a promoter statement is already present and matches the Party's registered statement. This is useful for checking compliance on existing campaign materials.

    c. **Batch processing:** Party users can add promoter statements to images in batch mode — upload, stamp, and download — without registering images as verified assets. This supports high-volume campaign workflows where many images need to be stamped quickly.

    d. **Email interface:** Images can be submitted as email attachments to a dedicated processing address, with anti-spoofing verification to prevent unauthorised submissions. The processed image with promoter statement is returned via email. This provides a low-friction workflow for campaign staff who may not be regular users of the web portal.

### Privacy and security

15. The system is designed with a privacy-first architecture:

    a. All stored images are encrypted with AES-256-GCM using envelope encryption, where each image has a unique data encryption key.

    b. The public verification process exposes only hash comparisons, never the stored images themselves.

    c. Verification is anonymous. No login, personal information, or tracking is required.

    d. IP addresses are hashed in system logs and cannot be reversed.

    e. Party user personal information (email addresses) is encrypted at rest.

    f. The system is designed to comply with the Privacy Act 2020.

---

## STRATEGIC VALUE FOR THE LABOUR PARTY

### Protecting the Party's brand

16. The Labour Party's campaign imagery is a core asset. Without verification, any actor can create and circulate fabricated imagery that:

    a. attributes false policy positions to the Party;

    b. depicts candidates in fabricated scenarios;

    c. creates culturally offensive or divisive content under the Party's name;

    d. mimics the Party's visual identity to spread misinformation.

17. The verification system gives the Party a mechanism to say definitively: "This is ours" or "This is not ours." This is a brand protection tool as much as an electoral integrity tool.

### Demonstrating leadership on trust

18. The Labour Party has an opportunity to demonstrate leadership on electoral trust by being an early adopter of the verification system. Early adoption:

    a. signals the Party's commitment to transparency and authentic political communication;

    b. positions the Party as proactive on a concern shared by more than 80 percent of New Zealanders;

    c. provides a public contrast with parties that have used AI without disclosure;

    d. creates a practical benefit for voters: Labour imagery can be verified, building trust in the Party's communications.

### Holding opponents to account

19. The verification system creates a new standard of transparency. If the Labour Party registers its imagery and other parties do not, the public and media can ask why. This is particularly relevant given that:

    a. The National Party used AI in attack advertisements during the 2023 election without disclosure and did not commit to disclosing AI use in future campaigns.

    b. The ACT Party published AI-generated social media posts without disclosure, including culturally insensitive AI-generated imagery.

    c. Neither party has indicated willingness to adopt transparency measures for AI-generated content.

20. By adopting the verification system, the Labour Party establishes the standard and creates implicit pressure for other parties to follow — or to explain why they will not.

---

## WHAT ADOPTION INVOLVES

### Onboarding

21. The system is pre-seeded with accounts for all seven registered parliamentary parties. Onboarding for the Labour Party involves:

    a. Designating authorised users (administrators and submitters) within the Party.

    b. Setting up multi-factor authentication for each authorised user.

    c. Familiarisation with the submission portal (web-based, no software installation required).

22. The Party retains full control over which images are registered. There is no obligation to register all campaign imagery — the Party can choose which images to authenticate.

### Ongoing use

23. During the campaign period, authorised Party users would:

    a. Upload campaign images through the submission portal before or at the time of publication.

    b. Optionally add the Party's promoter statement to images during registration, or use the batch mode to stamp multiple images with the promoter statement for download.

    c. Optionally apply verification badges or QR codes to published imagery.

    d. Direct voters and media to the verification portal when the authenticity of Labour imagery is questioned.

### Cost

24. There is no cost to political parties for using the system. The system is funded through the Electoral Commission (or hosting agency). The Party's only investment is staff time for onboarding and image submission.

---

## POPULATION IMPLICATIONS

25. The system is designed to benefit all New Zealanders who engage with political advertising. Specific implications relevant to Labour's constituencies include:

    a. **Maori:** AI models trained on Western data present specific risks of culturally offensive or stereotyping content in political contexts. Fabricated imagery purporting to represent Maori positions or interests could be created by any actor and circulated without accountability — as demonstrated by the ACT Party's AI-generated image of a Maori couple in 2023. The verification system helps Maori communities confirm whether political imagery purporting to represent Maori interests is genuinely from the claimed party.

    b. **Pacific peoples:** Similar risks of AI-generated stereotyping apply. Verification provides a practical tool for Pacific communities to check political imagery targeting them.

    c. **Older New Zealanders:** Research indicates lower digital literacy among older populations, making them more susceptible to AI-generated misinformation. The QR code system on physical media (hoardings, printed material) provides an accessible verification method.

    d. **Rural communities:** Political advertising on physical media (hoardings, billboards) is prevalent in rural areas. QR code verification is particularly relevant for these communities.

    e. **Disabled people:** The web portal is designed to meet WCAG 2.1 AA accessibility standards.

---

## INTERNATIONAL CONTEXT

26. Internationally, jurisdictions have recognised the threat to electoral trust and taken steps to protect the integrity of political communications:

| Jurisdiction | Measures to Protect Electoral Trust | Status |
|---|---|---|
| **South Korea** | Ban on election deepfakes within 90 days of polling; up to 7 years' imprisonment | In force (2023) |
| **Singapore** | Prohibition on digitally generated content depicting candidates during elections | In force (2024) |
| **European Union** | AI Act classifies election-influencing AI as high-risk; transparency requirements | Full enforcement August 2026 |
| **United States** | No federal legislation; 28 states have enacted laws; FCC fines for AI robocalls | Patchwork |
| **Australia** | No binding AI-specific laws; AEC "Stop and Consider" campaign only | Voluntary |
| **Canada** | No AI-specific election legislation; election watchdog rates AI as "high" risk | Gap |
| **New Zealand** | No verification infrastructure; Electoral Commission does not regulate ad content; no trust mechanisms | **Significant gap** |

27. New Zealand is an outlier among comparable democracies in having no mechanisms to address AI-generated political content. The verification system provides a practical response that does not require legislative change.

---

## KEY STATISTICS

| Statistic | Source |
|---|---|
| 80%+ of countries with elections in 2024 experienced AI-related electoral incidents | Harvard Ash Center |
| 63% of New Zealanders are nervous about AI | Ipsos |
| 80%+ of New Zealanders are concerned about disinformation impacts | DPMC National Security Survey |
| 550% increase in known deepfake videos globally since 2019 | Deepstrike |
| 57% of Americans are worried about AI generating false political content | Pew Research Center |
| 87% of voters support AI disclosure requirements for political ads | Public Citizen |
| Up to 8 million deepfake videos projected on social media by 2025 | Industry projections |

---

## RECOMMENDATIONS

The Labour Party is recommended to:

28. **note** that advances in generative AI now allow any actor to create realistic political imagery that falsely appears to originate from the Labour Party, at minimal cost and with minimal technical skill;

29. **note** that AI-generated political content has been used to undermine trust in elections internationally, including the annulment of Romania's presidential election in December 2024;

30. **note** that the National Party and ACT Party used AI-generated content in the 2023 New Zealand General Election without disclosure, and that neither party has committed to transparency measures for AI-generated content;

31. **note** that no mechanism currently exists for voters to verify whether political imagery is genuinely from the party it claims to represent;

32. **note** that more than 80 percent of New Zealanders are concerned about the impacts of disinformation, and that cybersecurity experts assess the 2026 election as facing serious AI-enabled misinformation risks;

33. **agree** to adopt the Political Image Verification System as a tool for authenticating Labour Party campaign imagery for the 2026 General Election;

34. **agree** to designate authorised Party users to manage image registration through the system;

35. **agree** to incorporate verification badges and QR codes into the Party's campaign imagery, where practicable, to enable voters to verify content;

36. **agree** to publicly advocate for all political parties to adopt the verification system, establishing transparency as a standard of political communication in New Zealand.

---

**Prepared by:** Political Image Verification Project Team

---

## APPENDIX: Technical Summary

### System Architecture

The system comprises a FastAPI (Python) backend with PostgreSQL database, a Next.js web frontend, and containerised deployment via Docker.

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js (React) | Public verification portal and party submission portal |
| API | FastAPI (Python) | RESTful API with OpenAPI documentation |
| Data | PostgreSQL + encrypted file storage | Party registry, hash index, encrypted image storage |

### Hashing Approach

| Method | Purpose | Detail |
|---|---|---|
| SHA-256 | Exact match | 256-bit cryptographic hash; detects unmodified originals |
| PDQ (Meta) | Perceptual match | 256-bit perceptual hash; tolerates compression, resizing, badge overlays; Hamming distance threshold |
| pHash | Fallback match | 64-bit perceptual hash; secondary matching algorithm |

### Encryption

- **Envelope encryption:** Each image encrypted with a unique AES-256-GCM data encryption key (DEK), which is itself encrypted by a key encryption key (KEK).
- **PII encryption:** Party user email addresses and contact details encrypted at rest.
- **Transport:** TLS for all connections.

### Authentication

- JWT-based authentication for party users.
- TOTP multi-factor authentication mandatory for party administrators.
- Role-based access control (admin, submitter, viewer).

### Key API Endpoints

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/v1/verify/image` | None | Upload image for verification |
| `POST /api/v1/verify/hash` | None | Verify by pre-computed hash |
| `GET /api/v1/verify/{id}` | None | QR code / verification ID lookup |
| `POST /api/v1/assets` | Party | Submit image for registration (with optional promoter statement overlay and OCR check) |
| `POST /api/v1/assets/add-promoter` | Party | Add promoter statement to image and return (batch mode) |
| `GET /api/v1/assets` | Party | List registered assets |
| `PUT /api/v1/parties/{id}/promoter-statement` | Admin | Set or update party promoter statement |

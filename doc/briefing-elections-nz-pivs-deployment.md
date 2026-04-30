# BRIEFING TO THE CHIEF ELECTORAL OFFICER

**From:** Political Image Verification Project Team

**Date:** April 2026

**Title:** Deployment of a Political Image Verification System for the 2026 General Election: Supporting Parties to Certify Their Own Campaign Imagery


---

## PROPOSAL

This briefing invites the Chief Electoral Officer to consider funding the deployment of a Political Image Verification System (PIVS) for the 2026 General Election. PIVS is a voluntary, party-driven tool that lets each registered party certify which campaign images are genuinely theirs, and lets members of the public check a given image against that party's own register. It is accompanied by an optional browser extension for desktop and mobile that performs this check passively in the background on images a user encounters while browsing. PIVS is an authenticity-of-origin tool. It is not a content regulator, a fact-checker, or an AI-detector.

The problem PIVS addresses is narrow and well-defined. Any image circulating online or in print can be falsely attributed to a New Zealand political party, regardless of how the image was created. PIVS gives each party a simple way to say "yes, this image is ours" or "no, this is not from us", and extends the long-standing logic of the promoter statement (section 204F, Electoral Act 1993) into the visual layer. The tool takes no view on whether an image is factual, persuasive, professionally produced, or AI-assisted. Those judgements properly remain with parties, voters, and existing bodies such as the Advertising Standards Authority.

The system has already been built to a working prototype by the project team at no cost to the Commission. The team is offering it to the Commission on whichever basis the Commission prefers: contracted deployment, intellectual property transfer, or a managed service, with optional technical support during the campaign period. The Commission's funded scope would be testing, security assurance, and operational hosting, estimated at \$40,000 to \$90,000 across the election cycle, with infrastructure hosted on Catalyst Cloud under the All-of-Government Cloud Framework Agreement.

---

## RELATION TO THE ELECTORAL COMMISSION'S STRATEGIC PRIORITIES

This proposal is designed to work alongside the Commission's existing functions, not to expand them. It supports:
   - the **2026 General Election programme** and Budget 2025 delivery and modernisation allocation of \$61.9 million, by adding a ready-built capability the Commission can offer parties and voters without commissioning bespoke development;
   - the **voter education function**, by giving the Commission a concrete, positive action it can point the public to when political imagery is in question (check with the party's own register), rather than asking the public to make their own judgements about authenticity;
   - the **integrity responsibilities** supported by the \$18.7 million Budget 2025 allocation for election integrity improvements over four years;
   - the **Commission's statutory role** under the Electoral Act 1993 to promote public confidence in the electoral process and to conduct voter education, without drawing the Commission into any role as a content regulator or arbiter of factual accuracy.

---

## EXECUTIVE SUMMARY

The Electoral Commission has a well-established and internationally respected role in running New Zealand's elections, and has rightly been deliberate about the boundaries of that role. In particular, the Commission has chosen not to become a regulator of advertising content, and this proposal is designed to respect that choice. PIVS is not a content regulator, a fact-checker, or an AI-detector. It is infrastructure that lets parties make a simple, verifiable statement about their own imagery: this is from us, or it is not.

The underlying problem is misattribution, not technology. Campaign images can be copied, edited, recombined, or fabricated from scratch, and then circulated in ways that imply they came from a party that never produced them. This has always been possible with photo editing. It is simply faster and cheaper now. The origin of a misattributed image (whether hand-edited, AI-generated, screenshot-manipulated, or entirely synthetic) does not change the nature of the harm, and PIVS treats all origins the same way.

PIVS works by giving each registered party an authenticated account in which they register the images they genuinely publish. The system stores cryptographic and perceptual hashes of each image, not judgements about the image. Members of the public, media organisations, and platform operators can check any image they encounter against the relevant party's register and receive a factual answer: registered by the party, or not registered. The system takes no position on whether an image is truthful, well-produced, or politically fair. Those remain matters for parties, voters, the Advertising Standards Authority, and the political process itself. A companion browser extension for desktop and mobile extends this to ordinary browsing: it runs locally on the user's device, uses on-device OCR to detect promoter statements (the existing statutory marker under section 204F that an image is election material), checks any such image against a local bloom filter of registered hashes that the device has downloaded, and only escalates to the server on a possible match. The extension can display an unobtrusive "unregistered" overlay where a promoter statement is present but no match is found. Users can also flag election-related images they find concerning. Detections and flags feed an administrative review queue, and where follow-up with the named promoter confirms an image is genuine it may be added to the register in a clearly distinct "authority-supplied" category. A built-in transparency mode shows users, the Commission, and security reviewers exactly what the extension is doing on their device.

The system has been developed to a working prototype by the project team, at no cost to the Commission, and is ready for acceptance testing. The team is offering the Commission a choice of arrangements: contracted deployment, intellectual property transfer, or a managed service, with optional ongoing technical support during the campaign period. The Commission's funded scope would be testing, security audit, and operational hosting, estimated at \$40,000–\$90,000 across the election cycle, with infrastructure hosted on Catalyst Cloud under the All-of-Government Cloud Framework Agreement.

---

## BACKGROUND

### Image misattribution as an electoral-integrity question

Political images have always been editable. Photo manipulation, selective cropping, and re-captioning have been part of campaign environments for decades, and are addressed primarily through the promoter statement regime and the Advertising Standards Authority's complaints process. What has changed is the ease and speed with which convincing imagery can be produced and circulated, regardless of the method of production. The framing of this briefing is deliberately method-neutral: the question PIVS helps answer is "did this image actually come from the party it is being attributed to?", not "how was it made?".

International experience confirms that misattribution of campaign imagery (by any method) is the point at which voter trust is most directly affected. The incidents below are presented for context, not as a claim that any particular actor or technology is the relevant threat in New Zealand:

   a. **United States (2024):** An AI-generated robocall mimicking President Biden's voice told New Hampshire voters not to vote. The perpetrator was fined USD \$6 million and criminally indicted. Russian operatives created deepfake videos of Vice President Harris making fabricated statements. AI-generated images falsely depicted Black Americans supporting a candidate.

   b. **Romania (2024):** The Constitutional Court annulled the presidential first-round election results on 6 December 2024, the first European country to cancel a presidential election due to cyber and information warfare. Investigations uncovered over 85,000 cyberattacks against electoral IT infrastructure, coordinated AI content, bot networks, and troll farms.

   c. **Slovakia (2023):** An AI-generated audio recording fabricated a phone call between a journalist and an opposition leader, purportedly discussing election rigging. The opposition lost the subsequent election.

   d. **Canada (2025):** A deepfake video of Prime Minister Carney reached over one million views. Canada's election watchdog classified AI use as a "high" risk.

   e. **Taiwan (2024):** Microsoft identified China-based deepfake operations as the first confirmed use of AI-generated material by a nation-state to influence a foreign election.

### The "liar's dividend"

A secondary effect identified in the academic literature is the "liar's dividend": the ability of public figures to dismiss genuine imagery as fabricated. This cuts both ways, genuine content can be wrongly discounted, and fabricated content can be wrongly accepted. A provenance register addresses both sides symmetrically: a party can positively confirm that a given image is theirs, and can positively confirm that a given image is not.

### Public trust in New Zealand's electoral process

New Zealand enjoys comparatively high public trust in its electoral system, and the Commission is central to that. At the same time, the Department of the Prime Minister and Cabinet's national security surveys in 2022 and 2023 found that more than 80 percent of New Zealanders are concerned about the impacts of disinformation, and Ipsos polling shows 63 percent of New Zealanders are nervous about AI. A voluntary party-authored verification register is a measured response to this concern: it gives voters a reliable source of "is this image from the party?" without asking the Commission to take any view on content.

The practical case for PIVS is narrow. A fabricated or misattributed campaign image, whatever its origin, can be circulated on social media and associated with a party that never produced it. Today, a voter wishing to check such an image has no authoritative party-sourced reference to compare it against. PIVS provides exactly that reference point, and nothing more.

Commentary on the 2026 election cycle has noted that the volume and realism of online political content will continue to grow. PIVS does not try to stem that volume. It simply lets parties publish a verifiable register of their own material so that voters, media, and platforms can cross-check when they choose to.

### The Commission's position on content, and where PIVS sits relative to it

The Commission has been clear, correctly in our view, that it does not regulate the content of election advertisements and does not take a position on the use of AI in election ads. That restraint is appropriate: content regulation sits uneasily with the Commission's role as a neutral administrator of elections, and the matters that flow from content (accuracy, fairness, taste, creative method) are better handled through the existing settings, party accountability under section 204F, the Advertising Standards Authority's fast-track process, the Broadcasting Standards Authority's Election Programmes Code, and the normal workings of political debate and a free press.

PIVS has been deliberately designed to sit within that restraint, not against it. Specifically:

    a. PIVS makes no judgement about the content of any image. It does not detect AI, assess factuality, or evaluate persuasive intent.

    b. Parties decide what they register. The Commission does not curate, approve, or refuse images.

    c. The Commission's role in the operational system is limited to hosting, account administration for registered parties, and voter-facing information, functions that sit comfortably within existing administrative and voter-education responsibilities.

    d. Participation by parties is voluntary. Voters are not required to verify. Media and platforms are not required to integrate.

In this way PIVS extends the existing logic of the promoter statement, which identifies who is responsible for an advertisement, to the visual layer, by letting parties additionally attest which visual material is theirs. It fills a narrow operational gap (there is currently no shared reference register of party-authored images) without moving the Commission's role in any other direction.

Internationally, other jurisdictions have taken a range of approaches to similar issues. These are included for comparative context only; most involve content-regulation powers that New Zealand has chosen not to adopt, and PIVS does not propose to introduce:

    a. **South Korea** amended the Public Official Election Act to ban election-related deepfakes within 90 days of election day.

    b. **Singapore** passed the Elections (Integrity of Online Advertising) Amendment Bill, prohibiting certain digitally generated content depicting candidates during elections.

    c. **The European Union** classified AI systems used for influencing elections as high-risk under the AI Act (fully enforceable from August 2026), with associated transparency measures.

    d. In the **United States**, 28 states have enacted laws addressing deepfakes in political communications.

    PIVS is comparatively light: it does not restrict, label, or classify any content. It simply gives parties a way to publish an authenticated list of their own images.

---

## ANALYSIS

### The proposed system

The Political Image Verification System (PIVS) is a privacy-first platform that lets political parties register their own campaign imagery and lets the public check imagery against those registers. A "registered by party" result confirms provenance only, it is not an endorsement of the image's content, accuracy, or fairness. The system has four components:

    a. **Party submission portal:** Authorised party representatives submit campaign images through authenticated accounts with multi-factor authentication. The system computes cryptographic and perceptual hashes of each image before encrypting and storing it.

    b. **Public verification portal:** Any member of the public can upload a political image or scan a QR code to check whether it has been registered by a political party. No personal information or account is required.

    c. **Verification API:** Media organisations and platform operators can integrate verification into their own systems through a documented programming interface.

    d. **Administrative dashboard:** Commission staff can monitor system performance, manage party accounts, and review verification logs.

### How verification works

The system uses a dual-hashing approach to handle the practical reality that political images are modified as they circulate:

    a. **Cryptographic hash (SHA-256):** Provides exact-match verification for unmodified original images. This is fast and deterministic.

    b. **Perceptual hash (PDQ, developed by Meta):** Provides fuzzy matching that tolerates visual modifications commonly introduced by social media platforms, including JPEG recompression, resizing, minor cropping, screenshot capture, and the addition of verification badges or QR codes. PDQ uses a 256-bit hash with a Hamming distance threshold; images scoring within this threshold are identified as matching. pHash provides a secondary fallback algorithm. This is processed locally to avoid privacy concerns of sending images to a third-party service. Generative AI is not used in the verification process to avoid the risk of hallucination and to maintain transparency and auditability.

This dual approach means that an image originally registered by a party will still be verified even after it has been shared on Facebook, screenshotted, or printed on a hoarding with a QR verification code added.

### Privacy and security

The system is designed with a privacy-first architecture:

    a. All stored images are encrypted with AES-256-GCM using envelope encryption, where each image has a unique data encryption key.

    b. The public verification process exposes only hash comparisons, never the stored images themselves.

    c. Verification is anonymous. No login, personal information, or tracking is required.

    d. IP addresses are hashed in system logs and cannot be reversed.

    e. Party user personal information (email addresses) is encrypted at rest.

    f. The system is designed to comply with the Privacy Act 2020, notwithstanding the political party exemption.

### Verification badges and QR codes

When a party registers an image, the system generates:

    a. A small verification badge (under 5 percent of image area) that can be overlaid on the image. The badge is deliberately sized to remain within the perceptual hash tolerance so that badged images still verify against the original.

    b. A QR code encoding a verification URL. This is particularly useful for physical media such as hoardings and billboards, enabling voters to scan and verify on their mobile device.

    c. A unique verification ID and URL for each registered image.

### Promoter statement management

The system includes integrated support for Electoral Act promoter statements (section 204F). Each party account can store a promoter statement, and the system provides tools to:

    a. **Add promoter statements to images:** Authorised party users can overlay their party's promoter statement onto campaign images during registration. The overlay uses contrast-aware text placement (meeting WCAG 2.1 AA legibility standards with a minimum 4.5:1 contrast ratio) and configurable corner positioning, with automatic adjustment for portrait and landscape orientations.

    b. **Verify promoter statements using OCR:** The system can scan submitted images using optical character recognition to check whether a promoter statement is already present and whether it matches the party's registered statement, using fuzzy text matching to account for OCR imprecision. This is locally processed so information is not sent to a third-party service.

    c. **Batch processing:** Party users can add promoter statements to images in batch mode (upload and download directly) or via email, without registering images as verified assets. This supports high-volume campaign workflows.

    d. **Email interface:** Images can be submitted as email attachments to a processing address. Anti-spoofing verification ensures that images are processed only after the registered user confirms the submission via a verification email sent to their authenticated address.

This feature directly assists parties in meeting their existing legal obligations under the Electoral Act, reducing the barrier to compliance and ensuring that promoter statements are consistently legible and correctly placed.

### Complementary role to Commission functions

PIVS has been designed to fit inside the existing architecture of New Zealand's electoral communications regime, not to reshape it. It works alongside the Commission's current functions and the current division of responsibilities with the ASA and BSA:

    a. The promoter statement regime (section 204F, Electoral Act 1993) tells voters who is responsible for an advertisement. PIVS complements that by letting parties additionally attest which visual material is genuinely theirs, and by giving parties practical tools to produce compliant, legible, contrast-aware promoter statements on their own imagery.

    b. The Advertising Standards Authority's fast-track complaints process remains the appropriate mechanism for matters of content, misleading claims, taste, decency, and truthfulness. PIVS does not duplicate, pre-empt, or substitute for that process. A PIVS "registered by party" result says nothing about whether an image is fair, accurate, or appropriate, only that the party acknowledges it as their own.

    c. The Commission's voter education programme can, at the Commission's discretion, point members of the public to PIVS as one practical action they can take when they encounter political imagery of uncertain origin. This fits naturally within the existing voter-education function and does not expand the Commission's regulatory scope.

    d. If the Commission wishes, PIVS can be presented as a component of the Commission's 2026 election delivery and modernisation programme, a ready-built capability the Commission has chosen to host for the benefit of parties and voters, without committing the Commission to any new regulatory position.

### Development status and readiness

The system is ready for early testing. The current status is:

    a. **Core application:** Complete. FastAPI backend, Next.js frontend, PostgreSQL database, and containerised Docker deployment are all built and functional.

    b. **Hashing and verification:** Complete. SHA-256, PDQ, and pHash algorithms are integrated and tested against common image transformation scenarios.

    c. **Encryption and security:** Complete. AES-256-GCM envelope encryption, JWT authentication, TOTP multi-factor authentication, and role-based access control are implemented.

    d. **Party registry:** Complete. Pre-seeded with New Zealand's seven registered parliamentary parties.

    e. **Promoter statement tools:** Complete. Contrast-aware text overlay with WCAG 2.1 AA legibility, OCR verification via Tesseract, batch processing mode, and email processing interface with anti-spoofing verification.

    f. **Production deployment configuration:** Complete. Gunicorn application server, Nginx reverse proxy with rate limiting, security headers, and TLS termination are configured.

The system is ready for acceptance testing, security audit, and deployment either as a contracted deployment on Catalyst Cloud or to the Commission's operational environment.

### Risks and mitigations

The following risks have been identified:

| Risk | Mitigation |
|---|---|
| Low party adoption reduces usefulness | Early engagement with major parties; simple onboarding process; system pre-seeded with seven registered NZ parties |
| False positive matches (incorrect verification) | Multiple hash algorithms with configurable thresholds; confidence scoring; human review pathway |
| System targeted by cyberattack | Rate limiting; web application firewall; encrypted storage; security audit before launch; nginx reverse proxy with rate limiting zones |
| Late election traffic spike overwhelms system | CDN deployment; auto-scaling infrastructure; load testing before election |
| Public confusion about what verification means | Clear user interface messaging; verification means "registered by a party" not "factually accurate" |
| Adversarial image manipulation to evade detection | PDQ is resistant to common transforms; multiple hash algorithms reduce evasion; DINOv2-based hashing available for future enhancement |
| Reputational risk to Commission if system fails | Thorough testing and security audit; soft launch with limited publicity; staged rollout |
| Browser extension privacy concerns | All image analysis performed locally on-device; only hashes transmitted; no account or tracking; independent privacy review before release |
| Browser extension false positives on OCR | Conservative OCR confidence threshold; extension only acts on images where a promoter-statement pattern is detected; user can dismiss the overlay at any time |
| "Authority-supplied" category misused to register contested imagery | Registration under this category requires documented confirmation from the named promoter; register entries are publicly labelled as authority-supplied so users can distinguish from party-submitted entries |
| Extension-enabled harassment via flagging | Flags are administrative triage input only, with no automatic publication or content action; rate limiting per device; flag reason codes rather than free-text amplification |

---

## BROWSER EXTENSION PROPOSAL

### Rationale

The core PIVS register and public website described above require voters to take action: encountering a suspicious image, copying or screenshotting it, navigating to the verification site, and uploading it. This works, but most voters will not do it. A companion browser extension turns PIVS from a tool voters have to seek out into a background service that protects them while they browse, so that the most common way to benefit from verification is simply to have the extension installed. The extension also provides a low-friction flagging channel that feeds administrative follow-up with named promoters and, where appropriate, referrals to the Advertising Standards Authority. This is the component of the proposal with the largest expected impact on the ordinary voter's experience and is therefore treated here as a substantive proposal in its own right.

### Design principles

The extension is designed to respect three constraints that reflect both the Commission's restraint on content regulation and ordinary user-privacy expectations:

- **Method-neutral.** The extension does not attempt to detect AI-generated content, deepfakes, or any specific production method. It looks only for images that carry a section 204F promoter statement and checks them against the register.
- **Local-first.** All image analysis, OCR of the promoter statement and perceptual-hash computation, runs on the user's device. The image itself never leaves the device. Only a 256-bit hash and the detected promoter-statement text are transmitted, and only when a promoter statement has been detected.
- **Non-coercive.** The extension never blocks, hides, replaces, or reports on images on the user's behalf. Overlays are informational and dismissable. The judgement about what to do with the information remains entirely with the voter.

### User experience

For an ordinary voter who has installed the extension, the experience is passive. Nothing visible happens on the vast majority of images, because the vast majority of images on the web do not carry a promoter statement. When an image carrying a promoter statement is encountered, one of three outcomes applies:

- **Registered:** A small green tick badge is overlaid in the corner, showing the issuing party's name and that the image has been registered. Clicking the badge opens a verification record page.
- **Authority-supplied:** A small blue badge indicates that the image is in the register via the authority-supplied category, the named promoter has confirmed to the Commission that the image is theirs. Clicking explains the distinction.
- **Not found:** A small amber badge overlays the image with the message "Unregistered political image, carries a promoter statement but has not been verified by the named party". The badge is dismissable and does not block the image.

The user can right-click (or long-press on mobile) any political image to bring up a "Flag this political image" menu with predefined reasons: "appears misattributed", "promoter statement appears fake", "content concern", or "other". An optional short note is supported. Flags are submitted with the image's perceptual hash and the page URL.

### Detection pipeline

1. The content script observes images that become visible in the viewport, filtered to images above a minimum display size (to avoid processing icons and sprites).
2. For each candidate image, an on-device OCR pass is run using a WebAssembly build of Tesseract configured for short-form text extraction. The OCR result is matched against promoter-statement patterns, phrases such as "Authorised by" followed by a name and address, with fuzzy matching.
3. If a promoter statement is detected, the extension computes a 256-bit PDQ perceptual hash of the image locally.
4. The hash and the detected promoter text are sent to `POST /api/v1/verify/hash` with a category hint. The response is one of `registered`, `authority-supplied`, or `not_found`, along with the issuing-party metadata where applicable.
5. The extension renders the appropriate overlay. Nothing is uploaded to the server except the hash and the promoter-statement text string.

### Administrative workflow

Three administrative workflows are added to the existing PIVS admin dashboard:

- **Unregistered-with-promoter queue.** Hashes reported as "promoter statement present, not in register" are aggregated and de-duplicated across users. Administrators see: the detected promoter-statement text, the number of times the image has been observed, sample referring URLs, and the first-seen and last-seen timestamps. This gives the Commission a practical signal that a given image is circulating as apparent election material without being in any party's register.
- **Authority-supplied registration.** Administrators may contact the named promoter to confirm whether the image is genuinely theirs. Where the promoter confirms and provides the image, the administrator registers the image under the distinct **authority-supplied** category. This closes off a trivial evasion route (a promoter who simply does not register their imagery) while preserving full transparency about the source of the register entry, the public verification portal shows explicitly that the entry was completed by the Commission on the promoter's confirmation rather than by the promoter directly.
- **User-flag review.** Flags submitted via the extension's "Flag this political image" action are triaged by administrators. Flags are not acted on by the Commission as content decisions. They are used only to prioritise outreach on the unregistered-with-promoter queue and, where the matter falls within another body's jurisdiction (for example, an ASA code complaint), to refer the matter on. The flag channel does not create any new content-complaints jurisdiction for the Commission.

### Distribution

The extension is built once as a Manifest V3 WebExtension and published to:

- the Chrome Web Store (covering Chrome, Edge, Brave, Opera, and other Chromium browsers on Windows, macOS, Linux, ChromeOS, and Android);
- the Firefox Add-ons store (desktop and Android);
- the Safari Extensions Gallery (macOS and iOS/iPadOS), distributed as a macOS app wrapper per Apple's current requirements.

Installation is voluntary. The Commission's voter-education programme would link to the extension alongside the main PIVS verification website.

### Privacy and security

- **No account and no registration.** Users install the extension and it works.
- **No browsing history or telemetry.** The extension does not record which pages the user visits, does not send analytics, and does not retain any history between sessions.
- **Image bytes never leave the device.** Only perceptual hashes are transmitted, and only where a promoter statement has been detected on the image.
- **Local bloom filter.** Each install downloads a small (under 10 KB) bloom-filter snapshot of all registered hashes. Image hashes are checked against this filter on the user's device first. Only on a "maybe registered" hit does the extension query the server to confirm. This means the server cannot see which images a user is browsing in the common case, and the privacy floor of the extension is set by the user's own device, not by trust in the Commission's logs.
- **Rate limiting.** A per-install nonce limits requests to reasonable voter-scale volumes (a few hundred lookups per day) to mitigate abuse.
- **Independent review.** The extension would be reviewed under the same security assurance process as the core PIVS system (GCSB-approved provider, privacy review). A manifest-only source-available release allows independent inspection of what the extension does on the user's device.

### Transparency: debug mode

Public confidence in the extension depends on people being able to see what it actually does, not just on assurances in this briefing. The extension therefore includes a built-in **Debug (transparency) mode**, accessible from the popup with a single toggle. When debug mode is on, the popup shows:

- The status of the local bloom filter: whether it is loaded, how many hashes it covers, the number of bits and hash functions, the estimated false-positive rate, and the timestamp the snapshot was generated.
- A live, scrolling log of every meaningful step the extension takes: image observed, OCR run, hashes computed, bloom filter consulted (with hit or miss), API call made (with latency and result category), overlay rendered, flag or report submitted, and any error.

The log is capped at the most recent 500 entries, lives in memory only, and is never transmitted. A user can clear it or export it as a JSON file at any time. The Commission, the GCSB security reviewer, journalists, and curious voters can therefore audit the extension's behaviour on a real device, side by side with this briefing, before relying on it.

### Expected volumes

Verification-register lookups triggered by extension installs are expected to be small per user (election-period political images account for a minority of what voters see online) but the aggregate can be significant. Indicative estimates:

- 10,000–50,000 installed users across the 2026 campaign period, a small fraction of the voting public, scaled by organic adoption and voter-education promotion.
- 5–50 register lookups per installed user across the campaign period, depending on the user's browsing patterns during the regulated advertising period.
- Peak aggregate lookups: 20,000–150,000 per day during the final weeks of the campaign, dominated by hash-only requests. This volume is within the capacity of the core PIVS infrastructure described in the financial implications section; no additional scaling is required beyond what is already provisioned for the public-portal use case.

### Marginal cost impact

The extension does not materially change the infrastructure hosting envelope. Its development and publication represent the main incremental cost, and are bundled into the existing project-team deliverable. Indicative additional items for the Commission's funded scope are:

| Item | Estimated additional cost (NZD) |
|---|---|
| Independent security review of extension (in addition to core security audit) | \$5,000–\$10,000 |
| Accessibility review of extension overlays | \$1,000–\$2,000 |
| Extension-store developer-account setup and submission fees (one-off) | \$200–\$500 |
| Admin-queue UI testing | included in core acceptance testing |
| Infrastructure scaling for extension lookups | nil, absorbed by existing provisioning |

### Risks specific to the extension

These are summarised here and also included in the consolidated risk table earlier in this briefing:

| Risk | Mitigation |
|---|---|
| Privacy concerns about browser-installed software | All analysis local; only hashes transmitted; no account or history; independent privacy review before release |
| OCR false positives creating spurious "unregistered" overlays | Conservative OCR confidence threshold; only act where a promoter-statement pattern is matched; overlay is dismissable |
| Abuse of the user-flag channel for harassment of parties | Flags are administrative triage input only; no automatic public action; rate-limited per device; reason codes only |
| "Authority-supplied" category being used to register contested imagery | Requires documented confirmation from the named promoter; publicly labelled as authority-supplied so users can distinguish from party-submitted entries |
| Extension-store review delays blocking release | Manifest V3 from the outset; early draft submission to each store; fallback to a manually-installed developer build for advanced users while formal listings are approved |

---

## POPULATION IMPLICATIONS

The system is designed to benefit all New Zealanders who engage with political advertising. Specific population implications include:

    a. **Maori:** Imagery purporting to represent Maori positions or interests can be fabricated or misattributed by any actor, by any method. A party-authored register lets Maori communities confirm whether imagery attributed to a particular party is genuinely that party's own, without requiring any judgement about content.

    b. **Pacific peoples:** The same provenance-check benefit applies where imagery is targeted at, or purports to represent, Pacific communities.

    c. **Older New Zealanders:** Research indicates lower digital literacy among older populations. A single, clearly signposted provenance check, especially via QR code on physical media such as hoardings and printed material, provides an accessible and easy-to-explain verification method.

    d. **Rural communities:** Political advertising on physical media (hoardings, billboards) is prevalent in rural areas. QR code verification is particularly relevant for these communities.

    e. **Disabled people:** The web portal will be designed to meet WCAG 2.1 AA accessibility standards.

---

## HUMAN RIGHTS

The proposal is consistent with the New Zealand Bill of Rights Act 1990 and the Human Rights Act 1993. The system:

    a. does not restrict the publication of any content (section 14, freedom of expression);

    b. is voluntary for political parties to adopt;

    c. does not collect or process personal information from members of the public performing verification;

    d. supports informed participation in elections by enabling voters to assess the authenticity of political communications (section 12, right to vote).

---

## FINANCIAL IMPLICATIONS

### Estimated image volumes

Based on data from the 2023 General Election, the system would need to handle the following image volumes:

    a. In the 2023 election, the six main parliamentary parties ran approximately 9,000 paid Facebook advertisements across a three-month regulated period: National ran 4,073 Facebook ads, ACT ran 844 Meta ads, and the remaining parties ran a combined total of approximately 4,100 ads (Victoria University of Wellington; RNZ; The Spinoff). However, the number of **unique images** is substantially smaller than the number of ads, as each image is reused across multiple ad variants with different demographic and geographic targeting.

    b. Physical campaign materials add further volume. Labour's 2023 expense return recorded 130 large, 40 medium, and 200 small hoardings for a single electorate, with similar volumes across other parties and electorates (Electoral Commission, 2023 Party Expenses Returns). Parties also produce flyers, billboards, social media graphics, and print collateral.

    c. Based on these volumes, the estimated number of **unique images** that parties would register with the system is:

    | Category | Major Party (×3) | Minor Party (×4) |
    |---|---|---|
    | Party-wide campaign graphics (policy, leader, attack ads) | 30–80 | 15–40 |
    | Electorate candidate materials | 150–400 | 30–100 |
    | Social media originals | 50–150 | 20–50 |
    | Hoardings and billboard designs | 10–30 | 5–15 |
    | Print collateral (flyers, DLs) | 20–50 | 10–20 |
    | **Subtotal per party** | **260–710** | **80–225** |

    d. **System-wide totals:** Conservative estimate: ~1,300 images (3 major parties × 300 + 4 minor parties × 100). Moderate estimate: ~2,100 images. High estimate (including individual candidate submissions): 3,000–5,000 images.

    e. **Storage requirement:** Each registered image generates up to four encrypted variants (original, badge overlay, QR code, promoter-stamped version) at approximately 3 MB each, totalling ~12 MB per image. At 5,000 images, total encrypted storage is approximately 60 GB, a modest volume for cloud object storage.

    f. **Verification query volume:** During the campaign period, each registered image may be verified multiple times by the public, media, and automated integrations. Peak verification traffic is estimated at 5,000–20,000 queries per day during the final weeks of the campaign, based on the volume of social media political advertising observed in 2023.

### Financial implications

The system has initial development to alpha testing, with this cost invested by the project team. The project team is open to discussing arrangements for contracted deployment, intellectual property transfer and/or technical support during the campaign period; however, the costs below relate only to the Commission's operational hosting and deployment requirements.

**Recommended hosting platform:** Catalyst Cloud, the only All-of-Government Cloud Framework provider with 100% New Zealand-based infrastructure. Catalyst Cloud is ISO 27001 and ISO 27017 certified, PCI DSS compliant, and all three data centres are located in New Zealand, ensuring data sovereignty under New Zealand law. Cloud usage by government agencies is aggregated under the AoG framework, providing volume discounts regardless of individual agency spend. All prices below are sourced from Catalyst Cloud's published price list (catalystcloud.nz/pricing/price-list/, effective 1 June 2025) and are in NZD exclusive of GST unless otherwise noted.

The Commission's costs for testing, security assurance, and operational hosting are estimated as follows:

| Item | Estimated Cost (NZD) | Notes |
|---|---|---|
| **Security audit and penetration test if needed** | \$20,000–\$40,000 | Pre-launch independent security assessment; recommended to be conducted by a GCSB-approved provider |
| **Acceptance and integration testing** | \$10,000–\$20,000 * | Commission staff or contracted testers to validate functionality against Commission requirements |
| **Load and stress testing** | \$5,000–\$10,000 * | Simulate election-day traffic volumes to validate system capacity |
| **WCAG accessibility audit** | \$1,000–\$2,000 * | Confirm the public-facing portal meets WCAG 2.1 AA standards |
| **Privacy Impact Assessment** | \$0–\$5,000 * | Required under the Privacy Act 2020; a draft PIA can be provided with the system |
| **Infrastructure hosting** (see breakdown below) | \$625–\$1,275/month | Catalyst Cloud hosting for the deployment period (estimated 8 months, April–November 2026) |
| | | |
| **Total estimated operational cost** | **\$41,000–\$87,000** | Across the 2026 election cycle (including 8 months' hosting at \$5,000–\$10,200) |

\* These items could be conducted in-house by Commission staff with existing capabilities, reducing costs to staff time only. The privacy impact assessment, acceptance testing, load testing, and accessibility audit do not require external contractors if the Commission has qualified personnel available.

The monthly infrastructure hosting estimate of \$625–\$1,275 is based on the following Catalyst Cloud configurations:

    a. **Application compute:** \$285–\$570/month. Two application servers for the verification API, hash computation (SHA-256, PDQ, pHash), Tesseract OCR processing, and image overlay processing. Lower bound: 2× c1.c2r4 instances (2 vCPU, 4 GB RAM each, at \$95.05/month each). Upper bound: 2× c1.c4r8 instances (4 vCPU, 8 GB RAM each, at \$190.09/month each) for election-day capacity. One additional worker instance for background processing (c1.c2r4 at \$95.05/month to c1.c4r8 at \$190.09/month).

    b. **Managed PostgreSQL database:** \$180–\$360/month. Catalyst Cloud Managed Database Service with automated backups and replication. A db.c1.c2r4 instance (2 vCPU, 4 GB RAM) provides sufficient capacity for the party registry, asset index, and verification logs. The upper estimate includes a read replica for high-availability during election peak.

    c. **Encrypted image storage:** \$5–\$20/month. Object storage for AES-256-GCM encrypted images, verification badges, QR codes, and promoter-stamped versions. At 60 GB (5,000 images × 12 MB), geo-replicated object storage costs \$0.10/GiB/month = ~\$6/month. Single-region storage at \$0.05/GiB/month halves this cost. Block storage for the database at \$0.21/GB/month for 50 GB adds ~\$10.50/month.

    d. **Network and load balancing:** \$75–\$150/month. Load balancer (\$24.62/month), public IPv4 addresses (\$4.50/month each), and outbound data transfer at \$0.12/GB. At 200 GB/month outbound (verification responses, image downloads, API traffic), bandwidth costs ~\$24/month. CDN for static frontend assets may be provided externally (e.g., Cloudflare free tier) or via Catalyst's network.

    e. **Operational overhead (15% contingency):** \$80–\$165/month. Covers monitoring, alerting, SSL/TLS certificates (free via Let's Encrypt), DNS, log aggregation, automated backups, and a buffer for unexpected traffic scaling or incident response during the election period.

All prices above are exclusive of GST (15%). Including GST, the monthly hosting cost is approximately \$720–\$1,470/month, or \$5,750–\$11,750 for an eight-month deployment period.

**Cost drivers and scaling:** The primary cost driver is compute, not storage. Image storage at the volumes estimated for a New Zealand general election (60 GB) is negligible on Catalyst Cloud, costing under \$10 per month even with geo-replication. The upper hosting estimate accounts for running redundant application servers and a database read replica during the peak election period (August to October), with the option to scale down to the lower configuration outside the peak.

These costs represent a fraction of the Budget 2025 allocations available to the Commission (\$18.7 million for integrity improvements; \$61.9 million for election delivery). The total is modest compared to the potential cost of an electoral integrity incident. Romania's annulled election required a full re-run at significant public expense and lasting damage to democratic legitimacy.

By deploying a system that has already been developed rather than commissioning bespoke development, the Commission avoids the typical software procurement costs and timeframes that would otherwise make deployment ahead of the 2026 election impractical.

---

## LEGISLATIVE IMPLICATIONS

No legislation is required to deploy the system. The system operates within existing regulatory settings as a voluntary verification tool. The Commission's statutory functions under the Electoral Act 1993, particularly the obligation to promote public confidence in the electoral process and to conduct voter education, provide sufficient basis for offering this tool to the public.

The Chief Electoral Officer may wish to note that:

    a. Future legislative consideration could make registration of political advertising images mandatory rather than voluntary, providing stronger assurance to the public.

    b. The Independent Electoral Review recommended expanding the undue influence offence and considering microtargeting regulations. A verification system would complement any such future legislative changes.

    c. Deployment now as a voluntary tool establishes operational experience and public familiarity that would ease any future transition to a mandatory regime.

---

## CONSULTATION

The following agencies have interests relevant to deployment:

    - **Ministry of Justice:** As the policy agency for electoral law and the Minister's office.
    - **Department of the Prime Minister and Cabinet:** As the lead agency for national security and disinformation resilience.
    - **Government Communications Security Bureau:** For cybersecurity review of the system prior to deployment.
    - **Office of the Privacy Commissioner:** To confirm the privacy-by-design approach meets best practice.
    - **Department of Internal Affairs:** As the lead for the Government's digital strategy and AI framework.

Engagement with registered political parties would be required before deployment to ensure uptake. The system is pre-seeded with accounts for all seven registered parliamentary parties, and onboarding can commence as soon as the Commission confirms operational readiness.

---

## PROPOSED DEPLOYMENT TIMELINE

Given that the system is already developed, the following timeline is indicative:

| Phase | Activity | Indicative Period |
|---|---|---|
| **1. Acquisition** | Engage with project team on IP transfer and/or support arrangements; receive source code and documentation | February - March 2026 |
| **2. Testing** | Acceptance testing; integration with Commission infrastructure; accessibility audit; browser-extension review and submission to Chrome, Edge, Firefox, Safari, and mobile extension stores | March - April 2026 |
| **3. Security** | Independent security audit and penetration test; GCSB review | April - May 2026 |
| **4. Remediation** | Address any findings from testing and security audit | May - June 2026 |
| **5. Party onboarding** | Engage registered parties; set up authenticated accounts; provide training | June - July 2026 |
| **6. Soft launch** | Limited public availability; monitor system performance | July 2026 |
| **7. Full deployment** | Public launch integrated with Commission voter education programme | August 2026 |
| **8. Election operations** | Full operational support through election day and post-election period | August - November 2026 |

This timeline provides adequate time for thorough testing and security assurance while ensuring the system is operational well before the regulated election advertising period commences.

---

## COMMUNICATIONS

If the Chief Electoral Officer agrees to progress this proposal, officials recommend:

    a. An announcement framed around election integrity and public trust, positioning the system as part of the Commission's broader 2026 election modernisation programme.

    b. Engagement with major media organisations to encourage integration of the verification tool into their election coverage workflows.

    c. Inclusion in the Commission's 2026 voter education programme, with clear messaging about what verification means and how to use the tool.

    d. A public-facing website with clear, plain-language guidance, integrated with the Commission's existing elections.nz domain.

    e. Engagement with social media platforms operating in New Zealand to encourage adoption of the verification API.

    f. Publication of the companion browser extension to the Chrome, Edge, Firefox, Safari, and supported mobile extension stores, with plain-language installation guidance for voters who wish to use passive verification while browsing.

---

## PROACTIVE RELEASE

The Chief Electoral Officer is advised to proactively release this briefing, with any redactions necessary to protect security-sensitive technical details, within 30 business days of decisions being confirmed.

---

## RECOMMENDATIONS

The Chief Electoral Officer is recommended to:

**Context**

**note** that campaign images can be edited, recombined, or fabricated by a range of means, and that the ease and volume of such production has increased;

**note** that the question PIVS addresses is narrow, whether a given image is genuinely from the party it is being attributed to, and that PIVS takes no view on content, factuality, creative process, or the use of any particular production method including AI;

**note** that the Commission has appropriately declined to regulate the content of election advertisements, and that PIVS has been designed to operate consistently with that position as a voluntary, party-authored provenance register;

**note** that parties currently have no shared infrastructure through which to attest which campaign imagery is genuinely theirs, and that voters and media have no corresponding reference against which to check;

**note** that the Commission's statutory functions, to administer elections, promote public confidence in the electoral process, and conduct voter education, provide a sufficient basis for hosting a voluntary provenance tool without expanding the Commission's role into content regulation;

**note** that Budget 2025 allocated \$18.7 million over four years for election integrity improvements and \$61.9 million for 2026 General Election delivery and modernisation;

**note** that a working prototype of the Political Image Verification System has been developed at no cost to the Commission and is available on terms of the Commission's choosing (contracted deployment, IP transfer, or managed service), with operational hosting and deployment costs estimated at \$40,000–\$90,000 across the election cycle on Catalyst Cloud under the All-of-Government Cloud Framework Agreement;

**note** that a companion browser extension (for desktop and mobile browsers) can detect promoter statements on images encountered while browsing, check the verification register automatically, and alert the user where an image carrying a promoter statement is not registered. This gives voters passive protection without requiring them to actively seek out verification;

**Decisions**

**agree** that a voluntary, party-authored image provenance register is a useful complement to existing electoral integrity arrangements for the 2026 General Election, on the basis that it does not change the Commission's role in relation to advertising content;

**agree** that the Political Image Verification System, which lets parties register their own campaign images and lets the public check images against those registers using cryptographic and perceptual hashing, with a privacy-first encrypted architecture, is a suitable implementation;

**agree** that the companion browser extension, the user-initiated content-concern flagging channel, and an administrative "authority-supplied" image category (for cases where an image carrying a promoter statement has not been registered by the party but is confirmed on follow-up to be genuine) form an appropriate extension of the core system;

**agree** to engage with the project team on commercial and technical arrangements (contracted deployment, IP transfer, or managed service) and to proceed with testing and deployment;

**agree** that the system will be deployed as a voluntary tool, available to all registered political parties, and that no party is required to register images and no voter is required to verify them;

**Next steps**

**direct** officials to engage with the project team on arrangements for intellectual property transfer and/or technical support, and to receive source code, documentation, and deployment configurations;

**direct** officials to commission an independent security audit and penetration test of the system (including the browser extension), and to engage the Government Communications Security Bureau for review;

**direct** officials to conduct acceptance testing and integration of the system with Commission infrastructure, including a WCAG 2.1 AA accessibility audit and publication of the browser extension to the Chrome, Edge, Firefox, Safari, and mobile browser extension stores;

**direct** officials to engage with registered political parties on voluntary adoption and to commence account onboarding;

**direct** officials to integrate the verification tool, browser extension, and user-flagging channel into the Commission's 2026 voter education programme;

**direct** officials to establish an administrative workflow for reviewing images flagged by the extension as "carries a promoter statement but not registered", including criteria for follow-up with the named promoter and for manual registration under the authority-supplied image category where appropriate;

**direct** officials to report back to the Chief Electoral Officer by April 2026 on testing outcomes, security audit results, and confirmed deployment timeline.

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
| `POST /api/v1/verify/hash` | None | Verify by pre-computed hash (used by browser extension) |
| `GET /api/v1/verify/{id}` | None | QR code / verification ID lookup |
| `GET /api/v1/parties` | None | List registered parties |
| `POST /api/v1/extension/report` | None (rate-limited) | Browser extension: report a promoter-statement-bearing image that did not match the register (submits hash, named promoter text, sample URL) |
| `POST /api/v1/extension/flag` | None (rate-limited) | Browser extension: user-initiated flag on a political image with reason code and optional note |
| `POST /api/v1/assets` | Party | Submit image for registration (with optional promoter statement overlay and OCR check) |
| `POST /api/v1/assets/add-promoter` | Party | Add promoter statement to image and return (batch mode) |
| `GET /api/v1/assets` | Party | List registered assets |
| `POST /api/v1/admin/assets/authority-supplied` | Admin | Register an image in the "authority-supplied" category on confirmation from the named promoter |
| `GET /api/v1/admin/review-queue` | Admin | List unregistered-with-promoter detections and user flags awaiting triage |
| `PUT /api/v1/parties/{id}/promoter-statement` | Admin | Set or update party promoter statement |
| `POST /api/v1/email/verify/{job_id}` | Token | Confirm an email-submitted processing job |

### Browser Extension

The companion browser extension runs entirely on the client device. Its components are:

- **Manifest V3 WebExtension** targeting Chrome, Edge, Firefox, and Safari (desktop and, where the browser supports extensions, mobile).
- **On-device OCR** via a WebAssembly build of Tesseract, used to detect section 204F promoter statements on images encountered while browsing.
- **Local perceptual hash** (PDQ) computed on the client; only the 256-bit hash (not the image) is sent to the API.
- **Non-blocking overlay** rendered on images that carry a promoter statement but do not match a registered entry. The overlay never prevents viewing or sharing.
- **User flag channel** accessed via context menu (desktop) or long-press (mobile), with predefined reason codes and an optional note.
- **Privacy stance:** no account required; no browsing history retained; no image bytes transmitted; rate limiting enforced per-device to prevent abuse.

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

The table below summarises approaches other jurisdictions have taken. Most involve content-regulation powers that New Zealand has deliberately not adopted. PIVS is not proposed as an equivalent to any of these measures; it is a lighter, voluntary provenance register that leaves content regulation out of scope.

| Jurisdiction | Approach | Status |
|---|---|---|
| **South Korea** | Ban on election deepfakes within 90 days of polling; up to 7 years' imprisonment | In force (2023) |
| **Singapore** | Prohibition on digitally generated content depicting candidates during elections | In force (2024) |
| **European Union** | AI Act classifies election-influencing AI as high-risk; Digital Services Act requires platforms to label manipulated content | Full enforcement August 2026 |
| **United States** | No federal legislation; 28 states have enacted laws; FCC fines for AI robocalls | Patchwork |
| **Australia** | No binding AI-specific laws; AEC "Stop and Consider" voter education campaign | Voluntary / education-led |
| **Canada** | No AI-specific election legislation; election watchdog rates AI-related risk as "high" | Under review |
| **New Zealand** | Existing promoter statement regime (s204F), ASA and BSA complaints processes; Commission does not regulate advertising content | Proposed addition: voluntary party-authored provenance register (PIVS) |

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
| \$18.7 million allocated in Budget 2025 for election integrity improvements | NZ Budget 2025 |
| \$61.9 million allocated for 2026 election delivery and modernisation | NZ Budget 2025 |

---

## APPENDIX D: Cost Comparison - Acquisition Approaches

| Approach | Estimated Operational Cost | Timeline | Risk |
|---|---|---|---|
| **Transfer of existing system** (recommended) | \$20,000 IP acquisition + \$41,000–\$87,000 hosting and deployment on Catalyst Cloud | 2 months to deployment | Low, system already has basic functionality; NZ data sovereignty assured |
| **Contracted Deployment** | \$100,000–\$150,000 for managed system deployed on Catalyst Cloud | 2 months to deployment with managed updates and security during the election | Low, system already has basic functionality; NZ data sovereignty assured |
| **Bespoke development via government procurement** | \$500,000–\$1,000,000+ | 12–18 months | High, impossible for 2026 election |
| **Commercial SaaS solution** | \$200,000–\$400,000/year | 3–6 months | Medium, data sovereignty concerns with offshore providers; vendor lock-in; ongoing costs |

The transfer approach provides the Commission with full ownership of the source code and infrastructure, avoids vendor lock-in, and ensures data sovereignty through hosting on Catalyst Cloud's 100% New Zealand-based infrastructure under the All-of-Government Cloud Framework Agreement. The operational cost estimate of \$41,000–\$87,000 covers Catalyst Cloud hosting (\$5,000–\$10,200 for 8 months), security audit and penetration testing (\$20,000–\$40,000), and acceptance testing, load testing, accessibility audit, and privacy impact assessment (\$16,000–\$37,000). Image storage for the estimated 2,000–5,000 campaign images across all parties is a negligible cost component at under \$10/month on Catalyst Cloud object storage. Arrangements for intellectual property transfer and/or technical support during the campaign period can be discussed separately with the project team.

---

## APPENDIX E: Privacy Impact Assessment

A draft Privacy Impact Assessment (PIA) has been prepared for the system and is provided as a separate document (*Privacy Impact Assessment: Political Image Verification System*, February 2026). The PIA assesses the system against all 13 Information Privacy Principles under section 22 of the Privacy Act 2020.

**Key findings:**

- **Overall privacy risk: Low.** The system collects minimal personal information (party user accounts only, approximately 50–100 individuals). Public verification is fully anonymous.
- **No personal information is collected from the public.** Verification requires no login, account, or identifying information. Uploaded images are processed in memory and not stored.
- **All personal information is encrypted at rest.** Email addresses use AES-256-GCM encryption; passwords are bcrypt-hashed; IP addresses are SHA-256 hashed in logs (irreversible).
- **No offshore data transfer.** When hosted on Catalyst Cloud, all personal information remains within New Zealand.
- **Recommendations:** The hosting agency should establish a data retention schedule, a documented process for access and correction requests, and consult with the Office of the Privacy Commissioner before deployment.

The full PIA is available for review by the Commission's privacy officer and for consultation with the Office of the Privacy Commissioner as required by the Cabinet Manual.

---

## REFERENCES

Electoral Commission of New Zealand. *Ensuring election integrity for 2026 and the future.* https://elections.nz/media-and-news/2025/ensuring-election-integrity-for-2026-and-the-future/

Electoral Commission of New Zealand. *About election advertising.* https://elections.nz/guidance-and-rules/advertising-and-campaigning/about-election-advertising/

Elections NZ. *2026 General Election.* https://elections.nz/about/about-the-electoral-commission/our-work/2026-general-election/

Department of the Prime Minister and Cabinet. *Strengthening resilience to disinformation in Aotearoa New Zealand.* https://www.dpmc.govt.nz/our-programmes/national-security/strengthening-resilience-disinformation

Ministry of Justice. *Electoral law changes.* https://www.justice.govt.nz/about/news-and-media/news/electoral-law-changes/

Ministry of Business, Innovation and Employment. *New Zealand's Strategy for Artificial Intelligence: Investing with confidence.* July 2025. https://www.mbie.govt.nz/business-and-employment/economic-growth/digital-policy/new-zealands-ai-strategy-investing-with-confidence

DPMC Multi-Stakeholder Group. *Strengthening civil society resilience to mis- and disinformation in Aotearoa New Zealand.* March 2024. https://www.dpmc.govt.nz/publications/strengthening-civil-society-resilience-mis-and-disinformation-aotearoa-new-zealand

Ministry of Justice. *Independent Electoral Review: Final Report.* November 2023. https://www.justice.govt.nz/justice-sector-policy/constitutional-issues-and-human-rights/independent-electoral-review/

International Foundation for Electoral Systems. *The Romanian 2024 Election Annulment.* https://www.ifes.org/publications/romanian-2024-election-annulment-addressing-emerging-threats-electoral-integrity

NPR. *How deepfakes and AI memes affected global elections in 2024.* December 2024. https://www.npr.org/2024/12/21/nx-s1-5220301/deepfakes-memes-artificial-intelligence-elections

Centre for Governance Innovation. *Then and Now: AI Electoral Interference in 2025.* https://www.cigionline.org/articles/then-and-now-how-does-ai-electoral-interference-compare-in-2025/

Harvard Ash Center. *The Apocalypse That Wasn't: AI in 2024 Elections.* https://ash.harvard.edu/articles/the-apocalypse-that-wasnt/

University of Waikato. *Playing politics with AI: Why NZ needs rules on the use of fake images in election campaigns.* https://www.waikato.ac.nz/int/news-events/news/playing-politics-with-ai-why-nz-needs-rules-on-the-use-of-fake-images-in-election-campaigns/

Pew Research Center. *Views of AI Around the World.* October 2025. https://www.pewresearch.org/global/2025/10/15/how-people-around-the-world-view-ai/

Advertising Standards Authority. *Spotlight on General Election Advertising.* https://asa.co.nz/2023/08/09/spotlight-on-general-election-advertising/

Broadcasting Standards Authority. *Election Programmes Code.* https://www.bsa.govt.nz/broadcasting-standards/election-code/

Carnegie Endowment for International Peace. *Can Democracy Survive the Disruptive Power of AI?* December 2024. https://carnegieendowment.org/research/2024/12/can-democracy-survive-the-disruptive-power-of-ai

Brennan Center for Justice. *Gauging the AI Threat to Free and Fair Elections.* March 2025. https://www.brennancenter.org/our-work/analysis-opinion/gauging-ai-threat-free-and-fair-elections

Catalyst Cloud. *Price List.* https://catalystcloud.nz/pricing/price-list/ (Prices effective 1 June 2025.)

Catalyst Cloud. *All-of-Government Cloud Framework Agreement.* https://catalystcloud.nz/customers/public-sector1/

New Zealand Government Procurement. *Catalyst Cloud Framework Agreement.* https://www.procurement.govt.nz/contracts/catalyst-cloud-framework-agreement/

Krewel, M. (Victoria University of Wellington). *Five weeks, 4,000 Facebook posts: social media campaigning in the 2023 election.* November 2023. https://www.wgtn.ac.nz/news/2023/11/five-weeks-4-000-facebook-posts-social-media-campaigning-in-the-2023-election

RNZ. *The campaign for social media supremacy in Election 2023.* October 2023. https://www.rnz.co.nz/news/political/500672/the-campaign-for-social-media-supremacy-in-election-2023-who-the-parties-targeted-and-their-key-messages

The Spinoff. *Who spent most on online ads this election?* October 2023. https://thespinoff.co.nz/politics/20-10-2023/who-spent-most-on-online-ads-this-election

Electoral Commission of New Zealand. *2023 General Election Party Expenses.* https://elections.nz/democracy-in-nz/historical-events/2023-general-election/party-expenses/

NZ Herald. *Election 2023: Who spent most on online advertising?* October 2023. https://www.nzherald.co.nz/business/election-2023-who-spent-most-on-online-advertising-act-tops-parties-in-meta-google-data/3GCHJGIJNRGLNKTGNGFTPUBIIQ/

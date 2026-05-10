# ISO and complementary standards applicable to PIVS

Prepared for the Chief Electoral Officer and the Office of the Privacy Commissioner. This document lists the international and New Zealand standards the Electoral Commission can reasonably use to evaluate adopting the Political Image Verification System (PIVS) for the 2026 General Election. The companion document [doc/security-privacy-assessment.md](security-privacy-assessment.md) maps the current codebase against the same standards.

The numbered editions in this document are current as of early 2026 to the best of our knowledge. ISO and NIST publish revisions on rolling cycles. The Commission's assessors should confirm the latest edition before formal citation.

## 1. Software lifecycle and engineering

### ISO/IEC/IEEE 12207:2017 — Systems and software engineering — Software life cycle processes

Defines a common framework for software life cycle processes from acquisition through development to disposal. For PIVS the Commission can use it to confirm that the provenance register, public verification API, browser extension, and admin review queue have documented life cycle processes covering requirements, architecture, integration, verification, deployment, and decommissioning, rather than being treated as an ad-hoc project.

### ISO/IEC/IEEE 90003:2018 — Application of ISO 9001:2015 to computer software

Translates ISO 9001 quality management into software-specific guidance. Relevant if the operator or contracted supplier of PIVS claims an ISO 9001 quality system, or if the Commission wants assurance that change management, defect handling, and supplier management wrap around the engineering processes in 12207.

## 2. Software quality model

### ISO/IEC 25010:2011 (revised 2023) — SQuaRE product quality model

Defines the product quality model with eight characteristics (functional suitability, performance efficiency, compatibility, usability, reliability, security, maintainability, portability) and a separate quality-in-use model. The 2023 revision split product quality from quality-in-use into ISO/IEC 25019. PIVS can be graded against the 25010 model to give the Commission a structured rubric covering reliability of the API, usability of the extension, and maintainability of the admin queue.

### ISO/IEC 25040:2011 — SQuaRE evaluation process

The procedural companion to 25010. Sets out how to plan, execute, and conclude a product quality evaluation. This is what the Commission's assessors would actually follow when grading PIVS. The wider SQuaRE family also covers data quality (25012), measurement (25023), and ready-to-use product evaluation (25051).

## 3. Software testing

### ISO/IEC/IEEE 29119 — Software testing series

Multi-part series covering concepts (Part 1), test processes (Part 2), test documentation (Part 3), test techniques (Part 4), keyword-driven testing (Part 5), and recent additions for agile and DevOps (Part 6). The Commission can use Parts 1 to 4 to confirm that PIVS has a defined test strategy, traceable test cases, and a defensible mix of techniques (boundary value analysis, equivalence partitioning, security testing, performance testing, accessibility testing) across the API, extension, and admin queue.

## 4. Information security management

### ISO/IEC 27001:2022 — Information security management systems requirements

The certifiable standard for an Information Security Management System (ISMS). Annex A lists 93 controls organised into four themes (organisational, people, physical, technological). Certification of the operator gives the Commission baseline assurance that information security is managed systematically rather than incidentally. This is the right anchor for an electoral system whose provenance evidence may appear in judicial review or election petitions.

### ISO/IEC 27002:2022 — Information security controls

Not certifiable on its own. Provides the implementation guidance behind the 27001 Annex A controls. The Commission should expect a supplier to map their controls to 27002 when justifying their 27001 Statement of Applicability.

### ISO/IEC 27017:2015 — Cloud-specific controls

Extends 27002 with cloud-specific guidance for both customer and provider. Directly relevant to PIVS because the API, the bloom-filter snapshot endpoint, and the admin queue are intended for cloud hosting. Defines shared-responsibility expectations the Commission should require in procurement.

### ISO/IEC 27018:2019 — Protection of PII in public cloud

Companion to 27017 addressing PII processing in public cloud. Applies to PIVS because submitter, complainant, and operator data is processed in cloud infrastructure. Together with 27701 (privacy management, below) it forms the privacy overlay on the 27001 baseline.

## 5. Cryptographic module and algorithm references

### ISO/IEC 19790:2012 — Security requirements for cryptographic modules

Specifies four security levels for cryptographic modules covering design, implementation, physical security, key management, self-tests, and operational requirements. For PIVS, the master key used to wrap per-asset data encryption keys, and any signing keys, should be held in a module assessed at an appropriate level (typically Level 2 for software with a hardware root of trust, Level 3 for dedicated HSM use).

### ISO/IEC 18033 series — Encryption algorithms

Catalogues approved algorithms across Parts 1 to 7. Companion series cover digital signatures (14888, 9796), hash functions (10118), and key management (11770). PIVS should draw only from these catalogues, not bespoke schemes.

### FIPS 140-3 — NIST cryptographic module standard

Incorporates ISO/IEC 19790 by reference. In practice, commercially available HSMs and cryptographic libraries seek FIPS 140-3 validation. Treat as interchangeable with 19790 for procurement assurance.

## 6. Privacy management

### ISO/IEC 29100:2011 — Privacy framework

Establishes a common privacy vocabulary, an actor model (PII principal, controller, processor), and eleven privacy principles. Useful as the shared terminology for the Privacy Impact Assessment.

### ISO/IEC 27701:2019 — Privacy information management system

Extends 27001 and 27002 with controls for both PII controllers and PII processors. Certifiable as an extension to a 27001 certification. This is the most direct international standard for demonstrating that personal information held by PIVS is governed under the same management system as security. Pairs with the New Zealand Privacy Act 2020 Information Privacy Principles, which are the binding requirement in our jurisdiction.

## 7. Application security

### ISO/IEC 27034 series — Application security

Multi-part series covering an overview (Part 1), organisational normative framework (Part 2), application security management (Part 3), validation (Part 5), and assurance prediction (Part 7). Adoption in practice is limited.

### OWASP Application Security Verification Standard (ASVS) v4.0.3

The de facto reference for technical application security in government procurement, used by the NCSC and CERT NZ. Three levels of verifiable requirements (L1 opportunistic, L2 standard, L3 advanced). For PIVS, ASVS L2 across the verify API and admin queue, with selected L3 controls on cryptography and access control given the political sensitivity, is a reasonable target. The OWASP API Security Top 10 and OWASP Top 10 are complementary references.

## 8. Risk management

### ISO 31000:2018 — Risk management guidelines

Generic, principles-based, not certifiable. Provides a common reference for managing electoral, reputational, operational, legal, and technical risks alongside each other. ISO/IEC 31010 catalogues specific risk assessment techniques.

### ISO/IEC 27005:2022 — Information security risk management

Information-security-specific risk management aligned with both 27001 and 31000. The Commission should expect the supplier's risk register to follow this when documenting threats (signing-key compromise, denial of service against the verify API, insider misuse in the admin queue, deepfake-driven misattribution) and mitigations.

## 9. Identity and authentication assurance

### ISO/IEC 29115:2013 — Entity authentication assurance framework

Defines four Levels of Assurance (LoA 1 to 4) for entity authentication. PIVS roles map approximately to: public verification (no LoA), submitter (LoA 2), party admin (LoA 3 with MFA), Electoral Commission operator (LoA 3 or 4 with hardware authenticator).

### NIST SP 800-63-3, 800-63-4 (in late draft as of 2025) — Digital Identity Guidelines

De facto international reference. Splits assurance into IAL (identity proofing), AAL (authentication), and FAL (federation) levels. New Zealand RealMe and DIA identity-assurance frameworks draw on the same model. More granular than 29115.

## 10. Accessibility

### ISO 30071-1:2019 — Code of practice for accessible ICT

A code of practice for embedding accessibility into ICT design and procurement, referencing WCAG for the technical criteria. Useful for assessing whether the supplier has an accessibility process. The actual conformance bar will be WCAG.

### WCAG 2.1 Level AA (W3C Recommendation)

The de facto accessibility bar for New Zealand government digital services under the NZ Government Web Accessibility Standard 1.1 and Web Usability Standard 1.3. WCAG 2.2 was published in 2023 and is being progressively adopted. ISO/IEC 40500 republishes WCAG 2.0 as an ISO standard. There is no ISO publication of 2.1 or 2.2 yet.

## 11. Records management

### ISO 15489-1:2016 — Records management concepts and principles

Defines the principles for managing records as authoritative evidence of activities. The provenance register is fundamentally a records system, and verification decisions may be retained as evidence for petitions or judicial review. Companion references include ISO 16175 (electronic office environments), ISO 23081 (records metadata), and ISO 14641 (electronic archiving). In New Zealand the Public Records Act 2005 and the Chief Archivist's mandatory standards (Information and Records Management Standard, Disposal Standard) sit on top.

## 12. New Zealand complementary frameworks

### New Zealand Information Security Manual (NZISM)

Published by the GCSB / NCSC. The mandatory baseline for protecting government information systems. Maps in many places to ISO/IEC 27002 controls but is more prescriptive. If PIVS handles official information or is operated by or for the Crown, NZISM applies and will often be the binding control set rather than 27002.

### Privacy Act 2020 and the 13 Information Privacy Principles

The binding privacy law in New Zealand, enforced by the Office of the Privacy Commissioner. Covers collection, storage, access, correction, accuracy, retention, use, disclosure, cross-border disclosure, and unique identifiers. Imposes a mandatory notifiable privacy breach regime under sections 114 to 120 of the Act. The companion assessment document scores PIVS against each of the 13 IPPs.

### OPC Privacy Impact Assessment toolkit

The Office of the Privacy Commissioner publishes PIA guidance and a toolkit. A completed PIA covering submitter, complainant, operator, and end-user data flows is expected before adoption.

### All-of-Government Cloud Risk Discovery and Assessment

Administered by the Government Chief Digital Officer at the Department of Internal Affairs. If PIVS is hosted in cloud infrastructure, a completed cloud risk assessment is required. The Commission should align with the current iteration of the framework.

### Digital.govt.nz Service Design Standard

GCDO-published standards covering service design, accessibility, and usability. Relevant for the public-facing verification UI, the browser extension, and any public dashboard.

### Electoral Act 1993 and Electoral Regulations

The statutory framework the Commission operates within. Section 204F (promoter statements) is the legal anchor for the misattribution problem PIVS addresses. Any adoption must be consistent with the Commission's statutory functions and with the rules on election advertising, broadcasting, and electoral expenses.

### Public Records Act 2005

Applies to any electoral records held by the Crown. Retention schedules need to be approved by the Chief Archivist.

## 13. Election-specific resources

### Council of Europe Recommendation CM/Rec(2017)5 on standards for e-voting

The principal international recommendation on electronic voting. PIVS is not an e-voting system, but the recommendation's principles on transparency, verifiability, secrecy, and accountability translate well to electoral-integrity tooling, especially the verifiability and transparency design of the public verify API and the provenance register.

### NIST election security guidance

The Voluntary Voting System Guidelines (VVSG) 2.0 (adopted by the US Election Assistance Commission in 2021) are voting-system specific but include useful software-engineering requirements. NIST IR 8310 covers cybersecurity risk for election infrastructure. These are analogues rather than direct fits for image-provenance verification.

### Content provenance technical references

The C2PA (Coalition for Content Provenance and Authenticity) technical specification is the dominant industry reference for cryptographically signed image provenance. ISO/IEC JTC 1/SC 29 has begun work on JPEG Trust (ISO/IEC 21617, with parts in development as of 2025). Both are emerging rather than established but are directly relevant to PIVS's core function and are likely to be cited by the supplier.

## How the Commission can use this list

The shortest defensible adoption path runs through six standards:

1. ISO/IEC 27001 (security management) plus 27017 and 27018 overlays (cloud and PII in cloud).
2. ISO/IEC 27701 (privacy management) over the top of 27001.
3. ISO/IEC 25010 plus 25040 (quality model and evaluation process).
4. ISO/IEC/IEEE 29119 Parts 1 to 4 (testing).
5. OWASP ASVS v4.0.3 (application security verification).
6. NZ Privacy Act 2020 IPPs plus the OPC PIA toolkit.

WCAG 2.1 AA and ISO 30071-1 are required for accessibility. NZISM is required if Crown information is involved. ISO 15489 is required for the records retention story. NIST SP 800-63 sets the authentication assurance bar.

The actual gap assessment against this list is in [doc/security-privacy-assessment.md](security-privacy-assessment.md).

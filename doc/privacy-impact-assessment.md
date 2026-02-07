# PRIVACY IMPACT ASSESSMENT

## Political Image Verification System (PIVS)

**Prepared by:** Political Image Verification Project Team

**Date:** February 2026

**Version:** 1.0

**Classification:** Unclassified

---

## 1. PROJECT DESCRIPTION

### 1.1 Project name

Political Image Verification System (PIVS)

### 1.2 Project purpose

The system enables registered New Zealand political parties to authenticate their campaign imagery and provides the public with a mechanism to verify whether political images are genuine. It addresses the threat to public trust posed by AI-generated political content by creating a verifiable registry of authentic campaign images.

### 1.3 Project scope

The system comprises:

- A **party submission portal** where authorised political party representatives register campaign images through authenticated accounts with multi-factor authentication.
- A **public verification portal** where any member of the public can upload a political image or scan a QR code to check whether it has been registered by a political party.
- A **verification API** enabling media organisations and platform operators to integrate verification into their own systems.
- **Promoter statement tools** that help parties add Electoral Act-compliant promoter statements to campaign imagery, verify existing statements via OCR, and process images in batch.

### 1.4 Responsible agency

The Electoral Commission of New Zealand (or hosting agency as determined).

### 1.5 Key contacts

- Project Team: Political Image Verification Project Team
- Privacy contact: [To be designated by the responsible agency]

---

## 2. INFORMATION FLOWS

### 2.1 What personal information is collected?

The system collects the following categories of personal information:

| Category | Data Elements | From Whom | Purpose |
|---|---|---|---|
| **Party user accounts** | Username, email address, hashed password, TOTP MFA secret | Authorised party representatives | Authentication and authorisation for image submission |
| **Campaign images** | Images submitted by party users (which may incidentally depict individuals) | Authorised party representatives | Image registration, hash computation, and verification |
| **System logs** | Hashed IP addresses, timestamps, action types | Party users and public users (anonymous) | System monitoring, security, and rate limiting |

### 2.2 What personal information is NOT collected?

The following personal information is explicitly **not** collected:

- **Public verification users:** No login, account, name, email, IP address, or any identifying information is collected from members of the public performing verification. Verification is fully anonymous.
- **Uploaded verification images:** Images uploaded by the public for verification are processed in memory only. They are **not stored**. Only their hashes are computed temporarily and compared against the registry.
- **Browsing or tracking data:** No cookies, analytics, fingerprinting, or tracking mechanisms are used on the public verification portal.

### 2.3 How does personal information flow through the system?

**Party user registration flow:**
1. An administrator creates a user account, providing a username, email, and initial password.
2. The email address is encrypted using AES-256-GCM envelope encryption before storage.
3. The password is hashed using bcrypt (one-way; the original password is never stored).
4. If MFA is enabled, the TOTP secret is encrypted before storage.
5. On login, the system verifies credentials and issues a time-limited JWT token (60-minute expiry).

**Image submission flow:**
1. An authenticated party user uploads an image.
2. The system computes SHA-256, PDQ, and pHash hashes of the image.
3. The original image is encrypted using AES-256-GCM with a unique data encryption key (DEK), which is itself encrypted by a key encryption key (KEK).
4. The encrypted image and hashes are stored in the database and object storage.
5. Optional: A verification badge, QR code, and/or promoter statement overlay are generated and stored as separate encrypted artifacts.

**Public verification flow:**
1. A member of the public uploads an image or enters a verification ID.
2. The system computes hashes of the uploaded image **in memory** (the image is not stored).
3. The hashes are compared against the registered hash index.
4. A verification result (match/no match, party name, confidence) is returned.
5. The uploaded image is discarded from memory. No record of the query is retained that identifies the user.

**System logging flow:**
1. All server logs record a one-way SHA-256 hash of the client IP address (not the IP itself).
2. Log entries include timestamps and action types but no personally identifiable information.

---

## 3. ASSESSMENT AGAINST INFORMATION PRIVACY PRINCIPLES

### IPP 1 — Purpose for collection of personal information

**Principle:** Personal information shall not be collected unless the collection is for a lawful purpose connected with a function or activity of the agency, and the collection is necessary for that purpose.

**Assessment:**

| Information | Purpose | Lawful basis | Necessary? |
|---|---|---|---|
| Party user email | Account management, password reset, email processing verification | Connected to the agency's function of administering the verification system | Yes — required for account recovery and anti-spoofing verification |
| Party user password | Authentication | Connected to the agency's function of securing the system against unauthorised access | Yes — without authentication, any person could register images as a political party |
| MFA secret | Two-factor authentication | Connected to the agency's function of securing party accounts | Yes — mandatory for admin accounts to prevent unauthorised party impersonation |
| System log hashes | Security monitoring, rate limiting, incident response | Connected to the agency's function of maintaining system integrity | Yes — hashed IP addresses are the minimum necessary for security monitoring; raw IPs are not retained |

**Risk:** Low. All personal information collected is directly necessary for the system's core functions. No personal information is collected from public verification users.

**Mitigation:** The system does not collect any personal information that is not strictly necessary. Public verification is fully anonymous.

### IPP 2 — Source of personal information

**Principle:** Where an agency collects personal information, the information shall be collected directly from the individual concerned.

**Assessment:** All personal information is collected directly from the individual:

- Party user accounts are created with information provided directly by the user (or by an administrator on behalf of the user during onboarding, with the user's knowledge).
- No personal information is collected from third parties.
- No personal information is collected about members of the public performing verification.

**Risk:** Low. No collection from third-party sources.

### IPP 3 — Collection of information from subject

**Principle:** Where an agency collects personal information directly from the individual, the agency shall take reasonable steps to ensure the individual is aware of specified matters.

**Assessment:** Party users are informed at account creation of:

- The fact that their email address and username are collected.
- The purpose: authentication and authorisation for the image verification system.
- The intended recipients: system administrators within the hosting agency.
- The right to access and correct their information.
- Whether provision is voluntary or mandatory: use of the system is voluntary for parties; however, an account is required to submit images.

Public verification users are informed (via the portal interface) that:

- No personal information is collected during verification.
- Uploaded images are not stored.
- Verification is anonymous.

**Risk:** Low. Clear notice is provided at the point of collection.

### IPP 4 — Manner of collection

**Principle:** Personal information shall not be collected by an agency by unlawful means, or by means that are unfair or unreasonably intrusive.

**Assessment:**

- All information is collected through standard web forms with clear labels and purpose statements.
- No deceptive practices, hidden fields, or dark patterns are used.
- No information is collected through surveillance, scraping, or monitoring.
- IP addresses in server logs are immediately hashed (one-way) — the raw IP is never stored, which is the least intrusive approach to necessary security logging.
- No information is collected from children or vulnerable persons (the system's users are authorised party representatives).

**Risk:** Low. Collection methods are standard, transparent, and minimally intrusive.

### IPP 5 — Storage and security of personal information

**Principle:** An agency that holds personal information shall ensure that the information is protected by reasonable security safeguards against loss, access, use, modification, or disclosure, or other misuse.

**Assessment:** The system implements comprehensive security measures:

| Measure | Detail |
|---|---|
| **Encryption at rest** | All stored images encrypted with AES-256-GCM using envelope encryption (unique DEK per image, encrypted by KEK). Party user email addresses encrypted at rest. |
| **Password security** | Passwords hashed with bcrypt (one-way; originals never stored). |
| **MFA secrets** | TOTP secrets encrypted before storage. |
| **Transport security** | TLS for all connections. |
| **Access control** | JWT-based authentication with 60-minute token expiry. Role-based access control (admin, submitter, viewer). TOTP MFA mandatory for administrators. |
| **IP address protection** | IP addresses SHA-256 hashed in logs (irreversible). |
| **Rate limiting** | Nginx reverse proxy enforces 30 verifications/minute, 10 submissions/minute. |
| **Security headers** | X-Frame-Options, Content-Security-Policy, X-Content-Type-Options headers applied. |
| **Network isolation** | Database not directly exposed to the internet; accessible only through the application layer. |
| **Containerisation** | Application runs as a non-root user in Docker containers. |

**Risk:** Low. Security measures exceed standard practice for a system of this nature. Encryption at rest, MFA, and hashed IP logging provide strong protection.

**Recommendation:** An independent security audit and penetration test should be conducted before production deployment (included in the deployment plan).

### IPP 6 — Access to personal information

**Principle:** Where an agency holds personal information in such a way that it can readily be retrieved, the individual concerned shall be entitled to obtain confirmation of whether the agency holds such information, and to have access to that information.

**Assessment:**

- **Party users** can view their own account information (username, role, MFA status) through the party portal.
- **Party administrators** can view user accounts within their party.
- **Email addresses** are encrypted at rest and can be decrypted by authorised system administrators for access requests.
- **Public verification users** have no personal information held by the system, so no access request mechanism is needed.
- A formal process for handling access requests under Part 4 of the Privacy Act 2020 should be established by the hosting agency.

**Risk:** Low. The volume of personal information held is small (party user accounts only), and technical mechanisms exist to retrieve it.

**Recommendation:** The hosting agency should establish a documented process for responding to information access requests.

### IPP 7 — Correction of personal information

**Principle:** Where an agency holds personal information, the individual concerned shall be entitled to request correction of the information.

**Assessment:**

- Party users can update their password through the system.
- Party administrators can update user details for their party.
- For corrections to encrypted fields (email), a system administrator can process the request.
- A formal correction request process should be established by the hosting agency.

**Risk:** Low.

### IPP 8 — Accuracy of personal information

**Principle:** An agency that holds personal information shall not use or disclose that information without taking reasonable steps to check that the information is accurate, up to date, complete, relevant, and not misleading.

**Assessment:**

- The personal information held (usernames, emails, passwords) is provided directly by the individuals and is used solely for authentication.
- Email addresses are verified through the email processing anti-spoofing mechanism (verification email sent to registered address).
- The system does not make decisions about individuals based on the personal information held.
- Campaign images registered in the system are attributed to the party that registered them, not to individuals.

**Risk:** Low. The limited scope of personal information and its use for authentication only minimises accuracy concerns.

### IPP 9 — Retention of personal information

**Principle:** An agency that holds personal information shall not keep that information for longer than is required for the purposes for which the information may lawfully be used.

**Assessment:**

- **Party user accounts:** Retained for the duration of the election cycle and a reasonable post-election period for audit and dispute resolution purposes. The hosting agency should establish a retention schedule.
- **Registered images and hashes:** Retained for the election cycle and post-election period. Images may be retained longer for historical record purposes (public interest in the integrity of the electoral record).
- **System logs:** Contain only hashed IP addresses and timestamps. Should be retained for a defined period (recommended: 12 months post-election) and then deleted.
- **JWT tokens:** Expire after 60 minutes and are not stored server-side.

**Risk:** Low, provided a retention schedule is established.

**Recommendation:** The hosting agency should establish a data retention schedule specifying:
- Party user account data: deleted or anonymised within 6 months post-election unless needed for audit.
- System logs: deleted within 12 months post-election.
- Registered images: retained for the electoral record (public interest basis) or deleted per agency policy.

### IPP 10 — Limits on use of personal information

**Principle:** An agency that holds personal information obtained in connection with one purpose shall not use the information for any other purpose.

**Assessment:**

- Party user account information (email, username) is used **only** for authentication, authorisation, and system communications (password reset, email processing verification).
- System logs (hashed IPs) are used **only** for security monitoring and rate limiting.
- No personal information is used for marketing, analytics, profiling, or any secondary purpose.
- No personal information is shared with third parties for any purpose.

**Risk:** Low. The system architecture enforces purpose limitation by design — personal information is technically isolated from the verification function.

### IPP 11 — Limits on disclosure of personal information

**Principle:** An agency that holds personal information shall not disclose the information to another agency or person unless permitted.

**Assessment:**

- **Party user information** is not disclosed to any third party. Email addresses are encrypted and accessible only to system administrators.
- **Public verification results** disclose only whether an image was registered and by which party. No personal information about the submitter is included.
- **Registered images** are not disclosed through the verification process. Only hash comparisons are performed; the stored images themselves are never exposed to public users.
- **System logs** contain only hashed IP addresses (irreversible) and would not constitute disclosure of personal information even if shared.

Disclosures that may be required:
- In response to a lawful request by a law enforcement agency (section 22, IPP 11(e)).
- In response to an access request by the individual concerned (IPP 6).

**Risk:** Low. The system architecture prevents unauthorised disclosure by design.

### IPP 12 — Disclosure of personal information outside New Zealand

**Principle:** An agency shall not disclose personal information to a foreign person or entity unless adequate protections are in place.

**Assessment:**

- **Recommended hosting:** Catalyst Cloud, the only All-of-Government Cloud Framework provider with 100% New Zealand-based infrastructure. All three data centres are located in New Zealand.
- **No offshore transfer:** When hosted on Catalyst Cloud, no personal information leaves New Zealand. All processing, storage, and backup occurs within New Zealand data centres, regulated by New Zealand law.
- **No third-party services:** The system does not use offshore analytics, CDN services that would process personal data, or cloud services outside New Zealand for any function involving personal information.

**Risk:** Nil (when hosted on Catalyst Cloud). No personal information is disclosed outside New Zealand.

**Recommendation:** Any future change of hosting provider must be assessed for IPP 12 compliance before implementation.

### IPP 13 — Unique identifiers

**Principle:** An agency shall not assign a unique identifier to an individual unless the assignment is necessary for the agency's functions. An agency shall not require an individual to disclose a unique identifier assigned by another agency.

**Assessment:**

- **Party user IDs:** Each party user account is assigned a UUID (universally unique identifier) as a database primary key. This is necessary for the authentication and authorisation system to function and does not correspond to any external identifier.
- **No external identifiers required:** The system does not require users to provide government-issued identifiers (IRD numbers, passport numbers, driver licence numbers, etc.).
- **No identifiers for public users:** Members of the public performing verification are not assigned any identifier.
- **Image verification IDs:** Each registered image receives a unique verification ID. This identifies the image, not an individual.

**Risk:** Low. Unique identifiers are used only for internal system functions and are not cross-referenced with external identifiers.

---

## 4. RISK SUMMARY

| Privacy Principle | Risk Level | Key Finding |
|---|---|---|
| IPP 1 — Purpose | Low | All collection is necessary and connected to system functions |
| IPP 2 — Source | Low | All information collected directly from the individual |
| IPP 3 — Notice | Low | Clear notice provided at collection |
| IPP 4 — Manner | Low | Standard, transparent, minimally intrusive collection |
| IPP 5 — Security | Low | Comprehensive encryption, MFA, hashed IPs, role-based access |
| IPP 6 — Access | Low | Party users can access own information; formal process recommended |
| IPP 7 — Correction | Low | Mechanisms exist; formal process recommended |
| IPP 8 — Accuracy | Low | Limited information used only for authentication |
| IPP 9 — Retention | Low | Retention schedule to be established by hosting agency |
| IPP 10 — Use | Low | Purpose limitation enforced by system architecture |
| IPP 11 — Disclosure | Low | No third-party disclosure; architecture prevents exposure |
| IPP 12 — Overseas | Nil | 100% NZ-hosted on Catalyst Cloud; no offshore transfer |
| IPP 13 — Identifiers | Low | Internal UUIDs only; no external identifiers required |

**Overall privacy risk: LOW**

The system is designed with a privacy-first architecture. The most significant privacy design feature is that **public verification is fully anonymous** — no personal information is collected, stored, or processed from members of the public. The personal information held by the system is limited to party user accounts (approximately 50–100 individuals across all political parties), all of which is encrypted at rest.

---

## 5. RECOMMENDATIONS AND ACTION ITEMS

| # | Recommendation | Responsible | Priority |
|---|---|---|---|
| 1 | Establish a data retention schedule for party user accounts, system logs, and registered images | Hosting agency | High — before launch |
| 2 | Establish a documented process for handling access and correction requests under the Privacy Act 2020 | Hosting agency | High — before launch |
| 3 | Conduct an independent security audit and penetration test before production deployment | Hosting agency | High — before launch |
| 4 | Ensure privacy notice text is displayed on the party user registration and login pages | Project team | Medium — during testing |
| 5 | Ensure the public verification portal includes a clear statement that no personal information is collected and uploaded images are not stored | Project team | Medium — during testing |
| 6 | Review this PIA if the system scope changes (e.g., new data collection, change of hosting provider, integration with third-party services) | Hosting agency | Ongoing |
| 7 | Consult with the Office of the Privacy Commissioner if the system is to be operated by a government agency | Hosting agency | Medium — before launch |

---

## 6. PRIVACY BY DESIGN FEATURES

The system incorporates the following privacy-by-design measures:

1. **Anonymous public verification:** No account, login, or personal information required to verify images.
2. **Encryption at rest:** AES-256-GCM envelope encryption for all stored images; encrypted email addresses and MFA secrets.
3. **Hashed IP addresses:** Server logs contain only irreversible SHA-256 hashes of IP addresses, not the addresses themselves.
4. **Minimal data collection:** Only the information strictly necessary for authentication and system functions is collected.
5. **No tracking:** No cookies, analytics, fingerprinting, or user tracking on the public portal.
6. **In-memory processing:** Images uploaded for verification are processed in memory and immediately discarded; they are never written to disk or database.
7. **Data sovereignty:** Hosted on Catalyst Cloud (100% NZ infrastructure), ensuring all personal information remains under New Zealand law.
8. **Role-based access:** Party users can only access their own party's data. Cross-party access is prevented by the authorisation model.
9. **Time-limited tokens:** JWT authentication tokens expire after 60 minutes.
10. **MFA enforcement:** Mandatory TOTP multi-factor authentication for party administrator accounts.

---

## 7. COMPLIANCE SUMMARY

| Requirement | Status |
|---|---|
| Privacy Act 2020 — Information Privacy Principles (section 22) | Compliant (assessed above) |
| Privacy Act 2020 — Notifiable privacy breaches (Part 6) | Hosting agency to establish breach notification process |
| Cabinet Manual — PIA requirement for government proposals | This PIA satisfies the requirement |
| NZISM — NZ Information Security Manual | Security audit recommended before deployment |
| Te Tiriti o Waitangi considerations | The system benefits all New Zealanders equally. Maori and Pacific communities particularly benefit from protection against culturally offensive fabricated political imagery. The system does not collect or process ethnicity data. |

---

## 8. APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Project Lead | | | |
| Privacy Officer (hosting agency) | | | |
| Chief Information Security Officer | | | |

---

## REFERENCES

1. Privacy Act 2020, section 22 — Information privacy principles. https://www.legislation.govt.nz/act/public/2020/0031/latest/LMS23342.html

2. Office of the Privacy Commissioner. *Privacy Impact Assessments.* https://www.privacy.org.nz/responsibilities/privacy-impact-assessments/

3. Office of the Privacy Commissioner. *Privacy Principles.* https://www.privacy.org.nz/privacy-act-2020/privacy-principles/

4. Office of the Privacy Commissioner. *PIA Toolkit: How to do a PIA.* https://www.privacy.org.nz/assets/New-order/Resources-/Publications/Guidance-resources/PIA/2024-PIA-files/PIA-Toolkit-How-to-do-a-PIA_FINAL.pdf

5. New Zealand Government. *Assess project privacy risk.* https://www.digital.govt.nz/standards-and-guidance/privacy-security-and-risk/privacy/assess-privacy-risk/assess-project-privacy-risk/

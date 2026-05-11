"""Risk classification for verification results.

Combines the result of an image hash lookup with an OCR-based promoter
statement cross-check across all registered parties and assigns a
single ``RiskCategory`` plus a human-readable explanation and a
suggested action for the user.

The classifier deliberately does NOT make any judgement about whether
an image is "fake". It reports what the system has and has not been
able to verify, and where the signals point. The Commission, the
parties, and existing bodies such as the Advertising Standards
Authority remain the bodies that make content judgements.

The decision table (see classify()) is the single source of truth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


# Distance at which a perceptual match is still considered "the same
# image, slightly recompressed/resized" rather than "potentially
# modified registered material". Below this is treated as a clean
# match; at or above this is flagged with risk_level=low.
PDQ_CLEAN_MATCH_MAX = 15

# Heuristic regex for "this text looks like a section 204F promoter
# statement". The canonical NZ phrasing is "Authorised by <name>,
# <address>" so the pattern is anchored on that. We tolerate common
# OCR drift on the trailing "ed" (eg. "Authoris3d", "Authorisecl"),
# both NZ and US spellings, the abbreviation "Auth'd", and the
# alternative verbs "Promoted by" / "Published by".
_PROMOTER_TOKENS = re.compile(
    r"\b("
    r"author[ie](?:[s]|z)\w{0,4}\s+by"   # authorised by / authorized by / authorize by / authorising by
    r"|auth[\'`]?d\s+by"                  # auth'd by / authd by
    r"|promoted\s+by"
    r"|published\s+by"
    r")\b",
    re.IGNORECASE,
)


class RiskLevel(str, Enum):
    """Coarse severity for UI rendering and downstream routing."""

    OK = "ok"
    INFO = "info"
    LOW = "low"
    WARN = "warn"
    HIGH = "high"


class RiskCategory(str, Enum):
    """Machine-readable category of the verification outcome."""

    # Image is in the register.
    REGISTERED_EXACT = "registered_exact"
    REGISTERED_PERCEPTUAL = "registered_perceptual"
    REGISTERED_POSSIBLY_MODIFIED = "registered_possibly_modified"

    # Image is NOT in the register.
    UNREGISTERED_NO_PROMOTER = "unregistered_no_promoter"
    UNREGISTERED_UNKNOWN_PROMOTER = "unregistered_unknown_promoter"
    UNREGISTERED_ATTRIBUTING_KNOWN_PARTY = "unregistered_attributing_known_party"


class SuggestedAction(str, Enum):
    """A short code the UI can map to a button or link."""

    NONE = "none"
    REPORT_POSSIBLY_MODIFIED = "report_possibly_modified"
    REPORT_UNREGISTERED_ELECTION_MATERIAL = "report_unregistered_election_material"
    REPORT_UNKNOWN_PROMOTER = "report_unknown_promoter"
    REPORT_FALSE_ATTRIBUTION = "report_false_attribution"


@dataclass
class RiskAssessment:
    level: RiskLevel
    category: RiskCategory
    explanation: str
    suggested_action: SuggestedAction
    # The party the promoter statement appeared to attribute the
    # image to, if any. Useful for downstream "this image claims to
    # be from X" displays.
    attributed_party_name: str | None = None
    attributed_party_id: str | None = None
    # OCR-derived signals so the UI can show the working.
    promoter_text_present: bool = False
    promoter_pattern_matched: bool = False

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "category": self.category.value,
            "explanation": self.explanation,
            "suggested_action": self.suggested_action.value,
            "attributed_party_name": self.attributed_party_name,
            "attributed_party_id": self.attributed_party_id,
            "promoter_text_present": self.promoter_text_present,
            "promoter_pattern_matched": self.promoter_pattern_matched,
        }


def looks_like_promoter_statement(extracted_text: str | None) -> bool:
    """Return True if OCR text contains a section 204F-style marker."""
    if not extracted_text:
        return False
    return bool(_PROMOTER_TOKENS.search(extracted_text))


def classify(
    *,
    image_match: bool,
    match_type: str,
    pdq_distance: int | None,
    ocr_result: dict | None,
) -> RiskAssessment:
    """Combine the image-hash result and the OCR cross-check.

    Args:
        image_match: True if the hash matched an asset in the register.
        match_type: "exact", "perceptual", or "none".
        pdq_distance: PDQ Hamming distance for perceptual matches,
            None otherwise.
        ocr_result: dict returned by find_promoter_across_parties,
            or None if OCR was not run. Recognised keys:
                found            bool, True if the OCR text matched a
                                 party's registered promoter statement
                                 above the configured threshold.
                party_id         str, the matching party id when found.
                party_name       str, the matching party name when found.
                extracted_text   str, raw OCR text (may be empty).
    """
    ocr_result = ocr_result or {}
    extracted_text = ocr_result.get("extracted_text") or ""
    matched_party_id = ocr_result.get("party_id")
    matched_party_name = ocr_result.get("party_name")
    ocr_found = bool(ocr_result.get("found"))
    pattern_match = looks_like_promoter_statement(extracted_text)

    # --- 1. Image is registered ----------------------------------------
    if image_match and match_type == "exact":
        return RiskAssessment(
            level=RiskLevel.OK,
            category=RiskCategory.REGISTERED_EXACT,
            explanation=(
                "This image exactly matches an image registered with PIVS "
                "by a political party."
            ),
            suggested_action=SuggestedAction.NONE,
            promoter_text_present=bool(extracted_text),
            promoter_pattern_matched=pattern_match,
        )

    if image_match and match_type == "perceptual":
        dist = pdq_distance if pdq_distance is not None else 0
        if dist <= PDQ_CLEAN_MATCH_MAX:
            return RiskAssessment(
                level=RiskLevel.OK,
                category=RiskCategory.REGISTERED_PERCEPTUAL,
                explanation=(
                    "This image matches a registered image, allowing for "
                    "normal variation from social-media recompression, "
                    "resizing, or an added verification badge."
                ),
                suggested_action=SuggestedAction.NONE,
                promoter_text_present=bool(extracted_text),
                promoter_pattern_matched=pattern_match,
            )
        return RiskAssessment(
            level=RiskLevel.LOW,
            category=RiskCategory.REGISTERED_POSSIBLY_MODIFIED,
            explanation=(
                "This image is similar to a registered image but not "
                "identical. Differences are within the matching threshold, "
                "so it may be the same image after recompression or it "
                "may have been modified. Treat with caution."
            ),
            suggested_action=SuggestedAction.REPORT_POSSIBLY_MODIFIED,
            promoter_text_present=bool(extracted_text),
            promoter_pattern_matched=pattern_match,
        )

    # --- 2. Image is NOT registered ------------------------------------

    if ocr_found and matched_party_id:
        return RiskAssessment(
            level=RiskLevel.HIGH,
            category=RiskCategory.UNREGISTERED_ATTRIBUTING_KNOWN_PARTY,
            explanation=(
                f"This image carries a promoter statement attributing it "
                f"to {matched_party_name}, but {matched_party_name} has "
                f"NOT registered this image with PIVS. This is a red flag "
                f"for a potential false attribution. The image may have "
                f"been fabricated to look like it came from "
                f"{matched_party_name}."
            ),
            suggested_action=SuggestedAction.REPORT_FALSE_ATTRIBUTION,
            attributed_party_name=matched_party_name,
            attributed_party_id=matched_party_id,
            promoter_text_present=True,
            promoter_pattern_matched=True,
        )

    if pattern_match:
        return RiskAssessment(
            level=RiskLevel.HIGH,
            category=RiskCategory.UNREGISTERED_UNKNOWN_PROMOTER,
            explanation=(
                "This image carries text that looks like a section 204F "
                "promoter statement, but the statement does not match any "
                "registered party. This is a red flag for potentially "
                "fake election material, or material from a promoter who "
                "is not on a registered party's list of authorised "
                "candidates. Future candidate-list checks will further "
                "refine this finding."
            ),
            suggested_action=SuggestedAction.REPORT_UNKNOWN_PROMOTER,
            promoter_text_present=True,
            promoter_pattern_matched=True,
        )

    # No promoter signal at all. Could just be a normal image.
    return RiskAssessment(
        level=RiskLevel.INFO,
        category=RiskCategory.UNREGISTERED_NO_PROMOTER,
        explanation=(
            "No promoter statement was detected on this image, and the "
            "image is not in the register. It may not be election "
            "material, or it may be unregistered election material "
            "without a section 204F statement. If you believe it is "
            "campaign material being shared as such, you can notify the "
            "Electoral Commission."
        ),
        suggested_action=SuggestedAction.REPORT_UNREGISTERED_ELECTION_MATERIAL,
        promoter_text_present=bool(extracted_text),
        promoter_pattern_matched=False,
    )

"""Unit tests for app.services.risk."""

import pytest

from app.services.risk import (
    PDQ_CLEAN_MATCH_MAX,
    RiskCategory,
    RiskLevel,
    SuggestedAction,
    classify,
    looks_like_promoter_statement,
)


# --------------------------------------------------------------------------
# looks_like_promoter_statement
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Authorised by J. Smith, 1 Test St",
        "AUTHORISED BY THE PARTY OFFICE",
        "Authorized by A. Person",
        "Published by the Promoter",
        "Promoted by K. Jones",
    ],
)
def test_pattern_matches_promoter_statements(text: str):
    assert looks_like_promoter_statement(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Just a regular caption with no promoter info",
        "Vote for me!",
        "Click here for more",
        None,
    ],
)
def test_pattern_rejects_non_promoter_text(text):
    assert looks_like_promoter_statement(text) is False


# --------------------------------------------------------------------------
# classify
# --------------------------------------------------------------------------


class TestRegisteredImages:
    def test_exact_match_is_ok(self):
        r = classify(image_match=True, match_type="exact", pdq_distance=None, ocr_result=None)
        assert r.level == RiskLevel.OK
        assert r.category == RiskCategory.REGISTERED_EXACT
        assert r.suggested_action == SuggestedAction.NONE

    def test_perceptual_match_near_zero_distance(self):
        r = classify(
            image_match=True, match_type="perceptual", pdq_distance=3, ocr_result=None
        )
        assert r.level == RiskLevel.OK
        assert r.category == RiskCategory.REGISTERED_PERCEPTUAL

    def test_perceptual_match_at_clean_threshold(self):
        r = classify(
            image_match=True,
            match_type="perceptual",
            pdq_distance=PDQ_CLEAN_MATCH_MAX,
            ocr_result=None,
        )
        assert r.level == RiskLevel.OK
        assert r.category == RiskCategory.REGISTERED_PERCEPTUAL

    def test_perceptual_match_above_clean_threshold_is_possibly_modified(self):
        r = classify(
            image_match=True,
            match_type="perceptual",
            pdq_distance=PDQ_CLEAN_MATCH_MAX + 1,
            ocr_result=None,
        )
        assert r.level == RiskLevel.LOW
        assert r.category == RiskCategory.REGISTERED_POSSIBLY_MODIFIED
        assert r.suggested_action == SuggestedAction.REPORT_POSSIBLY_MODIFIED


class TestUnregisteredImages:
    def test_no_promoter_text_is_info_level(self):
        r = classify(
            image_match=False,
            match_type="none",
            pdq_distance=None,
            ocr_result={"found": False, "extracted_text": ""},
        )
        assert r.level == RiskLevel.INFO
        assert r.category == RiskCategory.UNREGISTERED_NO_PROMOTER
        assert r.suggested_action == SuggestedAction.REPORT_UNREGISTERED_ELECTION_MATERIAL

    def test_random_text_with_no_promoter_marker_is_info_level(self):
        r = classify(
            image_match=False,
            match_type="none",
            pdq_distance=None,
            ocr_result={
                "found": False,
                "extracted_text": "Vote for me on election day!",
            },
        )
        assert r.level == RiskLevel.INFO
        assert r.category == RiskCategory.UNREGISTERED_NO_PROMOTER

    def test_unknown_promoter_text_is_high_risk(self):
        r = classify(
            image_match=False,
            match_type="none",
            pdq_distance=None,
            ocr_result={
                "found": False,
                "extracted_text": "Authorised by an unknown person, no address",
            },
        )
        assert r.level == RiskLevel.HIGH
        assert r.category == RiskCategory.UNREGISTERED_UNKNOWN_PROMOTER
        assert r.suggested_action == SuggestedAction.REPORT_UNKNOWN_PROMOTER
        assert r.promoter_pattern_matched is True

    def test_matches_known_party_but_image_not_registered_is_high_risk(self):
        r = classify(
            image_match=False,
            match_type="none",
            pdq_distance=None,
            ocr_result={
                "found": True,
                "party_id": "party-uuid-123",
                "party_name": "Test Party",
                "extracted_text": "Authorised by Test Party HQ, 1 Test St",
            },
        )
        assert r.level == RiskLevel.HIGH
        assert r.category == RiskCategory.UNREGISTERED_ATTRIBUTING_KNOWN_PARTY
        assert r.suggested_action == SuggestedAction.REPORT_FALSE_ATTRIBUTION
        assert r.attributed_party_name == "Test Party"
        assert r.attributed_party_id == "party-uuid-123"
        assert "Test Party" in r.explanation


class TestSerialisation:
    def test_to_dict_round_trip(self):
        r = classify(
            image_match=True, match_type="exact", pdq_distance=None, ocr_result=None
        )
        d = r.to_dict()
        assert d["level"] == "ok"
        assert d["category"] == "registered_exact"
        assert d["suggested_action"] == "none"
        # The required keys are present
        for key in (
            "level",
            "category",
            "explanation",
            "suggested_action",
            "attributed_party_name",
            "attributed_party_id",
            "promoter_text_present",
            "promoter_pattern_matched",
        ):
            assert key in d

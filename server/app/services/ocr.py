"""
OCR service for promoter statement detection.

Uses Tesseract OCR to extract text from political campaign images and
fuzzy-matches against the party's registered promoter statement.
"""

import io
from difflib import SequenceMatcher

from PIL import Image, ImageEnhance

from app.core.config import settings

try:
    import pytesseract
except ImportError:
    pytesseract = None  # type: ignore[assignment]


def _preprocess_image(image_bytes: bytes) -> Image.Image:
    """Pre-process image for better OCR accuracy.

    Converts to grayscale and increases contrast to help Tesseract
    extract text from varied backgrounds.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Convert to grayscale
    gray = img.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.0)

    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(enhanced)
    enhanced = enhancer.enhance(2.0)

    return enhanced


def extract_text_from_image(image_bytes: bytes) -> str:
    """Run Tesseract OCR on an image and return all extracted text.

    Args:
        image_bytes: Image file bytes.

    Returns:
        Extracted text as a single string.

    Raises:
        RuntimeError: If pytesseract is not installed.
    """
    if pytesseract is None:
        raise RuntimeError(
            "pytesseract is not installed. Install with: pip install pytesseract"
        )

    processed = _preprocess_image(image_bytes)
    text = pytesseract.image_to_string(processed, lang="eng")
    return text.strip()


def _best_substring_match(text: str, target: str) -> tuple[str, float]:
    """Find the substring of text that best matches the target string.

    Uses a sliding window approach with SequenceMatcher for fuzzy matching.

    Returns:
        (best_matching_substring, match_ratio)
    """
    text_lower = text.lower()
    target_lower = target.lower()

    # Try exact substring first
    if target_lower in text_lower:
        return target, 1.0

    # Sliding window fuzzy match
    target_len = len(target_lower)
    best_match = ""
    best_ratio = 0.0

    # Try windows of varying sizes around the target length
    for window_size in range(
        max(1, target_len - 20), target_len + 20
    ):
        if window_size > len(text_lower):
            continue
        for start in range(0, len(text_lower) - window_size + 1):
            window = text_lower[start : start + window_size]
            ratio = SequenceMatcher(None, window, target_lower).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = text[start : start + window_size]

    return best_match, best_ratio


def find_promoter_statement(
    image_bytes: bytes,
    expected_statement: str,
) -> dict:
    """OCR an image and search for the expected promoter statement.

    Args:
        image_bytes: Image file bytes.
        expected_statement: The promoter statement text to search for.

    Returns:
        dict with keys:
            found: bool - whether the statement was found with sufficient confidence
            confidence: float - match confidence 0.0 to 1.0
            extracted_text: str - raw OCR text
            best_match: str | None - closest matching substring
            match_ratio: float - fuzzy match ratio
    """
    try:
        extracted_text = extract_text_from_image(image_bytes)
    except RuntimeError:
        return {
            "found": False,
            "confidence": 0.0,
            "extracted_text": "",
            "best_match": None,
            "match_ratio": 0.0,
            "error": "OCR engine not available",
        }

    if not extracted_text:
        return {
            "found": False,
            "confidence": 0.0,
            "extracted_text": "",
            "best_match": None,
            "match_ratio": 0.0,
        }

    best_match, match_ratio = _best_substring_match(extracted_text, expected_statement)

    threshold = settings.PROMOTER_OCR_MATCH_THRESHOLD
    found = match_ratio >= threshold

    return {
        "found": found,
        "confidence": round(match_ratio, 3),
        "extracted_text": extracted_text,
        "best_match": best_match if match_ratio > 0.3 else None,
        "match_ratio": round(match_ratio, 3),
    }

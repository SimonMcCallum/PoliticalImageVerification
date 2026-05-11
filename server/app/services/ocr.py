"""
OCR service for promoter statement detection.

NZ section 204F promoter statements are typically printed in small
text (often near the edge of a campaign image), and on social-media
graphics they are frequently white on a dark background. Plain
grayscale + contrast OCR misses many of these. The pipeline therefore
runs Tesseract on several variants of the image and merges the text
back together before the fuzzy-match stage:

  1. grayscale + contrast + sharpness (handles dark-on-light)
  2. inverted grayscale + contrast (handles white-on-dark)
  3. high-contrast binary threshold (handles low-contrast scans)
  4. 2x upscale of variant 1 (helps with small text)

For each variant we ask Tesseract for both a generic-text pass and a
"sparse text" pass (page-segmentation mode 11), since promoter
statements are usually a short isolated block rather than flowing
paragraphs.

The combined text is then passed to the fuzzy-match stage. The
behavioural contract for callers is unchanged.
"""

import io
import logging
from difflib import SequenceMatcher

from PIL import Image, ImageEnhance, ImageOps

from app.core.config import settings

try:
    import pytesseract
except ImportError:
    pytesseract = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def _to_grayscale_contrast(img: Image.Image) -> Image.Image:
    """Grayscale + contrast + sharpness, suitable for dark-on-light text."""
    gray = img.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(2.0)
    gray = ImageEnhance.Sharpness(gray).enhance(2.0)
    return gray


def _to_inverted_contrast(img: Image.Image) -> Image.Image:
    """Inverted grayscale + contrast, suitable for white-on-dark text."""
    gray = img.convert("L")
    inv = ImageOps.invert(gray)
    inv = ImageEnhance.Contrast(inv).enhance(2.0)
    return inv


def _to_binary_threshold(img: Image.Image, threshold: int = 160) -> Image.Image:
    """Aggressive binarisation; helps low-contrast scans of printed text."""
    gray = img.convert("L")
    return gray.point(lambda p: 255 if p >= threshold else 0).convert("L")


def _to_upscaled(img: Image.Image, factor: int = 2) -> Image.Image:
    """Upscale to give Tesseract more pixels per glyph on small text."""
    w, h = img.size
    return img.resize((w * factor, h * factor), Image.LANCZOS)


def _preprocess_image(image_bytes: bytes) -> Image.Image:
    """Backward-compatible single-variant preprocessor (used by callers
    that only need one image)."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return _to_grayscale_contrast(img)


def _run_tesseract(img: Image.Image, psm: int) -> str:
    """Run Tesseract once with the given page-segmentation mode."""
    config = f"--psm {psm}"
    try:
        return pytesseract.image_to_string(img, lang="eng", config=config).strip()
    except Exception as exc:
        logger.debug(f"Tesseract failed at psm={psm}: {exc}")
        return ""


def extract_text_from_image(image_bytes: bytes) -> str:
    """Run multi-variant Tesseract OCR and return the combined text.

    The variants cover dark-on-light, white-on-dark, low-contrast, and
    small-text cases. The page-segmentation modes 3 (auto) and 11
    (sparse) are both tried per variant. Duplicate lines are
    collapsed at the end.

    Raises ``RuntimeError`` if pytesseract is not installed.
    """
    if pytesseract is None:
        raise RuntimeError(
            "pytesseract is not installed. Install with: pip install pytesseract"
        )

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    variants: list[Image.Image] = [
        _to_grayscale_contrast(img),
        _to_inverted_contrast(img),
        _to_binary_threshold(img),
        _to_upscaled(_to_grayscale_contrast(img), factor=2),
    ]

    pieces: list[str] = []
    for v in variants:
        # psm=3 is the default; psm=11 ("sparse text") is much better
        # for finding a single isolated block like a promoter line.
        for psm in (3, 11):
            piece = _run_tesseract(v, psm)
            if piece:
                pieces.append(piece)

    if not pieces:
        return ""

    # Collapse duplicate lines while preserving order.
    seen: set[str] = set()
    out_lines: list[str] = []
    for chunk in pieces:
        for line in chunk.splitlines():
            ln = line.strip()
            if not ln:
                continue
            key = ln.lower()
            if key in seen:
                continue
            seen.add(key)
            out_lines.append(ln)

    return "\n".join(out_lines)


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


def find_promoter_across_parties(
    image_bytes: bytes,
    parties: list[tuple[str, str, str]],
) -> dict:
    """OCR an image and search for ANY party's promoter statement.

    Args:
        image_bytes: Image file bytes.
        parties: List of (party_id, party_name, promoter_statement) tuples.

    Returns:
        dict with: found, party_id, party_name, confidence, extracted_text
    """
    try:
        extracted_text = extract_text_from_image(image_bytes)
    except RuntimeError:
        return {
            "found": False,
            "party_id": None,
            "party_name": None,
            "confidence": 0.0,
            "extracted_text": "",
        }

    if not extracted_text:
        return {
            "found": False,
            "party_id": None,
            "party_name": None,
            "confidence": 0.0,
            "extracted_text": "",
        }

    best_party_id = None
    best_party_name = None
    best_ratio = 0.0

    for party_id, party_name, statement in parties:
        if not statement:
            continue
        _, ratio = _best_substring_match(extracted_text, statement)
        if ratio > best_ratio:
            best_ratio = ratio
            best_party_id = party_id
            best_party_name = party_name

    threshold = settings.PROMOTER_OCR_MATCH_THRESHOLD
    return {
        "found": best_ratio >= threshold,
        "party_id": best_party_id if best_ratio >= threshold else None,
        "party_name": best_party_name if best_ratio >= threshold else None,
        "confidence": round(best_ratio, 3),
        "extracted_text": extracted_text,
    }


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

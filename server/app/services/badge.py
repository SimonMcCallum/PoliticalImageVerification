"""
Badge and QR code generation service.

Generates verification badges and QR codes that can be overlaid
on registered images. The badge is kept small (<=5% of image area)
to ensure the perceptual hash still matches the original.
"""

import io
import math

import qrcode
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings


def generate_qr_code(verification_id: str, size: int = 200) -> bytes:
    """Generate a QR code PNG for a verification URL."""
    url = f"{settings.VERIFICATION_BASE_URL}/{verification_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_badge_overlay(
    original_bytes: bytes,
    verification_id: str,
    party_name: str,
    position: str | None = None,
) -> bytes:
    """Generate a copy of the image with a verification badge overlay.

    The badge contains a small QR code and verification text.
    It is sized to be <= BADGE_MAX_AREA_PERCENT of the total image area.
    """
    position = position or settings.BADGE_DEFAULT_POSITION
    img = Image.open(io.BytesIO(original_bytes)).convert("RGBA")
    img_w, img_h = img.size

    # Calculate badge dimensions (max 5% of image area)
    max_badge_area = img_w * img_h * (settings.BADGE_MAX_AREA_PERCENT / 100)
    badge_side = int(math.sqrt(max_badge_area))
    # Badge is rectangular: wider than tall
    badge_w = max(40, min(badge_side, img_w // 3))
    badge_h = max(20, badge_w // 2)

    # Create badge background with semi-transparency
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 180))
    draw = ImageDraw.Draw(badge)

    # QR code (small, left side of badge)
    qr_size = max(10, badge_h - 8)
    qr_bytes = generate_qr_code(verification_id, size=qr_size)
    qr_img = Image.open(io.BytesIO(qr_bytes)).convert("RGBA").resize(
        (qr_size, qr_size), Image.NEAREST
    )
    badge.paste(qr_img, (4, 4))

    # Text (right side of badge)
    text_x = qr_size + 10
    try:
        font_small = ImageFont.truetype("arial.ttf", max(10, badge_h // 5))
        font_tiny = ImageFont.truetype("arial.ttf", max(8, badge_h // 7))
    except OSError:
        font_small = ImageFont.load_default()
        font_tiny = font_small

    draw.text((text_x, 4), "VERIFIED", fill=(100, 220, 100, 255), font=font_small)
    draw.text(
        (text_x, 4 + badge_h // 4), party_name[:20], fill=(255, 255, 255, 255), font=font_tiny
    )
    draw.text(
        (text_x, 4 + badge_h // 2),
        f"ID: {verification_id}",
        fill=(200, 200, 200, 255),
        font=font_tiny,
    )

    # Add thin border
    draw.rectangle(
        [(0, 0), (badge_w - 1, badge_h - 1)], outline=(100, 220, 100, 200), width=1
    )

    # Position the badge
    margin = 10
    positions = {
        "bottom-right": (img_w - badge_w - margin, img_h - badge_h - margin),
        "bottom-left": (margin, img_h - badge_h - margin),
        "top-right": (img_w - badge_w - margin, margin),
        "top-left": (margin, margin),
    }
    pos = positions.get(position, positions["bottom-right"])

    # Composite badge onto image
    result = img.copy()
    result.paste(badge, pos, badge)

    # Convert back to RGB and return as PNG bytes
    result_rgb = result.convert("RGB")
    buf = io.BytesIO()
    result_rgb.save(buf, format="PNG")
    return buf.getvalue()

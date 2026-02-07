"""
Promoter statement overlay service.

Adds Electoral Act promoter statements to political campaign images with
contrast-aware text colouring and configurable positioning. Text placement
accounts for image orientation (portrait vs landscape) and checks background
colour to ensure WCAG 2.1 AA legibility (4.5:1 contrast ratio minimum).
"""

import io
import math
import textwrap

from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings

# Valid positions for the promoter statement overlay
VALID_POSITIONS = ("top-left", "top-right", "bottom-left", "bottom-right")


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.1 definition.

    See: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    r, g, b = rgb
    channels = []
    for c in (r, g, b):
        srgb = c / 255.0
        if srgb <= 0.04045:
            channels.append(srgb / 12.92)
        else:
            channels.append(((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def wcag_contrast_ratio(
    fg: tuple[int, int, int], bg: tuple[int, int, int]
) -> float:
    """Calculate WCAG 2.1 contrast ratio between two RGB colours.

    Returns a value between 1.0 (identical) and 21.0 (black on white).
    WCAG AA requires >= 4.5:1 for normal text.
    """
    lum_fg = _relative_luminance(fg)
    lum_bg = _relative_luminance(bg)
    lighter = max(lum_fg, lum_bg)
    darker = min(lum_fg, lum_bg)
    return (lighter + 0.05) / (darker + 0.05)


def sample_background_color(
    img: Image.Image, region: tuple[int, int, int, int]
) -> tuple[int, int, int]:
    """Sample the average RGB colour within a rectangular region of the image.

    Args:
        img: PIL Image (RGB mode).
        region: (left, top, right, bottom) bounding box.

    Returns:
        Average (R, G, B) tuple.
    """
    cropped = img.crop(region)
    # Resize to 1x1 pixel for fast average
    avg = cropped.resize((1, 1), Image.LANCZOS)
    pixel = avg.getpixel((0, 0))
    if isinstance(pixel, int):
        return (pixel, pixel, pixel)
    return (pixel[0], pixel[1], pixel[2])


def choose_text_color(
    bg: tuple[int, int, int],
) -> tuple[tuple[int, int, int], bool]:
    """Choose white or black text for best contrast against the background.

    Returns:
        (text_colour_rgb, needs_backing) - if neither white nor black achieves
        the minimum contrast ratio, needs_backing=True indicates a
        semi-transparent backing rectangle should be drawn.
    """
    min_ratio = settings.PROMOTER_WCAG_CONTRAST_RATIO

    white = (255, 255, 255)
    black = (0, 0, 0)

    ratio_white = wcag_contrast_ratio(white, bg)
    ratio_black = wcag_contrast_ratio(black, bg)

    if ratio_white >= min_ratio and ratio_white >= ratio_black:
        return white, False
    if ratio_black >= min_ratio:
        return black, False

    # Neither passes — use whichever is better, but flag for backing
    if ratio_white >= ratio_black:
        return white, True
    return black, True


def detect_orientation(img: Image.Image) -> str:
    """Detect whether the image is portrait or landscape."""
    w, h = img.size
    if h > w:
        return "portrait"
    return "landscape"


def calculate_font_size(
    img: Image.Image,
    text: str,
    max_width_ratio: float = 0.40,
    min_height_ratio: float = 0.015,
) -> int:
    """Calculate an appropriate font size for legibility.

    Ensures:
    - Text block width <= max_width_ratio of image width
    - Font height >= min_height_ratio of image height
    - Font height >= PROMOTER_MIN_FONT_SIZE pixels

    Returns the font size in pixels.
    """
    w, h = img.size
    min_size = max(settings.PROMOTER_MIN_FONT_SIZE, int(h * min_height_ratio))
    max_text_width = int(w * max_width_ratio)

    # Start at min_size and increase until text gets too wide
    font_size = min_size
    for candidate in range(min_size, min(80, h // 4)):
        try:
            font = ImageFont.truetype("arial.ttf", candidate)
        except OSError:
            font = ImageFont.load_default()

        # Estimate single-line width
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        if text_width > max_text_width:
            break
        font_size = candidate

    return font_size


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font, falling back to default if system fonts unavailable."""
    for font_name in ("arial.ttf", "Arial.ttf", "helvetica.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels using the given font."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]


def overlay_promoter_statement(
    image_bytes: bytes,
    statement: str,
    position: str = "bottom-left",
    font_size: int | None = None,
) -> bytes:
    """Add a promoter statement text overlay to an image.

    The statement is rendered with appropriate contrast against the background,
    using a semi-transparent backing rectangle where necessary for legibility.

    Args:
        image_bytes: Original image as bytes.
        statement: The promoter statement text to overlay.
        position: Corner placement - one of top-left, top-right,
                  bottom-left, bottom-right.
        font_size: Override font size in pixels, or None for auto-calculation.

    Returns:
        Modified image as PNG bytes.
    """
    if position not in VALID_POSITIONS:
        position = "bottom-left"

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_w, img_h = img.size
    orientation = detect_orientation(img)

    # Calculate font size
    if font_size is None:
        font_size = calculate_font_size(img, statement)
    font_size = max(font_size, settings.PROMOTER_MIN_FONT_SIZE)
    font = _load_font(font_size)

    # Calculate text area dimensions
    padding = max(6, font_size // 2)
    # In portrait, allow wider text area; in landscape, keep narrower
    if orientation == "portrait":
        max_text_width = int(img_w * 0.90) - (padding * 2)
    else:
        max_text_width = int(img_w * 0.45) - (padding * 2)

    # Wrap text to fit
    lines = _wrap_text(statement, font, max_text_width)

    # Calculate text block dimensions
    line_height = font_size + 4
    text_block_height = len(lines) * line_height
    text_block_width = 0
    for line in lines:
        bbox = font.getbbox(line)
        text_block_width = max(text_block_width, bbox[2] - bbox[0])

    # Total box dimensions including padding
    box_w = text_block_width + (padding * 2)
    box_h = text_block_height + (padding * 2)

    # Calculate position
    margin = max(8, font_size)
    if position == "bottom-left":
        box_x = margin
        box_y = img_h - box_h - margin
    elif position == "bottom-right":
        box_x = img_w - box_w - margin
        box_y = img_h - box_h - margin
    elif position == "top-left":
        box_x = margin
        box_y = margin
    else:  # top-right
        box_x = img_w - box_w - margin
        box_y = margin

    # Clamp to image bounds
    box_x = max(0, min(box_x, img_w - box_w))
    box_y = max(0, min(box_y, img_h - box_h))

    # Sample background colour beneath the text region
    sample_region = (box_x, box_y, box_x + box_w, box_y + box_h)
    bg_color = sample_background_color(img, sample_region)

    # Choose text colour for contrast
    text_color, needs_backing = choose_text_color(bg_color)

    # Draw onto an RGBA overlay for alpha compositing
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Always draw a semi-transparent backing rectangle for consistency
    # Use dark backing for white text, light backing for black text
    if text_color == (255, 255, 255):
        backing_color = (0, 0, 0, 180)  # dark semi-transparent
    else:
        backing_color = (255, 255, 255, 180)  # light semi-transparent

    draw.rectangle(
        [(box_x, box_y), (box_x + box_w, box_y + box_h)],
        fill=backing_color,
    )

    # Draw text lines
    y_cursor = box_y + padding
    for line in lines:
        # Determine x alignment based on position (left-align for left, right-align for right)
        if "right" in position:
            bbox = font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            text_x = box_x + box_w - padding - line_w
        else:
            text_x = box_x + padding

        draw.text(
            (text_x, y_cursor),
            line,
            fill=(*text_color, 255),
            font=font,
        )
        y_cursor += line_height

    # Composite overlay onto original
    img_rgba = img.convert("RGBA")
    result = Image.alpha_composite(img_rgba, overlay)
    result_rgb = result.convert("RGB")

    buf = io.BytesIO()
    result_rgb.save(buf, format="PNG")
    return buf.getvalue()

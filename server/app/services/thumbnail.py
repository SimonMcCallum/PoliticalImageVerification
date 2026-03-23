"""Thumbnail generation service."""

import io

from PIL import Image

THUMBNAIL_SIZE = (200, 200)
THUMBNAIL_FORMAT = "JPEG"
THUMBNAIL_QUALITY = 85


def generate_thumbnail(
    image_bytes: bytes, size: tuple[int, int] = THUMBNAIL_SIZE
) -> bytes:
    """Generate a thumbnail from image bytes.

    Args:
        image_bytes: Original image as bytes.
        size: Maximum (width, height) for the thumbnail.

    Returns:
        Thumbnail as JPEG bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail(size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format=THUMBNAIL_FORMAT, quality=THUMBNAIL_QUALITY)
    return buf.getvalue()

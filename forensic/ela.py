
from PIL import Image, ImageChops, ImageEnhance
import io


def analyze_ela(image_bytes, quality=90):
    """Generate an Error Level Analysis visualization."""
    original = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)

    recompressed = Image.open(buffer).convert("RGB")
    difference = ImageChops.difference(original, recompressed)

    extrema = difference.getextrema()
    max_difference = max(channel[1] for channel in extrema)

    if max_difference > 0:
        scale = 255.0 / max_difference
        difference = ImageEnhance.Brightness(
            difference
        ).enhance(scale)

    return difference


import cv2
import numpy as np
from PIL import Image
import io


def analyze_noise(image_bytes):
    """Create a simple high-frequency residual visualization."""

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    rgb = np.array(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(
        gray, (5, 5), 0
    )

    residual = cv2.absdiff(gray, blurred)

    mean_noise = float(np.mean(residual))
    std_noise = float(np.std(residual))

    return {
        "residual": residual,
        "mean_residual": round(mean_noise, 3),
        "std_residual": round(std_noise, 3)
    }

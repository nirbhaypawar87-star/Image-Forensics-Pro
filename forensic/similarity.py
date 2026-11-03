
from PIL import Image
import imagehash
import io


def compare_images(bytes_1, bytes_2):
    """Compare images using perceptual hashing."""

    image_1 = Image.open(io.BytesIO(bytes_1)).convert("RGB")
    image_2 = Image.open(io.BytesIO(bytes_2)).convert("RGB")

    hash_1 = imagehash.phash(image_1)
    hash_2 = imagehash.phash(image_2)

    distance = hash_1 - hash_2
    total_bits = len(hash_1.hash) ** 2

    similarity = 100 * (1 - distance / total_bits)

    return {
        "hash_1": str(hash_1),
        "hash_2": str(hash_2),
        "distance": distance,
        "similarity_percent": round(similarity, 2)
    }

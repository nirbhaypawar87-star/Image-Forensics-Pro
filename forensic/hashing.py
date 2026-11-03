
import hashlib


def calculate_sha256(image_bytes):
    """Calculate the SHA-256 fingerprint of image bytes."""
    return hashlib.sha256(image_bytes).hexdigest()


def compare_sha256(image_bytes_1, image_bytes_2):
    """Check whether two files have identical byte content."""
    hash_1 = calculate_sha256(image_bytes_1)
    hash_2 = calculate_sha256(image_bytes_2)

    return {
        "hash_1": hash_1,
        "hash_2": hash_2,
        "identical": hash_1 == hash_2
    }

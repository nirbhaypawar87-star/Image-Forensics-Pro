
from forensic.hashing import compare_sha256
from forensic.similarity import compare_images
from forensic.noise_analysis import analyze_noise

from PIL import Image
import io


def make_test_image(color):
    image = Image.new("RGB", (200, 200), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


image_a = make_test_image("red")
image_b = make_test_image("red")
image_c = make_test_image("blue")

result = compare_sha256(image_a, image_b)
assert result["identical"] is True
print("SHA-256 test: PASSED")

similarity = compare_images(image_a, image_c)
print("Perceptual comparison:", similarity)

noise = analyze_noise(image_a)
print("Mean residual:", noise["mean_residual"])
print("Residual standard deviation:", noise["std_residual"])

print("All forensic modules executed successfully.")

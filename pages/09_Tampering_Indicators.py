import io

import streamlit as st
from PIL import Image

from forensic.hashing import calculate_sha256, compare_sha256
from forensic.similarity import compare_images
from forensic.noise_analysis import analyze_noise
from forensic.ela import analyze_ela
from forensic.metadata import extract_metadata
from forensic.history import save_analysis
from forensic.pdf_report import generate_pdf_report


st.set_page_config(
    page_title="Tampering Indicators",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 Image Tampering Indicators")
st.write(
    "Run several forensic checks and review their observations together. "
    "This page does not automatically declare an image authentic or manipulated."
)

st.warning(
    "ELA, residual/noise analysis, metadata and perceptual similarity can be "
    "affected by compression, resizing, editing, image content and software. "
    "Treat them as clues, not proof."
)


def get_image_details(image_bytes):
    with Image.open(io.BytesIO(image_bytes)) as image:
        return {
            "format": image.format or "Unknown",
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
        }


def make_summary(details, sha256, noise_result, ela_quality, comparison=None):
    lines = [
        f"SHA-256: {sha256}",
        f"Format: {details['format']}",
        f"Dimensions: {details['width']} x {details['height']}",
        f"Mean residual: {noise_result['mean_residual']}",
        f"Residual standard deviation: {noise_result['std_residual']}",
        f"ELA recompression quality: {ela_quality}",
    ]
    if comparison is not None:
        lines.extend([
            f"Compared with: {comparison['other_filename']}",
            f"Byte-identical: {comparison['identical']}",
            f"Perceptual similarity: {comparison['similarity_percent']}%",
            f"Perceptual hash distance: {comparison['distance']}",
        ])
    lines.append(
        "These measurements are technical observations and do not independently "
        "prove authenticity or tampering."
    )
    return "\n".join(lines)


image_file = st.file_uploader(
    "Upload the primary image",
    type=["png", "jpg", "jpeg", "tiff", "webp"],
    key="indicator_primary",
)

second_file = st.file_uploader(
    "Optional: upload a second image to compare",
    type=["png", "jpg", "jpeg", "tiff", "webp"],
    key="indicator_secondary",
)

ela_quality = st.slider(
    "ELA JPEG recompression quality",
    min_value=50,
    max_value=100,
    value=90,
    step=5,
    key="indicator_ela_quality",
)

if image_file is not None:
    image_bytes = image_file.getvalue()

    try:
        details = get_image_details(image_bytes)
        metadata = extract_metadata(image_bytes)
        sha256 = calculate_sha256(image_bytes)

        st.subheader("Primary image")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(image_bytes, caption=image_file.name, use_container_width=True)

        with col2:
            st.write(f"**Filename:** {image_file.name}")
            st.write(f"**Format:** {details['format']}")
            st.write(f"**Dimensions:** {details['width']} × {details['height']} pixels")
            st.write(f"**File size:** {len(image_bytes):,} bytes")
            st.write("**SHA-256:**")
            st.code(sha256)

        st.divider()
        st.subheader("Forensic checks")

        with st.spinner("Running noise and ELA analysis..."):
            noise_result = analyze_noise(image_bytes)
            ela_image = analyze_ela(image_bytes, quality=ela_quality)

        extra_exif_count = sum(
            1 for key in metadata
            if key not in ["Format", "Width", "Height", "Color Mode", "File Size (bytes)"]
        )

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Mean residual", f"{noise_result['mean_residual']:.4f}")
        metric2.metric("Residual standard deviation", f"{noise_result['std_residual']:.4f}")
        metric3.metric("Available metadata fields", extra_exif_count)

        noise_col, ela_col = st.columns(2)
        with noise_col:
            st.image(
                noise_result["residual"],
                caption="High-frequency residual",
                clamp=True,
                use_container_width=True,
            )
        with ela_col:
            st.image(
                ela_image,
                caption=f"ELA visualization (quality {ela_quality})",
                use_container_width=True,
            )

        comparison_data = None
        if second_file is not None:
            second_bytes = second_file.getvalue()
            hashes = compare_sha256(image_bytes, second_bytes)
            similarity = compare_images(image_bytes, second_bytes)
            comparison_data = {
                "other_filename": second_file.name,
                "identical": hashes["identical"],
                "similarity_percent": similarity["similarity_percent"],
                "distance": similarity["distance"],
            }

            st.divider()
            st.subheader("Two-image comparison")
            c1, c2 = st.columns(2)
            c1.metric("Byte-identical files", "Yes" if hashes["identical"] else "No")
            c2.metric("Estimated perceptual similarity", f"{similarity['similarity_percent']}%")
            st.caption(
                f"Perceptual hash distance: {similarity['distance']}. "
                "A byte mismatch does not necessarily mean the depicted content differs."
            )

        st.divider()
        st.subheader("Interpretation guide")
        st.markdown(
            "- **SHA-256:** identifies exact file bytes. A changed hash means the bytes differ, not necessarily that the image was manipulated.\n"
            "- **Perceptual similarity:** estimates visual similarity between two images; it is not a probability of authenticity.\n"
            "- **Noise/residual view:** compares the grayscale image with a blurred version. Edges, texture, resizing and compression affect it.\n"
            "- **ELA:** shows differences after JPEG recompression. Uneven areas have multiple possible causes.\n"
            "- **Metadata:** can provide context, but may be absent, edited or removed."
        )

        summary_lines = [
            f"SHA-256: {sha256}",
            f"Format: {details['format']}",
            f"Dimensions: {details['width']} x {details['height']}",
            f"Mean residual: {noise_result['mean_residual']}",
            f"Residual standard deviation: {noise_result['std_residual']}",
            f"ELA recompression quality: {ela_quality}",
        ]
        if comparison_data:
            summary_lines.extend([
                f"Compared with: {comparison_data['other_filename']}",
                f"Byte-identical: {comparison_data['identical']}",
                f"Perceptual similarity: {comparison_data['similarity_percent']}%",
                f"Perceptual hash distance: {comparison_data['distance']}",
            ])
        summary_lines.append(
            "These measurements are technical observations and do not independently "
            "prove authenticity or tampering."
        )
        summary = "\n".join(summary_lines)

        st.subheader("Combined observations")
        st.text_area("Report summary", value=summary, height=190)

        if st.button("Save forensic record to history", type="primary"):
            try:
                save_analysis(
                    filename=image_file.name,
                    sha256=sha256,
                    file_size=len(image_bytes),
                    image_format=details["format"],
                    width=details["width"],
                    height=details["height"],
                    analysis_type="Tampering Indicators",
                    result_summary=summary,
                )
                st.success("Forensic record saved to analysis history.")
            except Exception as error:
                st.error(f"Could not save record: {error}")

        pdf_bytes = generate_pdf_report(
            filename=image_file.name,
            sha256=sha256,
            file_size=len(image_bytes),
            image_format=details["format"],
            width=details["width"],
            height=details["height"],
            analysis_type="Tampering Indicators",
            result_summary=summary,
        )

        st.download_button(
            "Download Combined Forensic PDF",
            data=pdf_bytes,
            file_name="tampering_indicators_report.pdf",
            mime="application/pdf",
            key="download_tampering_indicators_pdf",
        )

    except Exception as error:
        st.error(f"Could not analyze this image: {error}")

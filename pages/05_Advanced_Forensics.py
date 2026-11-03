import io
import streamlit as st
from PIL import Image

from forensic.hashing import compare_sha256, calculate_sha256
from forensic.similarity import compare_images
from forensic.noise_analysis import analyze_noise
from forensic.ela import analyze_ela
from forensic.history import save_analysis
from forensic.pdf_report import generate_pdf_report


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def image_to_png_bytes(image):
    """Convert a PIL image to PNG bytes for downloading."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def create_pdf_report(filename, image_bytes, analysis_type, summary):
    """Build a PDF report using the uploaded image's metadata."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        image_format = image.format or "Unknown"
        width, height = image.size

    return generate_pdf_report(
        filename=filename,
        sha256=calculate_sha256(image_bytes),
        file_size=len(image_bytes),
        image_format=image_format,
        width=width,
        height=height,
        analysis_type=analysis_type,
        result_summary=summary,
    )


def save_image_record(filename, image_bytes, analysis_type, summary):
    """Save an image analysis result to SQLite."""
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image_format = image.format or "Unknown"
            width, height = image.size

        save_analysis(
            filename=filename,
            sha256=calculate_sha256(image_bytes),
            file_size=len(image_bytes),
            image_format=image_format,
            width=width,
            height=height,
            analysis_type=analysis_type,
            result_summary=summary,
        )
        return True

    except Exception as error:
        st.warning(f"Could not save analysis history: {error}")
        return False


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Advanced Image Forensics",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Advanced Image Forensics")

st.write(
    "Analyze digital images using file hashing, perceptual "
    "similarity, noise visualization, and Error Level Analysis."
)

st.warning(
    "These techniques provide forensic clues, not definitive "
    "proof that an image is authentic or manipulated."
)


# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🖼️ Image Comparison",
    "🔍 Noise Analysis",
    "🧪 ELA Analysis",
])


# ==================================================
# TAB 1: IMAGE COMPARISON
# ==================================================
with tab1:
    st.subheader("Compare Two Images")

    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader(
            "Upload first image",
            type=["png", "jpg", "jpeg"],
            key="image_one",
        )

    with col2:
        file2 = st.file_uploader(
            "Upload second image",
            type=["png", "jpg", "jpeg"],
            key="image_two",
        )

    if file1 is not None and file2 is not None:
        bytes1 = file1.getvalue()
        bytes2 = file2.getvalue()

        left, right = st.columns(2)

        with left:
            st.image(
                bytes1,
                caption=file1.name,
                use_container_width=True,
            )

        with right:
            st.image(
                bytes2,
                caption=file2.name,
                use_container_width=True,
            )

        if st.button("Compare Images", type="primary", key="compare_images_button"):
            try:
                hashes = compare_sha256(bytes1, bytes2)
                similarity = compare_images(bytes1, bytes2)

                st.divider()
                st.subheader("SHA-256 File Fingerprints")

                st.write("Image 1:")
                st.code(hashes["hash_1"])

                st.write("Image 2:")
                st.code(hashes["hash_2"])

                if hashes["identical"]:
                    st.success("Both files have identical byte content.")
                else:
                    st.info(
                        "The files differ at the byte level. "
                        "They may still depict the same visual content."
                    )

                st.subheader("Perceptual Similarity")

                metric1, metric2 = st.columns(2)

                metric1.metric(
                    "Estimated similarity",
                    f'{similarity["similarity_percent"]}%',
                )

                metric2.metric(
                    "Perceptual hash distance",
                    similarity["distance"],
                )

                st.caption(
                    "Perceptual similarity is a hash-based estimate, "
                    "not the probability that the images are identical."
                )

                summary1 = (
                    f"Compared with {file2.name}. "
                    f'Perceptual similarity: {similarity["similarity_percent"]}%. '
                    f'Hash distance: {similarity["distance"]}. '
                    f'Identical file bytes: {hashes["identical"]}.'
                )

                summary2 = (
                    f"Compared with {file1.name}. "
                    f'Perceptual similarity: {similarity["similarity_percent"]}%. '
                    f'Hash distance: {similarity["distance"]}. '
                    f'Identical file bytes: {hashes["identical"]}.'
                )

                saved1 = save_image_record(
                    file1.name,
                    bytes1,
                    "Image Comparison",
                    summary1,
                )

                saved2 = save_image_record(
                    file2.name,
                    bytes2,
                    "Image Comparison",
                    summary2,
                )

                if saved1 and saved2:
                    st.success("Both image records saved to history.")

                comparison_summary = (
                    f"Image 1: {file1.name}. "
                    f"Image 2: {file2.name}. "
                    f"Image 1 SHA-256: {hashes['hash_1']}. "
                    f"Image 2 SHA-256: {hashes['hash_2']}. "
                    f"Identical file bytes: {hashes['identical']}. "
                    f"Perceptual similarity: {similarity['similarity_percent']}%. "
                    f"Perceptual hash distance: {similarity['distance']}. "
                    "These observations alone do not prove authenticity or manipulation."
                )

                pdf_bytes = create_pdf_report(
                    file1.name,
                    bytes1,
                    "Image Comparison",
                    comparison_summary,
                )

                st.download_button(
                    label="📄 Download Image Comparison PDF Report",
                    data=pdf_bytes,
                    file_name="image_comparison_report.pdf",
                    mime="application/pdf",
                    key="download_comparison_pdf",
                )

            except Exception as error:
                st.error(f"Image comparison failed: {error}")


# ==================================================
# TAB 2: NOISE ANALYSIS
# ==================================================
with tab2:
    st.subheader("High-Frequency Residual Analysis")

    noise_file = st.file_uploader(
        "Upload an image for noise analysis",
        type=["png", "jpg", "jpeg"],
        key="noise_image",
    )

    if noise_file is not None:
        noise_bytes = noise_file.getvalue()

        st.image(
            noise_bytes,
            caption="Original image",
            use_container_width=True,
        )

        if st.button("Analyze Noise", type="primary", key="analyze_noise_button"):
            try:
                result = analyze_noise(noise_bytes)

                st.subheader("Residual Visualization")

                st.image(
                    result["residual"],
                    caption="High-frequency residual (grayscale)",
                    clamp=True,
                    use_container_width=True,
                )

                metric1, metric2 = st.columns(2)

                metric1.metric(
                    "Mean residual",
                    result["mean_residual"],
                )

                metric2.metric(
                    "Residual standard deviation",
                    result["std_residual"],
                )

                st.info(
                    "Residual values measure differences between the "
                    "grayscale image and its blurred version. Texture, "
                    "edges, compression and resizing affect the results."
                )

                noise_summary = (
                    f'Mean residual: {result["mean_residual"]}; '
                    f'Standard deviation: {result["std_residual"]}. '
                    "Texture, edges, compression and resizing can affect these values."
                )

                saved = save_image_record(
                    noise_file.name,
                    noise_bytes,
                    "Noise Analysis",
                    noise_summary,
                )

                if saved:
                    st.success("Noise analysis saved to history.")

                pdf_bytes = create_pdf_report(
                    noise_file.name,
                    noise_bytes,
                    "Noise Analysis",
                    noise_summary,
                )

                st.download_button(
                    label="📄 Download Noise Analysis PDF Report",
                    data=pdf_bytes,
                    file_name="noise_analysis_report.pdf",
                    mime="application/pdf",
                    key="download_noise_pdf",
                )

            except Exception as error:
                st.error(f"Noise analysis failed: {error}")


# ==================================================
# TAB 3: ERROR LEVEL ANALYSIS (ELA)
# ==================================================
with tab3:
    st.subheader("Error Level Analysis (ELA)")

    st.write(
        "ELA compares an image with a JPEG-recompressed version "
        "to visualize differences in compression error."
    )

    ela_file = st.file_uploader(
        "Upload an image for ELA",
        type=["png", "jpg", "jpeg"],
        key="ela_image",
    )

    ela_quality = st.slider(
        "JPEG recompression quality",
        min_value=50,
        max_value=100,
        value=90,
        step=5,
        key="ela_quality",
    )

    if ela_file is not None:
        ela_bytes = ela_file.getvalue()

        st.image(
            ela_bytes,
            caption="Original image",
            use_container_width=True,
        )

        if st.button("Run ELA Analysis", type="primary", key="run_ela_button"):
            try:
                ela_image = analyze_ela(
                    ela_bytes,
                    quality=ela_quality,
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.image(
                        ela_bytes,
                        caption="Original image",
                        use_container_width=True,
                    )

                with col2:
                    st.image(
                        ela_image,
                        caption="ELA Visualization",
                        use_container_width=True,
                    )

                st.download_button(
                    label="Download ELA Image",
                    data=image_to_png_bytes(ela_image),
                    file_name="ela_analysis.png",
                    mime="image/png",
                    key="download_ela_image",
                )

                st.info(
                    "Bright or uneven areas can have multiple causes, "
                    "including editing, texture, edges and compression "
                    "history. ELA alone cannot confirm tampering."
                )

                ela_summary = (
                    "ELA visualization generated at JPEG "
                    f"quality {ela_quality}. "
                    "ELA alone cannot confirm image tampering."
                )

                saved = save_image_record(
                    ela_file.name,
                    ela_bytes,
                    "ELA Analysis",
                    ela_summary,
                )

                if saved:
                    st.success("ELA analysis saved to history.")

                pdf_bytes = create_pdf_report(
                    ela_file.name,
                    ela_bytes,
                    "ELA Analysis",
                    ela_summary,
                )

                st.download_button(
                    label="📄 Download ELA PDF Report",
                    data=pdf_bytes,
                    file_name="ela_analysis_report.pdf",
                    mime="application/pdf",
                    key="download_ela_pdf",
                )

            except Exception as error:
                st.error(f"ELA analysis failed: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Image Forensics Mini Project | Python | Streamlit | "
    "Pillow | OpenCV | ImageHash | SQLite | ReportLab"
)


import streamlit as st
from PIL import Image, ImageChops, ImageEnhance, ExifTags
import hashlib
import io
import json
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Digital Image Forensics",
    page_icon="🔎",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔎 Digital Image Forensics Tool")
st.caption(
    "Image metadata | SHA-256 | ELA analysis | Forensic report"
)

st.info(
    "Upload an image to inspect its properties and "
    "examine possible signs of image editing."
)

# ---------------- UPLOAD ----------------
uploaded = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG and PNG"
)

if uploaded is not None:
    image_bytes = uploaded.getvalue()

    try:
        # Verify and load the image
        image = Image.open(io.BytesIO(image_bytes))
        image.load()

        original_format = image.format or "Unknown"
        image_rgb = image.convert("RGB")

        # ---------------- HASH ----------------
        sha256_hash = hashlib.sha256(
            image_bytes
        ).hexdigest()

        # ---------------- METADATA ----------------
        width, height = image.size
        file_size = len(image_bytes)

        # ---------------- DASHBOARD ----------------
        st.subheader("📊 Image Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Width", f"{width} px")
        col2.metric("Height", f"{height} px")
        col3.metric("File Size", f"{file_size:,} bytes")
        col4.metric("Format", original_format)

        left, right = st.columns(2)

        with left:
            st.subheader("🖼️ Uploaded Image")
            st.image(
                image,
                caption=uploaded.name,
                use_container_width=True
            )

        with right:
            st.subheader("🔐 SHA-256 Hash")
            st.code(sha256_hash, language=None)

            st.write("**Filename:**", uploaded.name)
            st.write("**Image mode:**", image.mode)
            st.write("**Dimensions:**", f"{width} × {height}")
            st.write("**File size:**", f"{file_size:,} bytes")

        # ---------------- EXIF ----------------
        st.subheader("📷 EXIF Metadata")

        exif_data = {}

        try:
            raw_exif = image.getexif()

            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(
                    tag_id, str(tag_id)
                )

                # Keep the report easy to read
                exif_data[tag_name] = str(value)

        except Exception:
            exif_data = {}

        if exif_data:
            st.json(exif_data)
        else:
            st.warning(
                "No standard EXIF metadata was found. "
                "Some images do not contain EXIF information."
            )

        # ---------------- ELA ANALYSIS ----------------
        st.subheader("🔬 Error Level Analysis (ELA)")

        st.write(
            "ELA compares an image with a recompressed JPEG "
            "version and highlights differences."
        )

        # Create a JPEG comparison copy in memory
        buffer = io.BytesIO()
        image_rgb.save(
            buffer,
            format="JPEG",
            quality=90
        )
        buffer.seek(0)

        recompressed = Image.open(buffer).convert("RGB")

        difference = ImageChops.difference(
            image_rgb, recompressed
        )

        ela_image = ImageEnhance.Contrast(
            difference
        ).enhance(10)

        st.image(
            ela_image,
            caption="ELA visualization (contrast enhanced)",
            use_container_width=True
        )

        st.warning(
            "ELA is an investigative aid, not proof of tampering. "
            "Different image regions may have different compression "
            "patterns for legitimate reasons."
        )

        # ---------------- REPORT ----------------
        st.subheader("📄 Forensic Report")

        report = {
            "tool": "Digital Image Forensics Tool",
            "analysis_time": datetime.now().astimezone().isoformat(),
            "filename": uploaded.name,
            "format": original_format,
            "width_pixels": width,
            "height_pixels": height,
            "file_size_bytes": file_size,
            "sha256": sha256_hash,
            "exif_metadata": exif_data,
            "ela_method": (
                "Difference from JPEG recompression at quality 90; "
                "contrast enhanced by factor 10"
            ),
            "limitations": (
                "ELA does not independently prove manipulation. "
                "Interpret results with other evidence."
            )
        }

        report_json = json.dumps(
            report, indent=4, ensure_ascii=False
        )

        st.download_button(
            label="⬇️ Download Forensic Report (JSON)",
            data=report_json,
            file_name="forensic_report.json",
            mime="application/json"
        )

        st.success("Image analysis completed.")

    except Exception:
        st.error(
            "Unable to analyze this file. "
            "Please upload a valid JPG, JPEG or PNG image."
        )

else:
    st.info(
        "👆 Upload an image above to start forensic analysis."
    )

st.divider()
st.caption(
    "Academic Mini Project | Digital Image Forensics | Python + Streamlit"
)

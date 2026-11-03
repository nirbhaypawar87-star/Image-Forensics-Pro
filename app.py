
import streamlit as st
from PIL import Image, ImageChops, ImageEnhance, ExifTags
import hashlib
import io
import json
from datetime import datetime

# =============== PAGE CONFIGURATION ===============
st.set_page_config(
    page_title="Image Forensics Pro",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============== CUSTOM DESIGN ===============
st.markdown("""
<style>
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background: rgba(128, 128, 128, 0.08);
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(128, 128, 128, 0.2);
}
div[data-testid="stFileUploader"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =============== SIDEBAR ===============
st.sidebar.title("🔎 Image Forensics")
st.sidebar.caption("Digital Investigation Suite")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Image Analysis",
        "Metadata Forensics",
        "About Project"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Academic Mini Project")
st.sidebar.caption("Python • Streamlit • Pillow")

uploaded = st.sidebar.file_uploader(
    "Upload Evidence Image",
    type=["jpg", "jpeg", "png"],
    help="Choose a JPG, JPEG or PNG image."
)

# =============== HELPER FUNCTIONS ===============
def get_exif(image):
    metadata = {}

    try:
        exif = image.getexif()

        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(
                tag_id, str(tag_id)
            )
            metadata[tag_name] = str(value)

    except Exception:
        pass

    return metadata


def calculate_ela(image):
    original = image.convert("RGB")

    buffer = io.BytesIO()
    original.save(
        buffer,
        format="JPEG",
        quality=90
    )
    buffer.seek(0)

    recompressed = Image.open(buffer).convert("RGB")
    difference = ImageChops.difference(
        original, recompressed
    )

    enhanced = ImageEnhance.Contrast(
        difference
    ).enhance(10)

    return enhanced


def analyze_image(file_bytes):
    image = Image.open(io.BytesIO(file_bytes))
    image.load()

    return {
        "image": image,
        "format": image.format or "Unknown",
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "size": len(file_bytes),
        "sha256": hashlib.sha256(file_bytes).hexdigest(),
        "exif": get_exif(image)
    }


def format_bytes(size):
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} bytes"


# =============== HEADER ===============
st.title("🔎 Digital Image Forensics")
st.caption(
    "Advanced image examination, metadata inspection "
    "and integrity analysis"
)

# =============== PROCESS UPLOADED IMAGE ===============
result = None
file_bytes = None

if uploaded is not None:
    file_bytes = uploaded.getvalue()

    try:
        result = analyze_image(file_bytes)
    except Exception:
        st.error(
            "This image could not be processed. "
            "Please upload a valid JPG, JPEG or PNG."
        )

# =============== DASHBOARD PAGE ===============
if page == "Dashboard":

    st.subheader("Investigation Dashboard")

    st.write(
        "Examine image properties, inspect available metadata "
        "and generate preliminary forensic findings."
    )

    
    st.markdown("### Forensic Toolkit")

    tool1, tool2, tool3 = st.columns(3)

    with tool1:
        st.markdown("**🔐 Evidence Integrity**")
        st.caption(
            "Register evidence and review SHA-256 fingerprints."
        )
        if st.button("Open Evidence Records", use_container_width=True):
            st.switch_page("pages/10_Evidence_Records.py")

    with tool2:
        st.markdown("**🧪 Tampering Indicators**")
        st.caption(
            "Explore ELA, noise analysis and image comparison."
        )
        if st.button("Open Tampering Indicators", use_container_width=True):
            st.switch_page("pages/09_Tampering_Indicators.py")

    with tool3:
        st.markdown("**📊 Analysis History**")
        st.caption(
            "Review previously saved forensic analyses."
        )
        if st.button("Open Analysis History", use_container_width=True):
            st.switch_page("pages/06_Analysis_History.py")

    st.divider()


    if result:
        st.success("Image loaded and basic analysis completed.")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Image Width", f"{result['width']} px")
        c2.metric("Image Height", f"{result['height']} px")
        c3.metric("File Size", format_bytes(result["size"]))
        c4.metric("Image Format", result["format"])

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("### Uploaded Evidence")
            st.image(
                result["image"],
                caption=uploaded.name,
                use_container_width=True
            )

        with right:
            st.markdown("### Integrity Information")
            st.write("**Filename:**", uploaded.name)
            st.write("**Color mode:**", result["mode"])
            st.write("**EXIF fields found:**", len(result["exif"]))

            st.write("**SHA-256**")
            st.code(result["sha256"], language=None)

        st.info(
            "Select Image Analysis or Metadata Forensics "
            "from the sidebar to continue."
        )

    else:
        st.info(
            "👈 Upload an image from the sidebar to begin."
        )

        st.markdown("### Available Modules")

        c1, c2, c3 = st.columns(3)

        c1.markdown(
            "**🖼️ Image Analysis**\n\n"
            "Image preview, ELA visualization "
            "and comparison."
        )
        c2.markdown(
            "**📷 Metadata Forensics**\n\n"
            "Image properties and available EXIF data."
        )
        c3.markdown(
            "**🔐 Integrity Analysis**\n\n"
            "SHA-256 fingerprint and downloadable report."
        )

# =============== IMAGE ANALYSIS PAGE ===============
elif page == "Image Analysis":

    st.subheader("🖼️ Image Analysis")

    if result:
        original = result["image"].convert("RGB")

        left, right = st.columns(2)

        with left:
            st.markdown("#### Original Image")
            st.image(
                original,
                use_container_width=True
            )

        with right:
            st.markdown("#### ELA Visualization")

            ela_image = calculate_ela(original)

            st.image(
                ela_image,
                caption="JPEG recompression difference",
                use_container_width=True
            )

        st.markdown("### Image Properties")

        st.write(f"**Dimensions:** {result['width']} × {result['height']}")
        st.write(f"**Format:** {result['format']}")
        st.write(f"**File size:** {format_bytes(result['size'])}")

        st.warning(
            "ELA highlights differences after JPEG recompression. "
            "Image content, prior compression and normal editing "
            "can all affect this result. It does not prove tampering."
        )

    else:
        st.info("Upload an image using the sidebar first.")

# =============== METADATA PAGE ===============
elif page == "Metadata Forensics":

    st.subheader("📷 Metadata Forensics")

    if result:
        st.markdown("### General Properties")

        metadata_table = {
            "Filename": uploaded.name,
            "Format": result["format"],
            "Width": result["width"],
            "Height": result["height"],
            "Color Mode": result["mode"],
            "File Size": format_bytes(result["size"]),
            "SHA-256": result["sha256"]
        }

        st.json(metadata_table)

        st.markdown("### EXIF Information")

        if result["exif"]:
            st.dataframe(
                [
                    {"Field": key, "Value": value}
                    for key, value in result["exif"].items()
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                "No standard EXIF fields were found in this image."
            )

        st.caption(
            "Metadata may be missing, edited or removed. "
            "Metadata alone cannot establish authenticity."
        )

    else:
        st.info("Upload an image using the sidebar first.")

# =============== REPORT DOWNLOAD ===============
if result:
    report = {
        "tool": "Digital Image Forensics",
        "analysis_time": datetime.now().astimezone().isoformat(),
        "filename": uploaded.name,
        "format": result["format"],
        "width": result["width"],
        "height": result["height"],
        "color_mode": result["mode"],
        "file_size_bytes": result["size"],
        "sha256": result["sha256"],
        "exif_metadata": result["exif"],
        "ela_method": (
            "Difference against JPEG recompression at quality 90; "
            "contrast enhancement factor 10"
        ),
        "limitations": (
            "ELA and metadata are investigative aids, not "
            "conclusive proof of image manipulation."
        )
    }

    st.sidebar.divider()
    st.sidebar.download_button(
        "⬇️ Download JSON Report",
        data=json.dumps(
            report, indent=4, ensure_ascii=False
        ),
        file_name="forensic_report.json",
        mime="application/json",
        use_container_width=True
    )

# =============== ABOUT PAGE ===============
if page == "About Project":

    st.subheader("About the Project")

    st.markdown("""
    **Project Title:** Design and Develop a Tool for
    Digital Forensics of Images

    **Objective**

    To build a tool that examines digital image properties,
    extracts available metadata, computes cryptographic hashes
    and visualizes JPEG recompression differences.

    **Technology Stack**
    - Python
    - Streamlit
    - Pillow
    - SHA-256 hashing
    - JSON reporting

    **Current Limitations**

    This version does not automatically classify an image as
    authentic or manipulated. Advanced detection requires
    additional algorithms, suitable datasets and validation.
    """)

st.divider()
st.caption(
    "Digital Image Forensics | Academic Project | "
    "Results require careful interpretation."
)

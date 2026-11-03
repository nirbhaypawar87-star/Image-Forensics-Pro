
import streamlit as st
import pandas as pd

from forensic.metadata import extract_metadata


st.set_page_config(
    page_title="Metadata Forensics",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Metadata Forensics")

st.write(
    "Upload an image to inspect its basic properties "
    "and available EXIF metadata."
)

st.info(
    "Not every image contains EXIF metadata. Missing metadata "
    "does not prove that an image is fake or manipulated."
)

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg", "tiff", "webp"],
    key="metadata_image",
)

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(
            image_bytes,
            caption=uploaded_file.name,
            use_container_width=True,
        )

    with col2:
        st.subheader("File Information")
        st.write("**Filename:**", uploaded_file.name)
        st.write("**File size:**", f"{len(image_bytes):,} bytes")

    try:
        metadata = extract_metadata(image_bytes)

        st.divider()
        st.subheader("Extracted Metadata")

        metadata_rows = [
            {"Property": key, "Value": str(value)}
            for key, value in metadata.items()
        ]

        if metadata_rows:
            dataframe = pd.DataFrame(metadata_rows)
            st.dataframe(dataframe, use_container_width=True)

            csv_bytes = dataframe.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Metadata as CSV",
                data=csv_bytes,
                file_name="image_metadata.csv",
                mime="text/csv",
                key="download_metadata_csv",
            )
        else:
            st.warning("No metadata was found.")

        if not any(
            key not in [
                "Format",
                "Width",
                "Height",
                "Color Mode",
            ]
            for key in metadata
        ):
            st.info(
                "No additional EXIF fields were found "
                "in this image."
            )

    except Exception as error:
        st.error(f"Could not extract metadata: {error}")

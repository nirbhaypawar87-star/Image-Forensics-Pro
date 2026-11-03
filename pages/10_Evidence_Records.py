
import streamlit as st

from forensic.hashing import calculate_sha256
from forensic.evidence import save_evidence, get_evidence_records

st.set_page_config(page_title="Evidence Records", page_icon="🔐", layout="wide")

st.title("Evidence Integrity Records")
st.write("Register and review image evidence using SHA-256 hashes.")

uploaded_file = st.file_uploader(
    "Upload an evidence image",
    type=["png", "jpg", "jpeg", "tiff", "webp"]
)

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    sha256 = calculate_sha256(image_bytes)
    file_size = len(image_bytes)

    st.write("Filename:", uploaded_file.name)
    st.write("File size:", f"{file_size:,} bytes")
    st.code(sha256)

    if st.button("Save Evidence Record"):
        try:
            record = save_evidence(
                uploaded_file.name,
                sha256,
                file_size
            )
            st.success("Evidence record saved!")
            st.write("Evidence ID:", record["evidence_id"])
            st.write("Timestamp:", record["created_at"])
        except Exception as error:
            st.error(f"Could not save record: {error}")

st.divider()
st.subheader("Saved Evidence Records")

try:
    records = get_evidence_records()
    if records:
        st.dataframe(records, use_container_width=True, hide_index=True)
    else:
        st.info("No evidence records saved yet.")
except Exception as error:
    st.error(f"Could not load records: {error}")

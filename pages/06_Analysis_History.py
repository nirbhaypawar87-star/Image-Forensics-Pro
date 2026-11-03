
import streamlit as st
import pandas as pd

from forensic.history import get_history

st.set_page_config(
    page_title="Analysis History",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Forensic Analysis History")
st.write("View previously saved image analysis records.")

if st.button("Refresh History"):
    st.rerun()

try:
    records = get_history()

    if not records:
        st.info(
            "No analysis records saved yet. "
            "Save an analysis from the forensic tools first."
        )
    else:
        st.metric("Total Saved Records", len(records))

        df = pd.DataFrame(records)

        display_columns = [
            "id",
            "filename",
            "analysis_type",
            "file_size",
            "image_format",
            "width",
            "height",
            "created_at"
        ]

        df = df[
            [column for column in display_columns if column in df.columns]
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("View Record Details")

        record_ids = [record["id"] for record in records]

        selected_id = st.selectbox(
            "Select record ID",
            record_ids
        )

        selected_record = next(
            record for record in records
            if record["id"] == selected_id
        )

        st.write("Filename:", selected_record["filename"])
        st.write("Analysis type:", selected_record["analysis_type"])
        st.write("SHA-256:")
        st.code(selected_record["sha256"])
        st.write("Result summary:")
        st.write(selected_record["result_summary"] or "No summary available")

        st.download_button(
            "Download History as CSV",
            data=pd.DataFrame(records).to_csv(index=False).encode("utf-8"),
            file_name="forensic_history.csv",
            mime="text/csv"
        )

except Exception as error:
    st.error(f"Unable to load analysis history: {error}")

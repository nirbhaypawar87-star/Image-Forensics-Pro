
import streamlit as st
import pandas as pd

from forensic.history import get_history


st.set_page_config(
    page_title="Forensic Findings Summary",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Forensic Findings Summary")

st.write(
    "A summary of image forensic analyses saved in the project history."
)

try:
    records = get_history(limit=500)

    if not records:
        st.info(
            "No analysis records found yet. "
            "Run Image Comparison, Noise Analysis, or ELA first."
        )
    else:
        df = pd.DataFrame(records)

        total_analyses = len(df)
        unique_images = df["sha256"].nunique()
        analysis_types = df["analysis_type"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Analysis Records", total_analyses)
        col2.metric("Unique Image Files (by SHA-256)", unique_images)
        col3.metric("Analysis Types Used", analysis_types)

        st.divider()

        st.subheader("Analyses by Type")

        counts = (
            df["analysis_type"]
            .value_counts()
            .rename_axis("Analysis Type")
            .reset_index(name="Count")
        )

        st.bar_chart(
            counts,
            x="Analysis Type",
            y="Count",
        )

        st.divider()

        st.subheader("Recent Analysis Records")

        display_columns = [
            "id",
            "filename",
            "analysis_type",
            "image_format",
            "width",
            "height",
            "created_at",
        ]

        available_columns = [
            column for column in display_columns
            if column in df.columns
        ]

        st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("Inspect a Finding")

        record_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select an analysis record",
            options=record_ids,
            format_func=lambda record_id: (
                f"Record #{record_id} — "
                f"{df.loc[df['id'] == record_id, 'filename'].iloc[0]}"
            ),
        )

        selected = df.loc[df["id"] == selected_id].iloc[0]

        st.write("**Filename:**", selected["filename"])
        st.write("**Analysis Type:**", selected["analysis_type"])
        st.write("**SHA-256:**")
        st.code(selected["sha256"])

        st.write("**Recorded Summary:**")
        st.write(
            selected.get("result_summary", "")
            or "No summary available."
        )

        st.caption(
            "These are recorded technical observations. "
            "They do not independently prove authenticity or tampering."
        )

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download All History as CSV",
            data=csv_data,
            file_name="forensic_findings_history.csv",
            mime="text/csv",
        )

except Exception as error:
    st.error(f"Could not load forensic history: {error}")

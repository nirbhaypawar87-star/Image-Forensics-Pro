
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from datetime import datetime, timezone
import io


def generate_pdf_report(
    filename,
    sha256,
    file_size,
    image_format,
    width,
    height,
    analysis_type,
    result_summary
):
    """Generate a downloadable PDF forensic report."""

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph("Digital Image Forensics Report", styles["Title"])
    )
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Generated: " +
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 18))

    data = [
        ["Field", "Value"],
        ["Filename", str(filename)],
        ["Analysis Type", str(analysis_type)],
        ["Image Format", str(image_format)],
        ["Image Dimensions", f"{width} x {height} pixels"],
        ["File Size", f"{file_size:,} bytes"],
        ["SHA-256", str(sha256)],
        ["Analysis Summary", str(result_summary)],
    ]

    table = Table(data, colWidths=[1.6 * inch, 4.8 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263746")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#EAF0F5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "<b>Important limitation:</b> Hashing, perceptual "
            "similarity, noise analysis and ELA provide technical "
            "observations. These results alone do not prove whether "
            "an image is authentic or manipulated.",
            styles["BodyText"]
        )
    )

    document.build(story)
    buffer.seek(0)

    return buffer.getvalue()

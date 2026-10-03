import os
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from excel_export import load_ast_data
from resistance_analysis import create_mdr_dataset

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "Antibiotic_Sensitivity_Research_Report.pdf"
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def make_table(dataframe, max_rows=30):

    if dataframe.empty:
        return Paragraph(
            "No data available.",
            styles["Normal"]
        )

    df = dataframe.head(max_rows).copy()

    data = [
        list(df.columns)
    ] + df.astype(str).values.tolist()

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            )
        ])
    )

    return table


def add_section(story, title):

    story.append(
        Paragraph(
            title,
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 0.2 * cm)
    )


# ---------------------------------------------------------
# Report generation
# ---------------------------------------------------------

def generate_report():

    ast_data = load_ast_data()

    story = []

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "ANTIBIOTIC SENSITIVITY REPORT SYSTEM",
            title_style
        )
    )

    story.append(
        Spacer(1, 0.4 * cm)
    )

    story.append(
        Paragraph(
            "Research Analysis Report",
            subtitle_style
        )
    )

    story.append(
        Spacer(1, 0.5 * cm)
    )

    story.append(
        Paragraph(
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 0.8 * cm)
    )

    # -----------------------------------------------------
    # 1. Dataset
    # -----------------------------------------------------

    add_section(
        story,
        "1. Study Dataset"
    )

    if ast_data.empty:

        story.append(
            Paragraph(
                "No AST data available.",
                styles["Normal"]
            )
        )

    else:

        total_isolates = (
            ast_data["isolate_id"]
            .nunique()
        )

        total_samples = (
            ast_data["sample_id"]
            .nunique()
        )

        story.append(
            Paragraph(
                f"Total samples: {total_samples}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"Total isolates: {total_isolates}",
                styles["Normal"]
            )
        )

        organism_table = (
            ast_data[
                ["organism", "isolate_id"]
            ]
            .drop_duplicates()
            .groupby("organism")
            ["isolate_id"]
            .nunique()
            .reset_index(
                name="Isolates"
            )
        )

        story.append(
            Spacer(1, 0.3 * cm)
        )

        story.append(
            make_table(
                organism_table
            )
        )

    story.append(
        Spacer(1, 0.5 * cm)
    )

    # -----------------------------------------------------
    # 2. MDR
    # -----------------------------------------------------

    add_section(
        story,
        "2. Multidrug Resistance"
    )

    try:

        mdr_data = create_mdr_dataset(
            ast_data
        )

        if not mdr_data.empty:

            mdr_summary = (
                mdr_data[
                    "MDR"
                ]
                .value_counts()
                .rename_axis("MDR")
                .reset_index(
                    name="Isolates"
                )
            )

            story.append(
                make_table(
                    mdr_summary
                )
            )

        else:

            story.append(
                Paragraph(
                    "No MDR data available.",
                    styles["Normal"]
                )
            )

    except Exception as error:

        story.append(
            Paragraph(
                f"MDR analysis error: {error}",
                styles["Normal"]
            )
        )

    story.append(
        Spacer(1, 0.5 * cm)
    )

    
    # -----------------------------------------------------
    # Notes
    # -----------------------------------------------------

    add_section(
        story,
        "6. Analytical Notes"
    )

    notes = [
        "Susceptibility interpretations should follow the verified breakpoint standard used in the study.",
        "MDR classification should follow the definition approved in the study protocol.",
        "Statistical associations should not be interpreted as evidence of causation."
    ]

    for note in notes:

        story.append(
            Paragraph(
                "• " + note,
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1, 0.12 * cm)
        )

    # -----------------------------------------------------
    # Build PDF
    # -----------------------------------------------------

    document = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    document.build(story)

    print(
        f"\nPDF report created:\n{OUTPUT_FILE}"
    )

    return OUTPUT_FILE


# ---------------------------------------------------------
# Styles
# ---------------------------------------------------------

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "ReportTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=18,
    leading=22,
    spaceAfter=10
)

subtitle_style = ParagraphStyle(
    "ReportSubtitle",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=13,
    leading=16
)


if __name__ == "__main__":
    generate_report()

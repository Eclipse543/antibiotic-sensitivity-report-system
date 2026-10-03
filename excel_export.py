from resistance_analysis import (
    create_mdr_dataset,
    create_mdr_summary,
    mdr_by_organism,
    mdr_by_specimen
)
import sqlite3
from pathlib import Path

import pandas as pd

from database import DATABASE_PATH


EXPORT_DIR = Path(__file__).resolve().parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


def load_ast_data():
    """Load complete AST dataset from SQLite."""

    connection = sqlite3.connect(DATABASE_PATH)

    query = """
        SELECT
            s.sample_id,
            s.patient_id,
            s.age,
            s.sex,
            s.specimen,
            s.ward,
            s.collection_date,
            i.isolate_id,
            i.organism,
            a.antibiotic,
            a.zone_diameter,
            a.interpretation
        FROM samples s
        JOIN isolates i
            ON s.sample_id = i.sample_id
        JOIN ast_results a
            ON i.isolate_id = a.isolate_id
        ORDER BY s.collection_date, s.sample_id
    """

    dataframe = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return dataframe

def create_organism_summary(data):
    """Calculate organism distribution."""

    if data.empty:
        return pd.DataFrame()

    sample_organisms = data[
        ["sample_id", "organism"]
    ].drop_duplicates()

    summary = (
        sample_organisms
        .groupby("organism")
        .size()
        .reset_index(name="Isolates")
    )

    total = summary["Isolates"].sum()

    summary["Percentage"] = (
        summary["Isolates"] / total * 100
    ).round(2)

    return summary


def create_antibiotic_summary(data):
    """Calculate S/I/R percentages by antibiotic."""

    if data.empty:
        return pd.DataFrame()

    summary = (
        data
        .groupby("antibiotic")["interpretation"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )

    for category in ["S", "I", "R"]:
        if category not in summary.columns:
            summary[category] = 0

    summary["Total"] = (
        summary["S"]
        + summary["I"]
        + summary["R"]
    )

    summary["S_percent"] = (
        summary["S"] / summary["Total"] * 100
    ).round(2)

    summary["I_percent"] = (
        summary["I"] / summary["Total"] * 100
    ).round(2)

    summary["R_percent"] = (
        summary["R"] / summary["Total"] * 100
    ).round(2)

    return summary[
        [
            "antibiotic",
            "Total",
            "S",
            "S_percent",
            "I",
            "I_percent",
            "R",
            "R_percent"
        ]
    ]


def create_organism_antibiotic_summary(data):
    """Calculate resistance by organism and antibiotic."""

    if data.empty:
        return pd.DataFrame()

    summary = (
        data
        .groupby(
            ["organism", "antibiotic"]
        )["interpretation"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )

    for category in ["S", "I", "R"]:
        if category not in summary.columns:
            summary[category] = 0

    summary["Total"] = (
        summary["S"]
        + summary["I"]
        + summary["R"]
    )

    summary["Resistance_percent"] = (
        summary["R"] / summary["Total"] * 100
    ).round(2)

    return summary[
        [
            "organism",
            "antibiotic",
            "Total",
            "S",
            "I",
            "R",
            "Resistance_percent"
        ]
    ]

def export_to_excel():

    data = load_ast_data()

    if data.empty:
        return None, "No AST data available."

    organism_summary = create_organism_summary(data)

    antibiotic_summary = create_antibiotic_summary(data)

    organism_antibiotic_summary = (
        create_organism_antibiotic_summary(data)
    )

    # -------------------------------------------------
    # MDR analysis
    # -------------------------------------------------

    mdr_data = create_mdr_dataset()

    mdr_summary = create_mdr_summary(
        mdr_data
    )

    mdr_organism = mdr_by_organism(
        mdr_data
    )

    mdr_specimen = mdr_by_specimen(
        mdr_data
    )

    output_file = (
        EXPORT_DIR
        / "Antibiotic_Sensitivity_Report.xlsx"
    )

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        data.to_excel(
            writer,
            sheet_name="Raw_Data",
            index=False
        )

        organism_summary.to_excel(
            writer,
            sheet_name="Organism_Summary",
            index=False
        )

        antibiotic_summary.to_excel(
            writer,
            sheet_name="Antibiotic_Summary",
            index=False
        )

        organism_antibiotic_summary.to_excel(
            writer,
            sheet_name="Organism_Antibiotic",
            index=False
        )

        mdr_data.to_excel(
            writer,
            sheet_name="MDR_Data",
            index=False
        )

        mdr_summary.to_excel(
            writer,
            sheet_name="MDR_Summary",
            index=False
        )

        mdr_organism.to_excel(
            writer,
            sheet_name="MDR_by_Organism",
            index=False
        )

        mdr_specimen.to_excel(
            writer,
            sheet_name="MDR_by_Specimen",
            index=False
        )

    return output_file, None

import sqlite3
import pandas as pd

from database import DATABASE_PATH


# ---------------------------------------------------------
# Antimicrobial class mapping
# ---------------------------------------------------------
#
# This is a project configuration.
# Verify the classification against the methodology and
# antimicrobial panel used in your actual study.
# ---------------------------------------------------------

ANTIBIOTIC_CLASSES = {

    "Amikacin": "Aminoglycosides",
    "Gentamicin": "Aminoglycosides",

    "Ciprofloxacin": "Fluoroquinolones",
    "Levofloxacin": "Fluoroquinolones",
    "Ofloxacin": "Fluoroquinolones",

    "Cefepime": "Cephalosporins",
    "Ceftazidime": "Cephalosporins",

    "Piperacillin-Tazobactam": "Penicillins",

    "Imipenem": "Carbapenems",
    "Meropenem": "Carbapenems",

    "Aztreonam": "Monobactams"
}


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

def load_ast_data():

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
            a.interpretation
        FROM samples s
        JOIN isolates i
            ON s.sample_id = i.sample_id
        JOIN ast_results a
            ON i.isolate_id = a.isolate_id
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data


# ---------------------------------------------------------
# Add antimicrobial class
# ---------------------------------------------------------

def add_antimicrobial_class(data):

    data = data.copy()

    data["antimicrobial_class"] = (
        data["antibiotic"]
        .map(ANTIBIOTIC_CLASSES)
        .fillna("Unknown")
    )

    return data


# ---------------------------------------------------------
# Calculate resistant classes
# ---------------------------------------------------------

def calculate_resistant_classes(data):

    data = add_antimicrobial_class(data)

    # Only resistance is counted.
    resistant = data[
        data["interpretation"].str.upper() == "R"
    ].copy()

    # Count unique antimicrobial classes per isolate.
    resistant_classes = (
        resistant
        .groupby("isolate_id")["antimicrobial_class"]
        .nunique()
        .reset_index()
    )

    resistant_classes.rename(
        columns={
            "antimicrobial_class":
            "resistant_class_count"
        },
        inplace=True
    )

    return resistant_classes


# ---------------------------------------------------------
# Create isolate-level MDR dataset
# ---------------------------------------------------------

def create_mdr_dataset():

    data = load_ast_data()

    if data.empty:
        return pd.DataFrame()

    resistant_classes = calculate_resistant_classes(data)

    isolate_info = (
        data[
            [
                "isolate_id",
                "sample_id",
                "patient_id",
                "age",
                "sex",
                "specimen",
                "ward",
                "collection_date",
                "organism"
            ]
        ]
        .drop_duplicates()
    )

    result = isolate_info.merge(
        resistant_classes,
        on="isolate_id",
        how="left"
    )

    result["resistant_class_count"] = (
        result["resistant_class_count"]
        .fillna(0)
        .astype(int)
    )

    return result


# ---------------------------------------------------------
# MDR classification
# ---------------------------------------------------------

def classify_mdr(
    resistant_class_count,
    threshold=3
):

    if resistant_class_count >= threshold:
        return "MDR"

    return "Non-MDR"


def add_mdr_classification(
    data,
    threshold=3
):

    data = data.copy()

    data["MDR_status"] = (
        data["resistant_class_count"]
        .apply(
            lambda x: classify_mdr(
                x,
                threshold
            )
        )
    )

    return data


# ---------------------------------------------------------
# MDR summary
# ---------------------------------------------------------

def create_mdr_summary(
    data,
    threshold=3
):

    if data.empty:
        return pd.DataFrame()

    data = add_mdr_classification(
        data,
        threshold
    )

    summary = (
        data["MDR_status"]
        .value_counts()
        .reset_index()
    )

    summary.columns = [
        "MDR_status",
        "Isolates"
    ]

    total = summary["Isolates"].sum()

    summary["Percentage"] = (
        summary["Isolates"] / total * 100
    ).round(2)

    return summary


# ---------------------------------------------------------
# MDR by organism
# ---------------------------------------------------------

def mdr_by_organism(
    data,
    threshold=3
):

    if data.empty:
        return pd.DataFrame()

    data = add_mdr_classification(
        data,
        threshold
    )

    table = pd.crosstab(
        data["organism"],
        data["MDR_status"]
    )

    table["Total"] = table.sum(axis=1)

    if "MDR" not in table.columns:
        table["MDR"] = 0

    table["MDR_percentage"] = (
        table["MDR"] /
        table["Total"] * 100
    ).round(2)

    return table.reset_index()


# ---------------------------------------------------------
# MDR by specimen
# ---------------------------------------------------------

def mdr_by_specimen(
    data,
    threshold=3
):

    if data.empty:
        return pd.DataFrame()

    data = add_mdr_classification(
        data,
        threshold
    )

    table = pd.crosstab(
        data["specimen"],
        data["MDR_status"]
    )

    table["Total"] = table.sum(axis=1)

    if "MDR" not in table.columns:
        table["MDR"] = 0

    table["MDR_percentage"] = (
        table["MDR"] /
        table["Total"] * 100
    ).round(2)

    return table.reset_index()

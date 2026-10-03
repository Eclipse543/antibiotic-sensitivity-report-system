import sqlite3
import pandas as pd

from database import DATABASE_PATH


# ---------------------------------------------------------
# Load complete dataset
# ---------------------------------------------------------

def load_complete_data():

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

            a.ast_id,
            a.antibiotic,
            a.zone_diameter,
            a.interpretation

        FROM samples s

        LEFT JOIN isolates i
            ON s.sample_id = i.sample_id

        LEFT JOIN ast_results a
            ON i.isolate_id = a.isolate_id
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data


# ---------------------------------------------------------
# Check missing sample information
# ---------------------------------------------------------

def check_missing_sample_data(data):

    issues = []

    for _, row in data.iterrows():

        if pd.isna(row["patient_id"]) or str(
            row["patient_id"]
        ).strip() == "":
            issues.append({
                "Sample_ID": row["sample_id"],
                "Issue": "Missing patient ID"
            })

        if pd.isna(row["specimen"]) or str(
            row["specimen"]
        ).strip() == "":
            issues.append({
                "Sample_ID": row["sample_id"],
                "Issue": "Missing specimen"
            })

        if pd.notna(row["age"]):

            try:
                age = float(row["age"])

                if age < 0 or age > 120:
                    issues.append({
                        "Sample_ID": row["sample_id"],
                        "Issue": "Age outside expected range"
                    })

            except ValueError:

                issues.append({
                    "Sample_ID": row["sample_id"],
                    "Issue": "Invalid age"
                })

    return issues


# ---------------------------------------------------------
# Check organism information
# ---------------------------------------------------------

def check_organism_data(data):

    issues = []

    isolates = (
        data[
            [
                "sample_id",
                "isolate_id",
                "organism"
            ]
        ]
        .drop_duplicates()
    )

    for _, row in isolates.iterrows():

        if pd.isna(row["organism"]) or str(
            row["organism"]
        ).strip() == "":

            issues.append({
                "Sample_ID": row["sample_id"],
                "Isolate_ID": row["isolate_id"],
                "Issue": "Missing organism"
            })

    return issues


# ---------------------------------------------------------
# Check AST interpretation
# ---------------------------------------------------------

def check_ast_interpretation(data):

    issues = []

    valid_results = {
        "S",
        "I",
        "R"
    }

    ast_data = data[
        data["ast_id"].notna()
    ]

    for _, row in ast_data.iterrows():

        result = str(
            row["interpretation"]
        ).strip().upper()

        if result not in valid_results:

            issues.append({
                "Sample_ID": row["sample_id"],
                "Isolate_ID": row["isolate_id"],
                "Antibiotic": row["antibiotic"],
                "Issue": (
                    "Invalid AST interpretation"
                )
            })

    return issues


# ---------------------------------------------------------
# Check duplicate antibiotic results
# ---------------------------------------------------------

def check_duplicate_ast(data):

    issues = []

    ast_data = data[
        data["ast_id"].notna()
    ]

    duplicates = (
        ast_data
        .groupby(
            [
                "isolate_id",
                "antibiotic"
            ]
        )
        .size()
        .reset_index(
            name="count"
        )
    )

    duplicates = duplicates[
        duplicates["count"] > 1
    ]

    for _, row in duplicates.iterrows():

        issues.append({
            "Isolate_ID": row["isolate_id"],
            "Antibiotic": row["antibiotic"],
            "Issue": (
                "Duplicate antibiotic result"
            ),
            "Count": row["count"]
        })

    return issues


# ---------------------------------------------------------
# Check missing AST results
# ---------------------------------------------------------

def check_missing_ast(data):

    issues = []

    isolates = (
        data[
            [
                "sample_id",
                "isolate_id",
                "organism"
            ]
        ]
        .drop_duplicates()
    )

    for _, isolate in isolates.iterrows():

        isolate_id = isolate["isolate_id"]

        if pd.isna(isolate_id):
            continue

        ast_count = data[
            data["isolate_id"] == isolate_id
        ]["ast_id"].notna().sum()

        if ast_count == 0:

            issues.append({
                "Sample_ID": isolate["sample_id"],
                "Isolate_ID": isolate_id,
                "Issue": "No AST results recorded"
            })

    return issues


# ---------------------------------------------------------
# Check duplicate samples
# ---------------------------------------------------------

def check_duplicate_samples(data):

    issues = []

    sample_counts = (
        data[
            ["sample_id"]
        ]
        .drop_duplicates()
        .groupby("sample_id")
        .size()
    )

    # This normally will not detect duplicates in the
    # samples table because sample_id is a PRIMARY KEY.
    # It is retained as a general QC check.

    for sample_id, count in sample_counts.items():

        if count > 1:

            issues.append({
                "Sample_ID": sample_id,
                "Issue": "Duplicate sample record"
            })

    return issues


# ---------------------------------------------------------
# Run complete quality-control analysis
# ---------------------------------------------------------

def run_quality_control():

    data = load_complete_data()

    if data.empty:
        return pd.DataFrame([
            {
                "Issue": "No data available",
                "Sample_ID": ""
            }
        ])

    all_issues = []

    all_issues.extend(
        check_missing_sample_data(data)
    )

    all_issues.extend(
        check_organism_data(data)
    )

    all_issues.extend(
        check_ast_interpretation(data)
    )

    all_issues.extend(
        check_duplicate_ast(data)
    )

    all_issues.extend(
        check_missing_ast(data)
    )

    all_issues.extend(
        check_duplicate_samples(data)
    )

    if not all_issues:

        return pd.DataFrame([
            {
                "Status": "PASS",
                "Issue": "No data-quality problems detected"
            }
        ])

    return pd.DataFrame(all_issues)


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n===== DATA QUALITY CONTROL =====\n")

    results = run_quality_control()

    print(results.to_string(index=False))

import os

import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact

from resistance_analysis import (
    create_mdr_dataset,
    add_mdr_classification
)


# ---------------------------------------------------------
# Directories
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# ---------------------------------------------------------
# Percentage
# ---------------------------------------------------------

def percentage(
    numerator,
    denominator
):

    if denominator == 0:
        return 0

    return round(
        (numerator / denominator) * 100,
        2
    )


# ---------------------------------------------------------
# 2 x 2 association test
# ---------------------------------------------------------

def association_test(
    data,
    exposure_column,
    outcome_column
):

    table = pd.crosstab(
        data[exposure_column],
        data[outcome_column]
    )

    # Only perform inferential test for 2 x 2 tables
    if table.shape != (2, 2):

        return {
            "Exposure": exposure_column,
            "Outcome": outcome_column,
            "Test": "Not applicable (>2 categories)",
            "Chi_square": None,
            "Fisher_exact": None,
            "P_value": None,
            "Significant": None
        }

    chi2, chi_p, dof, expected = (
        chi2_contingency(
            table
        )
    )

    odds_ratio, fisher_p = (
        fisher_exact(
            table
        )
    )

    # Use Fisher's exact test if any expected
    # cell count is less than 5.
    if (expected < 5).any():

        selected_test = "Fisher's exact test"
        p_value = fisher_p

    else:

        selected_test = "Chi-square test"
        p_value = chi_p

    return {
        "Exposure": exposure_column,
        "Outcome": outcome_column,
        "Test": selected_test,
        "Chi_square": round(
            chi2,
            4
        ),
        "Fisher_exact": round(
            fisher_p,
            4
        ),
        "P_value": round(
            p_value,
            4
        ),
        "Significant": (
            "Yes"
            if p_value < 0.05
            else "No"
        )
    }


# ---------------------------------------------------------
# MDR summary
# ---------------------------------------------------------

def create_mdr_statistical_summary(
    data
):

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
        summary["Isolates"]
        / total
        * 100
    ).round(2)

    return summary


# ---------------------------------------------------------
# MDR by variable
# ---------------------------------------------------------

def create_mdr_crosstab(
    data,
    column
):

    table = pd.crosstab(
        data[column],
        data["MDR_status"]
    )

    # Ensure both categories exist
    if "MDR" not in table.columns:
        table["MDR"] = 0

    if "Non-MDR" not in table.columns:
        table["Non-MDR"] = 0

    table["Total"] = (
        table["MDR"]
        + table["Non-MDR"]
    )

    table["MDR_percentage"] = (
        table["MDR"]
        / table["Total"]
        * 100
    ).round(2)

    return table.reset_index()


# ---------------------------------------------------------
# Age groups
# ---------------------------------------------------------

def add_age_group(
    data
):

    data = data.copy()

    data["age"] = pd.to_numeric(
        data["age"],
        errors="coerce"
    )

    def age_group(age):

        if pd.isna(age):
            return "Unknown"

        if age < 18:
            return "<18"

        if age <= 30:
            return "18-30"

        if age <= 45:
            return "31-45"

        if age <= 60:
            return "46-60"

        return ">60"

    data["age_group"] = (
        data["age"]
        .apply(age_group)
    )

    return data


# ---------------------------------------------------------
# Main statistical analysis
# ---------------------------------------------------------

def export_statistical_analysis():

    print(
        "Starting statistical analysis..."
    )

    # -----------------------------------------------------
    # Load isolate-level data
    # -----------------------------------------------------

    data = create_mdr_dataset()

    if data is None or data.empty:

        print(
            "No data available."
        )

        return None

    print(
        f"Loaded {len(data)} isolates."
    )

    # -----------------------------------------------------
    # Add MDR classification
    # -----------------------------------------------------

    data = add_mdr_classification(
        data,
        threshold=3
    )

    # Add age group
    data = add_age_group(
        data
    )

    print(
        "\nMDR classification:"
    )

    print(
        data[
            [
                "isolate_id",
                "organism",
                "resistant_class_count",
                "MDR_status"
            ]
        ].to_string(index=False)
    )

    # -----------------------------------------------------
    # MDR summary
    # -----------------------------------------------------

    mdr_summary = (
        create_mdr_statistical_summary(
            data
        )
    )

    # -----------------------------------------------------
    # MDR by organism
    # -----------------------------------------------------

    mdr_organism = create_mdr_crosstab(
        data,
        "organism"
    )

    # -----------------------------------------------------
    # MDR by specimen
    # -----------------------------------------------------

    mdr_specimen = create_mdr_crosstab(
        data,
        "specimen"
    )

    # -----------------------------------------------------
    # MDR by sex
    # -----------------------------------------------------

    mdr_sex = create_mdr_crosstab(
        data,
        "sex"
    )

    # -----------------------------------------------------
    # MDR by age group
    # -----------------------------------------------------

    mdr_age = create_mdr_crosstab(
        data,
        "age_group"
    )

    # -----------------------------------------------------
    # Association tests
    # -----------------------------------------------------

    association_results = []

    variables = [
        "organism",
        "specimen",
        "sex",
        "age_group"
    ]

    for variable in variables:

        if variable not in data.columns:
            continue

        result = association_test(
            data,
            variable,
            "MDR_status"
        )

        association_results.append(
            result
        )

    association_df = pd.DataFrame(
        association_results
    )

    # -----------------------------------------------------
    # Output file
    # -----------------------------------------------------

    output_file = os.path.join(
        REPORT_DIR,
        "Statistical_Analysis.xlsx"
    )

    # -----------------------------------------------------
    # Export Excel
    # -----------------------------------------------------

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        data.to_excel(
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

        mdr_sex.to_excel(
            writer,
            sheet_name="MDR_by_Sex",
            index=False
        )

        mdr_age.to_excel(
            writer,
            sheet_name="MDR_by_Age",
            index=False
        )

        association_df.to_excel(
            writer,
            sheet_name="Association_Tests",
            index=False
        )

    print(
        "\nStatistical analysis completed."
    )

    print(
        f"Excel file created:\n{output_file}"
    )

    return output_file


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    export_statistical_analysis()

import os
import pandas as pd

from excel_export import load_ast_data


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------
# Create organism-specific antibiogram
# ---------------------------------------------------------

def create_antibiogram():

    data = load_ast_data()

    if data.empty:
        return pd.DataFrame()

    data = data.copy()

    data["interpretation"] = (
        data["interpretation"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # One AST result per isolate-antibiotic combination
    data = (
        data[
            [
                "isolate_id",
                "organism",
                "antibiotic",
                "interpretation"
            ]
        ]
        .drop_duplicates()
    )

    rows = []

    for (organism, antibiotic), group in data.groupby(
        ["organism", "antibiotic"]
    ):

        total_tested = group["isolate_id"].nunique()

        susceptible = (
            group["interpretation"]
            .eq("S")
            .sum()
        )

        intermediate = (
            group["interpretation"]
            .eq("I")
            .sum()
        )

        resistant = (
            group["interpretation"]
            .eq("R")
            .sum()
        )

        rows.append({
            "Organism": organism,
            "Antibiotic": antibiotic,

            "Total Tested": total_tested,

            "S n": susceptible,
            "S %": round(
                susceptible / total_tested * 100,
                2
            ) if total_tested else 0,

            "I n": intermediate,
            "I %": round(
                intermediate / total_tested * 100,
                2
            ) if total_tested else 0,

            "R n": resistant,
            "R %": round(
                resistant / total_tested * 100,
                2
            ) if total_tested else 0
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# Create compact thesis table
# ---------------------------------------------------------

def create_compact_antibiogram():

    data = create_antibiogram()

    if data.empty:
        return pd.DataFrame()

    data["S n (%)"] = (
        data["S n"].astype(str)
        + " ("
        + data["S %"].astype(str)
        + "%)"
    )

    data["I n (%)"] = (
        data["I n"].astype(str)
        + " ("
        + data["I %"].astype(str)
        + "%)"
    )

    data["R n (%)"] = (
        data["R n"].astype(str)
        + " ("
        + data["R %"].astype(str)
        + "%)"
    )

    return data[
        [
            "Organism",
            "Antibiotic",
            "Total Tested",
            "S n (%)",
            "I n (%)",
            "R n (%)"
        ]
    ]


# ---------------------------------------------------------
# Create organism-specific tables
# ---------------------------------------------------------

def create_tables_by_organism():

    data = create_antibiogram()

    if data.empty:
        return {}

    tables = {}

    for organism, group in data.groupby(
        "Organism"
    ):

        table = group[
            [
                "Antibiotic",
                "Total Tested",
                "S n",
                "S %",
                "I n",
                "I %",
                "R n",
                "R %"
            ]
        ].copy()

        tables[organism] = table

    return tables


# ---------------------------------------------------------
# Export antibiogram to Excel
# ---------------------------------------------------------

def export_antibiogram():

    output_file = os.path.join(
        OUTPUT_DIR,
        "Antibiogram.xlsx"
    )

    tables = create_tables_by_organism()

    if not tables:
        print("No AST data available.")
        return None

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        # Complete table
        create_antibiogram().to_excel(
            writer,
            sheet_name="Complete_Antibiogram",
            index=False
        )

        # Compact thesis version
        create_compact_antibiogram().to_excel(
            writer,
            sheet_name="Thesis_Antibiogram",
            index=False
        )

        # Separate organism sheets
        for organism, table in tables.items():

            # Excel sheet names cannot exceed 31 characters
            sheet_name = organism[:31]

            table.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

    print(
        "Antibiogram generated:"
    )

    print(output_file)

    return output_file


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":

    export_antibiogram()

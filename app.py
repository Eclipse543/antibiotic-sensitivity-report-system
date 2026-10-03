import sqlite3
from excel_export import export_to_excel
from results import ResultsWindow
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import get_connection, initialize_database
from breakpoints import interpret_zone
from dashboard import DashboardWindow


# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

initialize_database()


# ---------------------------------------------------------
# Main window
# ---------------------------------------------------------

root = tk.Tk()

root.title("Antibiotic Sensitivity Report System")
root.geometry("1000x700")
root.minsize(900, 600)


# ---------------------------------------------------------
# Variables
# ---------------------------------------------------------

sample_id_var = tk.StringVar()
patient_id_var = tk.StringVar()
age_var = tk.StringVar()
sex_var = tk.StringVar()
specimen_var = tk.StringVar()
ward_var = tk.StringVar()
collection_date_var = tk.StringVar(
    value=str(date.today())
)

organism_var = tk.StringVar()

antibiotic_var = tk.StringVar()
zone_var = tk.StringVar()
interpretation_var = tk.StringVar()


# ---------------------------------------------------------
# Store AST entries before saving
# ---------------------------------------------------------

ast_entries = []


# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------

def export_excel():

    file, error = export_to_excel()

    if error:

        messagebox.showwarning(
            "Export",
            error
        )

        return

    messagebox.showinfo(
        "Excel Export",
        f"Excel report created successfully.\n\n{file}"
    )


def add_ast_result():

    antibiotic = antibiotic_var.get().strip()
    zone = zone_var.get().strip()
    interpretation = interpretation_var.get().strip()

    # Check antibiotic
    if not antibiotic:

        messagebox.showwarning(
            "Missing information",
            "Please select or enter an antibiotic."
        )

        return

    # Prevent duplicate antibiotic
    for result in ast_entries:

        if result["antibiotic"] == antibiotic:

            messagebox.showwarning(
                "Duplicate Antibiotic",
                f"{antibiotic} has already been added."
            )

            return

    # Check zone diameter
    if not zone:

        messagebox.showwarning(
            "Missing zone diameter",
            "Enter a zone diameter for automatic interpretation."
        )

        return

    try:

        zone_value = float(zone)

    except ValueError:

        messagebox.showerror(
            "Invalid value",
            "Zone diameter must be a number."
        )

        return

    # Check that zone is reasonable
    if zone_value < 0:

        messagebox.showerror(
            "Invalid value",
            "Zone diameter cannot be negative."
        )

        return

    # Automatically determine interpretation
    calculated_result = interpret_zone(
        organism_var.get().strip(),
        antibiotic,
        zone
    )

    if calculated_result:

        interpretation = calculated_result

        interpretation_var.set(
            calculated_result
        )

    else:

        messagebox.showwarning(
            "Breakpoint unavailable",
            "No verified breakpoint is configured for "
            "this organism/antibiotic combination."
        )

        return

    # Store AST result
    ast_entries.append({
        "antibiotic": antibiotic,
        "zone": zone,
        "interpretation": interpretation
    })

    # Add result to table
    ast_table.insert(
        "",
        "end",
        values=(
            antibiotic,
            zone,
            interpretation
        )
    )

    # Clear AST input fields
    antibiotic_var.set("")
    zone_var.set("")
    interpretation_var.set("")


def remove_ast_result():

    selected = ast_table.selection()

    if not selected:

        messagebox.showwarning(
            "No selection",
            "Select an AST result to remove."
        )

        return

    # Get indexes before deleting Treeview rows
    selected_indices = [
        ast_table.index(item)
        for item in selected
    ]

    # Delete from table
    for item in selected:

        ast_table.delete(item)

    # Delete from ast_entries
    for index in sorted(
        selected_indices,
        reverse=True
    ):

        del ast_entries[index]


def save_record():

    sample_id = sample_id_var.get().strip()
    patient_id = patient_id_var.get().strip()
    age = age_var.get().strip()
    sex = sex_var.get().strip()
    specimen = specimen_var.get().strip()
    ward = ward_var.get().strip()
    collection_date = collection_date_var.get().strip()
    organism = organism_var.get().strip()

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    if not sample_id:

        messagebox.showwarning(
            "Missing information",
            "Please enter Sample ID."
        )

        return

    if not patient_id:

        messagebox.showwarning(
            "Missing information",
            "Please enter Patient ID."
        )

        return

    if not specimen:

        messagebox.showwarning(
            "Missing information",
            "Please select specimen type."
        )

        return

    if not organism:

        messagebox.showwarning(
            "Missing information",
            "Please select bacterial organism."
        )

        return

    if not ast_entries:

        messagebox.showwarning(
            "Missing AST",
            "Please add at least one antibiotic result."
        )

        return

    # -----------------------------------------------------
    # Validate age
    # -----------------------------------------------------

    age_value = None

    if age:

        try:

            age_value = int(age)

        except ValueError:

            messagebox.showerror(
                "Invalid age",
                "Age must be a whole number."
            )

            return

    # -----------------------------------------------------
    # Database connection
    # -----------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -------------------------------------------------
        # Insert sample
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO samples (
                sample_id,
                patient_id,
                age,
                sex,
                specimen,
                ward,
                collection_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sample_id,
            patient_id,
            age_value,
            sex,
            specimen,
            ward,
            collection_date
        ))

        # -------------------------------------------------
        # Insert isolate
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO isolates (
                sample_id,
                organism
            )
            VALUES (?, ?)
        """, (
            sample_id,
            organism
        ))

        isolate_id = cursor.lastrowid

        # -------------------------------------------------
        # Insert AST results
        # -------------------------------------------------

        for result in ast_entries:

            zone = (
                float(result["zone"])
                if result["zone"]
                else None
            )

            try:

                cursor.execute("""
                    INSERT INTO ast_results (
                        isolate_id,
                        antibiotic,
                        zone_diameter,
                        interpretation
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    isolate_id,
                    result["antibiotic"],
                    zone,
                    result["interpretation"]
                ))

            except sqlite3.IntegrityError:

                messagebox.showerror(
                    "Duplicate AST Result",
                    f'{result["antibiotic"]} has already '
                    f'been entered for this isolate.'
                )

                connection.rollback()

                return

        # -------------------------------------------------
        # Commit everything
        # -------------------------------------------------

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Record saved successfully."
        )

        clear_form()

    except Exception as error:

        connection.rollback()

        messagebox.showerror(
            "Database error",
            f"Could not save record:\n\n{error}"
        )

    finally:

        connection.close()


def clear_form():

    sample_id_var.set("")
    patient_id_var.set("")
    age_var.set("")
    sex_var.set("")
    specimen_var.set("")
    ward_var.set("")

    collection_date_var.set(
        str(date.today())
    )

    organism_var.set("")

    antibiotic_var.set("")
    zone_var.set("")
    interpretation_var.set("")

    ast_entries.clear()

    for item in ast_table.get_children():

        ast_table.delete(item)


# ---------------------------------------------------------
# Title
# ---------------------------------------------------------

title_label = tk.Label(
    root,
    text="ANTIBIOTIC SENSITIVITY REPORT SYSTEM",
    font=("Arial", 18, "bold")
)

title_label.pack(
    pady=15
)


# ---------------------------------------------------------
# Sample information frame
# ---------------------------------------------------------

sample_frame = ttk.LabelFrame(
    root,
    text="Patient / Sample Information",
    padding=10
)

sample_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


# ---------------------------------------------------------
# Row 1
# ---------------------------------------------------------

ttk.Label(
    sample_frame,
    text="Sample ID:"
).grid(
    row=0,
    column=0,
    sticky="w",
    padx=5,
    pady=5
)

ttk.Entry(
    sample_frame,
    textvariable=sample_id_var,
    width=20
).grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)


ttk.Label(
    sample_frame,
    text="Patient ID:"
).grid(
    row=0,
    column=2,
    sticky="w",
    padx=5,
    pady=5
)

ttk.Entry(
    sample_frame,
    textvariable=patient_id_var,
    width=20
).grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


ttk.Label(
    sample_frame,
    text="Age:"
).grid(
    row=0,
    column=4,
    padx=5,
    pady=5
)

ttk.Entry(
    sample_frame,
    textvariable=age_var,
    width=10
).grid(
    row=0,
    column=5,
    padx=5,
    pady=5
)


# ---------------------------------------------------------
# Row 2
# ---------------------------------------------------------

ttk.Label(
    sample_frame,
    text="Sex:"
).grid(
    row=1,
    column=0,
    sticky="w",
    padx=5,
    pady=5
)

sex_combo = ttk.Combobox(
    sample_frame,
    textvariable=sex_var,
    values=[
        "Male",
        "Female",
        "Other"
    ],
    state="readonly",
    width=17
)

sex_combo.grid(
    row=1,
    column=1,
    padx=5,
    pady=5
)


ttk.Label(
    sample_frame,
    text="Specimen:"
).grid(
    row=1,
    column=2,
    sticky="w",
    padx=5,
    pady=5
)

specimen_combo = ttk.Combobox(
    sample_frame,
    textvariable=specimen_var,
    values=[
        "Blood",
        "Urine",
        "Sputum",
        "Wound Swab",
        "Pus",
        "Body Fluid",
        "Catheter Tip",
        "Other"
    ],
    width=17
)

specimen_combo.grid(
    row=1,
    column=3,
    padx=5,
    pady=5
)


ttk.Label(
    sample_frame,
    text="Ward:"
).grid(
    row=1,
    column=4,
    sticky="w",
    padx=5,
    pady=5
)

ttk.Entry(
    sample_frame,
    textvariable=ward_var,
    width=18
).grid(
    row=1,
    column=5,
    padx=5,
    pady=5
)


# ---------------------------------------------------------
# Row 3
# ---------------------------------------------------------

ttk.Label(
    sample_frame,
    text="Collection Date:"
).grid(
    row=2,
    column=0,
    sticky="w",
    padx=5,
    pady=5
)

ttk.Entry(
    sample_frame,
    textvariable=collection_date_var,
    width=20
).grid(
    row=2,
    column=1,
    padx=5,
    pady=5
)


# ---------------------------------------------------------
# Organism frame
# ---------------------------------------------------------

organism_frame = ttk.LabelFrame(
    root,
    text="Bacterial Identification",
    padding=10
)

organism_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


ttk.Label(
    organism_frame,
    text="Organism:"
).pack(
    side="left",
    padx=5
)


organism_combo = ttk.Combobox(
    organism_frame,
    textvariable=organism_var,
    values=[
        "Pseudomonas aeruginosa",
        "Acinetobacter calcoaceticus baumannii complex",
        "Burkholderia cepacia complex",
        "Stenotrophomonas maltophilia",
        "Other"
    ],
    width=35
)

organism_combo.pack(
    side="left",
    padx=5
)


# ---------------------------------------------------------
# AST entry frame
# ---------------------------------------------------------

ast_frame = ttk.LabelFrame(
    root,
    text="Antimicrobial Susceptibility Testing",
    padding=10
)

ast_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


ttk.Label(
    ast_frame,
    text="Antibiotic:"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)


antibiotic_combo = ttk.Combobox(
    ast_frame,
    textvariable=antibiotic_var,
    values=[
        "Amikacin",
        "Gentamicin",
        "Ciprofloxacin",
        "Levofloxacin",
        "Cefepime",
        "Ceftazidime",
        "Piperacillin-Tazobactam",
        "Imipenem",
        "Meropenem",
        "Aztreonam"
    ],
    width=25
)

antibiotic_combo.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)


ttk.Label(
    ast_frame,
    text="Zone (mm):"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)


ttk.Entry(
    ast_frame,
    textvariable=zone_var,
    width=10
).grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


ttk.Label(
    ast_frame,
    text="Result:"
).grid(
    row=0,
    column=6,
    padx=5,
    pady=5
)


interpretation_combo = ttk.Combobox(
    ast_frame,
    textvariable=interpretation_var,
    values=[
        "S",
        "I",
        "R"
    ],
    state="readonly",
    width=8
)

interpretation_combo.grid(
    row=0,
    column=7,
    padx=5,
    pady=5
)


ttk.Button(
    ast_frame,
    text="Add Result",
    command=add_ast_result
).grid(
    row=0,
    column=8,
    padx=10,
    pady=5
)


# ---------------------------------------------------------
# AST table
# ---------------------------------------------------------

table_frame = ttk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=5
)


columns = (
    "antibiotic",
    "zone",
    "interpretation"
)


ast_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=8
)


ast_table.heading(
    "antibiotic",
    text="Antibiotic"
)

ast_table.heading(
    "zone",
    text="Zone Diameter (mm)"
)

ast_table.heading(
    "interpretation",
    text="Interpretation"
)


ast_table.column(
    "antibiotic",
    width=250
)

ast_table.column(
    "zone",
    width=150,
    anchor="center"
)

ast_table.column(
    "interpretation",
    width=120,
    anchor="center"
)


ast_table.pack(
    side="left",
    fill="both",
    expand=True
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=ast_table.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)


ast_table.configure(
    yscrollcommand=scrollbar.set
)


# ---------------------------------------------------------
# Buttons
# ---------------------------------------------------------

button_frame = ttk.Frame(root)

button_frame.pack(
    pady=15
)


ttk.Button(
    button_frame,
    text="Remove Selected",
    command=remove_ast_result
).grid(
    row=0,
    column=0,
    padx=10
)


ttk.Button(
    button_frame,
    text="Save Record",
    command=save_record
).grid(
    row=0,
    column=1,
    padx=10
)


ttk.Button(
    button_frame,
    text="View Results",
    command=lambda: ResultsWindow(root)
).grid(
    row=0,
    column=2,
    padx=10
)


ttk.Button(
    button_frame,
    text="Clear Form",
    command=clear_form
).grid(
    row=0,
    column=3,
    padx=10
)


ttk.Button(
    button_frame,
    text="Exit",
    command=root.destroy
).grid(
    row=0,
    column=4,
    padx=10
)


ttk.Button(
    button_frame,
    text="Export Excel",
    command=export_excel
).grid(
    row=0,
    column=5,
    padx=10
)


# ---------------------------------------------------------
# Analysis Dashboard
# ---------------------------------------------------------

ttk.Button(
    root,
    text="Analysis Dashboard",
    command=lambda: DashboardWindow(root)
).pack(
    pady=5
)


# ---------------------------------------------------------
# Start application
# ---------------------------------------------------------

root.mainloop()


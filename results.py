import tkinter as tk
from tkinter import ttk, messagebox

from database import get_connection


class ResultsWindow:

    def __init__(self, parent):

        self.window = tk.Toplevel(parent)
        self.window.title("Search AST Results")
        self.window.geometry("1100x650")

        self.search_var = tk.StringVar()

        self.create_widgets()
        self.load_results()

    # -----------------------------------------------------
    # Interface
    # -----------------------------------------------------

    def create_widgets(self):

        search_frame = ttk.LabelFrame(
            self.window,
            text="Search",
            padding=10
        )

        search_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ttk.Label(
            search_frame,
            text="Sample / Patient ID:"
        ).pack(side="left", padx=5)

        ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        ).pack(side="left", padx=5)

        ttk.Button(
            search_frame,
            text="Search",
            command=self.search_results
        ).pack(side="left", padx=5)

        ttk.Button(
            search_frame,
            text="Show All",
            command=self.load_results
        ).pack(side="left", padx=5)

        # -------------------------------------------------
        # Results table
        # -------------------------------------------------

        table_frame = ttk.Frame(self.window)

        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        columns = (
            "sample_id",
            "patient_id",
            "specimen",
            "organism",
            "antibiotic",
            "zone",
            "interpretation"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "sample_id": "Sample ID",
            "patient_id": "Patient ID",
            "specimen": "Specimen",
            "organism": "Organism",
            "antibiotic": "Antibiotic",
            "zone": "Zone (mm)",
            "interpretation": "Result"
        }

        widths = {
            "sample_id": 100,
            "patient_id": 100,
            "specimen": 120,
            "organism": 200,
            "antibiotic": 170,
            "zone": 90,
            "interpretation": 80
        }

        for column in columns:

            self.table.heading(
                column,
                text=headings[column]
            )

            self.table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        button_frame = ttk.Frame(self.window)

        button_frame.pack(
            pady=10
        )

        ttk.Button(
            button_frame,
            text="View Selected",
            command=self.view_selected
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_selected
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy
        ).pack(side="left", padx=10)

    # -----------------------------------------------------
    # Load all results
    # -----------------------------------------------------

    def load_results(self):

        for item in self.table.get_children():
            self.table.delete(item)

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                s.sample_id,
                s.patient_id,
                s.specimen,
                i.organism,
                a.antibiotic,
                a.zone_diameter,
                a.interpretation
            FROM samples s
            JOIN isolates i
                ON s.sample_id = i.sample_id
            JOIN ast_results a
                ON i.isolate_id = a.isolate_id
            ORDER BY s.collection_date DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        connection.close()

        for row in rows:
            self.table.insert(
                "",
                "end",
                values=row
            )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    def search_results(self):

        search_text = self.search_var.get().strip()

        if not search_text:
            self.load_results()
            return

        for item in self.table.get_children():
            self.table.delete(item)

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                s.sample_id,
                s.patient_id,
                s.specimen,
                i.organism,
                a.antibiotic,
                a.zone_diameter,
                a.interpretation
            FROM samples s
            JOIN isolates i
                ON s.sample_id = i.sample_id
            JOIN ast_results a
                ON i.isolate_id = a.isolate_id
            WHERE
                s.sample_id LIKE ?
                OR s.patient_id LIKE ?
                OR i.organism LIKE ?
                OR s.specimen LIKE ?
            ORDER BY s.collection_date DESC
        """

        search_pattern = f"%{search_text}%"

        cursor.execute(
            query,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern
            )
        )

        rows = cursor.fetchall()

        connection.close()

        for row in rows:
            self.table.insert(
                "",
                "end",
                values=row
            )

    # -----------------------------------------------------
    # View selected
    # -----------------------------------------------------

    def view_selected(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "No selection",
                "Please select a result first."
            )

            return

        values = self.table.item(
            selected[0],
            "values"
        )

        details = f"""
Sample ID: {values[0]}
Patient ID: {values[1]}
Specimen: {values[2]}
Organism: {values[3]}

Antibiotic: {values[4]}
Zone Diameter: {values[5]} mm
Interpretation: {values[7]}
"""

        messagebox.showinfo(
            "AST Result",
            details
        )

    # -----------------------------------------------------
    # Delete selected
    # -----------------------------------------------------

    def delete_selected(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showwarning(
                "No selection",
                "Please select a result first."
            )

            return

        values = self.table.item(
            selected[0],
            "values"
        )

        sample_id = values[0]
        antibiotic = values[4]

        confirm = messagebox.askyesno(
            "Confirm deletion",
            f"Delete {antibiotic} result from "
            f"sample {sample_id}?"
        )

        if not confirm:
            return

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM ast_results
            WHERE ast_id = (
                SELECT a.ast_id
                FROM ast_results a
                JOIN isolates i
                    ON a.isolate_id = i.isolate_id
                WHERE i.sample_id = ?
                AND a.antibiotic = ?
                LIMIT 1
            )
        """, (sample_id, antibiotic))

        connection.commit()
        connection.close()

        self.load_results()

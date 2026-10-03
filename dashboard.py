import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import matplotlib.pyplot as plt

from database import DATABASE_PATH
from resistance_analysis import (
    load_ast_data,
    add_mdr_classification
)


class DashboardWindow:

    def __init__(self, parent):

        self.window = tk.Toplevel(parent)
        self.window.title("AST Analysis Dashboard")
        self.window.geometry("1000x700")

        self.create_interface()

        self.refresh_dashboard()

    # -------------------------------------------------
    # Interface
    # -------------------------------------------------

    def create_interface(self):

        title = ttk.Label(
            self.window,
            text="ANTIBIOTIC RESISTANCE ANALYSIS DASHBOARD",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=15)

        self.stats_frame = ttk.Frame(self.window)
        self.stats_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.cards = {}

        card_names = [
            "Total Isolates",
            "MDR Isolates"
        ]

        for i, name in enumerate(card_names):

            frame = ttk.LabelFrame(
                self.stats_frame,
                text=name
            )

            frame.grid(
                row=0,
                column=i,
                padx=5,
                sticky="nsew"
            )

            value = ttk.Label(
                frame,
                text="0",
                font=("Arial", 20, "bold")
            )

            value.pack(
                padx=20,
                pady=15
            )

            self.cards[name] = value

        for i in range(len(card_names)):
            self.stats_frame.columnconfigure(
                i,
                weight=1
            )

        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Organism Distribution",
            command=self.organism_chart
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Resistance by Antibiotic",
            command=self.resistance_chart
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_dashboard
        ).grid(row=0, column=3, padx=5)

        ttk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy
        ).grid(row=0, column=4, padx=5)

    # -------------------------------------------------
    # Dashboard statistics
    # -------------------------------------------------

    def refresh_dashboard(self):

        try:

            ast_data = load_ast_data()

            if ast_data.empty:
                self.set_all_zero()
                return

            # Unique isolates
            total_isolates = (
                ast_data["isolate_id"]
                .nunique()
            )

            # MDR
            mdr_data = add_mdr_classification(
                ast_data
            )

            mdr_isolates = (
                mdr_data[
                    mdr_data["MDR"] == "MDR"
                ]["isolate_id"]
                .nunique()
            )

            self.cards[
                "Total Isolates"
            ].config(
                text=str(total_isolates)
            )

            self.cards[
                "MDR Isolates"
            ].config(
     		text=str(total_isolates)
            )

        except Exception as error:

            messagebox.showerror(
                "Dashboard Error",
                str(error)
            )

    # -------------------------------------------------
    # Zero values
    # -------------------------------------------------

    def set_all_zero(self):

        for card in self.cards.values():
            card.config(text="0")

    # -------------------------------------------------
    # Organism chart
    # -------------------------------------------------

    def organism_chart(self):

        data = load_ast_data()

        if data.empty:
            messagebox.showinfo(
                "No Data",
                "No AST data available."
            )
            return

        organism_counts = (
            data[
                ["isolate_id", "organism"]
            ]
            .drop_duplicates()
            ["organism"]
            .value_counts()
        )

        plt.figure(figsize=(9, 6))

        organism_counts.plot(
            kind="bar"
        )

        plt.title(
            "Distribution of NFGNB Isolates"
        )

        plt.xlabel("Organism")
        plt.ylabel("Number of Isolates")

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()
        plt.show()

    # -------------------------------------------------
    # Resistance chart
    # -------------------------------------------------

    def resistance_chart(self):

        data = load_ast_data()

        if data.empty:
            messagebox.showinfo(
                "No Data",
                "No AST data available."
            )
            return

        resistance = (
            data[
                data["interpretation"]
                .astype(str)
                .str.upper()
                == "R"
            ]
            .groupby("antibiotic")
            ["isolate_id"]
            .nunique()
            .sort_values(
                ascending=False
            )
        )

        plt.figure(figsize=(9, 6))

        resistance.plot(
            kind="bar"
        )

        plt.title(
            "Number of Isolates Resistant to Each Antibiotic"
        )

        plt.xlabel("Antibiotic")
        plt.ylabel("Number of Resistant Isolates")

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()
        plt.show()

# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()

    DashboardWindow(root)

    root.mainloop()

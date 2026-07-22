"""
gui.py

The Tkinter GUI for LedgerWise. Contains only widget/display logic —
all data loading and calculations are imported from ledgerwise.py so
this file stays focused on presentation.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date

from Personal_Finance_Manager import load_all_data, track_budgets, forecast_budgets


class LedgerWiseApp:
    """
    Main application window for LedgerWise.
    Holds the notebook (tabbed interface) and creates each tab's frame.
    """
    def __init__(self, root, accounts_list, budgets_list, transactions_list):
        self.root = root
        self.root.title("LedgerWise")
        self.root.geometry("900x600")

        # Store the in-memory data so any tab-building method can access it
        self.accounts_list = accounts_list
        self.budgets_list = budgets_list
        self.transactions_list = transactions_list

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.budgets_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.budgets_tab, text="Budgets")
        self.notebook.add(self.reports_tab, text="Reports")

        self.build_dashboard_tab()
        self.build_transactions_tab()
        self.build_budgets_tab()
        self.build_reports_tab()

    def build_dashboard_tab(self):
        """
        Builds the Dashboard tab: this month's income, expenses, net
        cashflow, and a warning list of categories at risk of going
        over budget.
        """
        current_month = date.today().strftime("%Y-%m")

        # --- Calculate this month's totals from transactions_list ---
        income = 0.0
        expenses = 0.0
        for t in self.transactions_list:
            if t["Date"].strftime("%Y-%m") == current_month:
                if t["Amount"] > 0:
                    income += t["Amount"]
                else:
                    expenses += abs(t["Amount"])

        net_cashflow = income - expenses

        # --- Summary labels ---
        title = ttk.Label(self.dashboard_tab, text=f"Dashboard — {current_month}", font=("Arial", 16, "bold"))
        title.pack(pady=(20, 10))

        summary_frame = ttk.Frame(self.dashboard_tab)
        summary_frame.pack(pady=10)

        ttk.Label(summary_frame, text=f"Income: £{income:.2f}", font=("Arial", 12)).grid(row=0, column=0, padx=20)
        ttk.Label(summary_frame, text=f"Expenses: £{expenses:.2f}", font=("Arial", 12)).grid(row=0, column=1, padx=20)

        cashflow_colour = "green" if net_cashflow >= 0 else "red"
        ttk.Label(summary_frame, text=f"Net: £{net_cashflow:.2f}", font=("Arial", 12, "bold"),
                  foreground=cashflow_colour).grid(row=0, column=2, padx=20)

        # --- Budget warnings using existing tracking/forecasting logic ---
        status = track_budgets(self.transactions_list, self.budgets_list)
        forecast = forecast_budgets(status)

        warnings_label = ttk.Label(self.dashboard_tab, text="Budget Watch", font=("Arial", 13, "bold"))
        warnings_label.pack(pady=(20, 5))

        current_month_forecasts = [
            f for f in forecast
            if f["Month"] == current_month and f["Projected Over Budget"]
        ]

        if current_month_forecasts:
            for f in current_month_forecasts:
                warning_text = (
                    f"⚠️ {f['Category']}: on track to be £{f['Projected Overspend']:.2f} "
                    f"over budget by month-end"
                )
                ttk.Label(self.dashboard_tab, text=warning_text, foreground="red").pack(anchor="w", padx=40)
        else:
            ttk.Label(self.dashboard_tab, text="No categories currently at risk.", foreground="green").pack(padx=40)

    def build_transactions_tab(self):
        """Placeholder content for the Transactions tab."""
        label = ttk.Label(self.transactions_tab, text="Transactions — table will go here", font=("Arial", 14))
        label.pack(pady=20)

    def build_budgets_tab(self):
        """Placeholder content for the Budgets tab."""
        label = ttk.Label(self.budgets_tab, text="Budgets — progress bars will go here", font=("Arial", 14))
        label.pack(pady=20)

    def build_reports_tab(self):
        """Placeholder content for the Reports tab."""
        label = ttk.Label(self.reports_tab, text="Reports — charts will go here", font=("Arial", 14))
        label.pack(pady=20)


def main():
    # load_all_data() prints a clear message and exits (sys.exit(1)) if
    # any CSV is missing, malformed, or has the wrong columns — no need
    # to catch anything here, the GUI simply won't open on bad data.
    accounts_list, budgets_list, transactions_list = load_all_data(
        "accounts.csv", "budgets.csv", "transactions.csv"
    )

    root = tk.Tk()
    app = LedgerWiseApp(root, accounts_list, budgets_list, transactions_list)
    root.mainloop()


if __name__ == "__main__":
    main()
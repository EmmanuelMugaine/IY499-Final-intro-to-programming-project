"""
gui.py

The Tkinter GUI for LedgerWise. Contains only widget/display logic —
all data loading and calculations are imported from ledgerwise.py so
this file stays focused on presentation.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Personal_Finance_Manager import (
    load_all_data,
    track_budgets,
    forecast_budgets,
    merge_sort,
    binary_search,
    linear_search,
)


class LedgerWiseApp:
    # Main application window for LedgerWise.
    # Holds the notebook (tabbed interface) and creates each tab's frame.
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
        # Builds the Dashboard tab: this month's income, expenses, net
        # cashflow, and a warning list of categories at risk of going
        # over budget.
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
                    f" {f['Category']}: on track to be £{f['Projected Overspend']:.2f} "
                    f"over budget by month-end"
                )
                ttk.Label(self.dashboard_tab, text=warning_text, foreground="red").pack(anchor="w", padx=40)
        else:
            ttk.Label(self.dashboard_tab, text="No categories currently at risk.", foreground="green").pack(padx=40)

    def build_transactions_tab(self):
        # Builds the Transactions tab: a Treeview table of all transactions,
        # with column-header sorting (merge sort) and two search boxes —
        # an exact date lookup (binary search) and a free-text search
        # across Company Name / Description (linear search).

        # --- Search controls row ---
        controls_frame = ttk.Frame(self.transactions_tab)
        controls_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Date search (binary search — needs an exact YYYY-MM-DD match)
        ttk.Label(controls_frame, text="Find date (YYYY-MM-DD):").grid(row=0, column=0, padx=(0, 5))
        self.date_search_var = tk.StringVar()
        date_entry = ttk.Entry(controls_frame, textvariable=self.date_search_var, width=12)
        date_entry.grid(row=0, column=1, padx=(0, 5))
        ttk.Button(controls_frame, text="Go", command=self.search_by_date).grid(row=0, column=2, padx=(0, 20))

        # Text search (linear search — partial match on Company Name / Description)
        ttk.Label(controls_frame, text="Search company/description:").grid(row=0, column=3, padx=(0, 5))
        self.text_search_var = tk.StringVar()
        text_entry = ttk.Entry(controls_frame, textvariable=self.text_search_var, width=20)
        text_entry.grid(row=0, column=4, padx=(0, 5))
        ttk.Button(controls_frame, text="Go", command=self.search_by_text).grid(row=0, column=5, padx=(0, 20))

        ttk.Button(controls_frame, text="Show All", command=self.reset_transaction_table).grid(row=0, column=6)

        # --- Status label (row count / search feedback) ---
        self.transactions_status_var = tk.StringVar()
        ttk.Label(self.transactions_tab, textvariable=self.transactions_status_var,
                foreground="grey").pack(anchor="w", padx=10)

        # --- Table ---
        columns = ("Date", "Company Name", "Amount", "Category", "Description")
        self.transactions_tree = ttk.Treeview(
            self.transactions_tab, columns=columns, show="headings", height=18
        )

        for col in columns:
            # Only Date and Amount are sortable, per the brief's chosen scope.
            if col in ("Date", "Amount"):
                self.transactions_tree.heading(
                    col, text=col, command=lambda c=col: self.sort_transaction_table(c)
                )
            else:
                self.transactions_tree.heading(col, text=col)

        self.transactions_tree.column("Date", width=100, anchor="center")
        self.transactions_tree.column("Company Name", width=160)
        self.transactions_tree.column("Amount", width=90, anchor="e")
        self.transactions_tree.column("Category", width=110)
        self.transactions_tree.column("Description", width=220)

        self.transactions_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Show every transaction initially, sorted by Date
        self.reset_transaction_table()

    def populate_transaction_table(self, transactions):
        """
        Clears the Treeview and refills it with the given list of
        transaction dictionaries, in the order given.
        """
        self.transactions_tree.delete(*self.transactions_tree.get_children())

        for t in transactions:
            self.transactions_tree.insert("", "end", values=(
                t["Date"].strftime("%Y-%m-%d"),
                t["Company Name"],
                f"£{t['Amount']:.2f}",
                t["Category"],
                t["Description"],
            ))

        self.transactions_status_var.set(f"Showing {len(transactions)} transaction(s)")

    def sort_transaction_table(self, column):
        """
        Sorts the currently displayed transactions by the clicked
        column, using the custom merge_sort algorithm, and redraws
        the table.
        """
        key_functions = {
            "Date": lambda t: t["Date"],
            "Amount": lambda t: t["Amount"],
        }
        sorted_transactions = merge_sort(self.transactions_list, key=key_functions[column])
        self.transactions_list = sorted_transactions  # keep sort order for future searches too
        self.populate_transaction_table(sorted_transactions)

    def search_by_date(self):
        """
        Looks up an exact date using binary search. Requires the data
        to be sorted by Date first, so we sort immediately before
        searching (cheap for this dataset size, and guarantees
        correctness regardless of whatever order the table was in).
        """
        date_text = self.date_search_var.get().strip()
        try:
            target_date = date.fromisoformat(date_text)
        except ValueError:
            self.transactions_status_var.set(
                f"'{date_text}' is not a valid date — use YYYY-MM-DD."
            )
            return

        sorted_by_date = merge_sort(self.transactions_list, key=lambda t: t["Date"])
        matches = binary_search_all(sorted_by_date, target_date, key=lambda t: t["Date"])

        self.populate_transaction_table(matches)
        if not matches:
            self.transactions_status_var.set(f"No transactions found on {target_date}.")

    def search_by_text(self):
        """
        Searches Company Name and Description for the given text
        using linear search (no sorting required — text fields
        aren't suited to exact-match binary search).
        """
        search_text = self.text_search_var.get().strip()
        if not search_text:
            self.reset_transaction_table()
            return

        company_matches = linear_search(self.transactions_list, search_text, key=lambda t: t["Company Name"])
        description_matches = linear_search(self.transactions_list, search_text, key=lambda t: t["Description"])

        # Combine without duplicating transactions that match both fields
        combined = company_matches + [t for t in description_matches if t not in company_matches]

        self.populate_transaction_table(combined)
        if not combined:
            self.transactions_status_var.set(f"No transactions matching '{search_text}'.")

    def reset_transaction_table(self):
        """Clears search boxes and shows every transaction, sorted by Date."""
        self.date_search_var.set("")
        self.text_search_var.set("")
        sorted_transactions = merge_sort(self.transactions_list, key=lambda t: t["Date"])
        self.transactions_list = sorted_transactions
        self.populate_transaction_table(sorted_transactions)

    def build_budgets_tab(self):
        """
        Builds the Budgets tab: a dropdown to pick a month, and one
        progress bar per category showing amount spent vs budget.
        """
        # --- Work out which months have budget data, most recent first ---
        # Uses track_budgets() so this only lists months that actually
        # have spending recorded against a budgeted category.
        status = track_budgets(self.transactions_list, self.budgets_list)
        months_with_data = sorted({entry["Month"] for entry in status}, reverse=True)

        if not months_with_data:
            ttk.Label(self.budgets_tab, text="No budget data available.",
                      font=("Arial", 14)).pack(pady=20)
            return

        # --- Controls row: label + dropdown (same pattern as Reports tab) ---
        controls_frame = ttk.Frame(self.budgets_tab)
        controls_frame.pack(pady=(20, 10))

        ttk.Label(controls_frame, text="Month:", font=("Arial", 11)).pack(side="left", padx=(0, 8))

        self.budget_selected_month = tk.StringVar(value=months_with_data[0])
        month_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.budget_selected_month,
            values=months_with_data,
            state="readonly",
            width=10
        )
        month_dropdown.pack(side="left")
        month_dropdown.bind("<<ComboboxSelected>>", lambda event: self.draw_budget_bars())

        # --- Frame that will hold the progress bars, rebuilt on each redraw ---
        self.budget_bars_frame = ttk.Frame(self.budgets_tab)
        self.budget_bars_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.draw_budget_bars()

    def draw_budget_bars(self):
        """
        Draws (or redraws) one row per category for the selected month,
        each with a progress bar showing amount spent vs budget, and
        the remaining amount as text.
        """
        # Clear any previously drawn rows before redrawing
        for widget in self.budget_bars_frame.winfo_children():
            widget.destroy()

        selected_month = self.budget_selected_month.get()

        status = track_budgets(self.transactions_list, self.budgets_list)
        month_entries = [entry for entry in status if entry["Month"] == selected_month]

        # Sort categories alphabetically so the row order doesn't jump
        # around when switching between months
        month_entries = merge_sort(month_entries, key=lambda e: e["Category"])

        if not month_entries:
            ttk.Label(self.budget_bars_frame, text=f"No budgeted spending recorded for {selected_month}.",
                      font=("Arial", 12)).pack(pady=20)
            return

        for entry in month_entries:
            row_frame = ttk.Frame(self.budget_bars_frame)
            row_frame.pack(fill="x", pady=6)

            # Category name + remaining amount label
            label_frame = ttk.Frame(row_frame)
            label_frame.pack(fill="x")

            ttk.Label(label_frame, text=entry["Category"], font=("Arial", 11, "bold")).pack(side="left")

            if entry["Remaining"] >= 0:
                remaining_text = f"£{entry['Remaining']:.2f} left"
                remaining_colour = "green"
            else:
                remaining_text = f"£{abs(entry['Remaining']):.2f} over"
                remaining_colour = "red"

            ttk.Label(label_frame, text=f"£{entry['Spent']:.2f} / £{entry['Budgeted']:.2f}   ({remaining_text})",
                    foreground=remaining_colour).pack(side="right")

            # Progress bar — capped at 100 so overspending doesn't overflow the widget,
            # colour communicates the over-budget state instead
            progress_value = min(entry["Percent Used"], 100)
            style_name = f"{entry['Category']}.Horizontal.TProgressbar"

            style = ttk.Style()
            bar_colour = "red" if entry["Over Budget"] else "green"
            style.configure(style_name, troughcolor="#e0e0e0", background=bar_colour)

            progress_bar = ttk.Progressbar(
                row_frame, style=style_name, orient="horizontal",
                length=400, mode="determinate", value=progress_value
            )
            progress_bar.pack(fill="x", pady=(2, 0))

    def build_reports_tab(self):
        # Builds the Reports tab: a pie chart of spending by category,
        # with a dropdown to pick which month to view.

        # --- Work out which months actually have data, most recent first ---
        months_with_data = sorted(
            {t["Date"].strftime("%Y-%m") for t in self.transactions_list},
            reverse=True
        )

        if not months_with_data:
            ttk.Label(self.reports_tab, text="No transaction data available.",
                    font=("Arial", 14)).pack(pady=20)
            return

        # --- Controls row: label + dropdown ---
        controls_frame = ttk.Frame(self.reports_tab)
        controls_frame.pack(pady=(20, 10))

        ttk.Label(controls_frame, text="Month:", font=("Arial", 11)).pack(side="left", padx=(0, 8))

        self.selected_month = tk.StringVar(value=months_with_data[0])
        month_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.selected_month,
            values=months_with_data,
            state="readonly",  # user can only pick from the list, not type freely
            width=10
        )
        month_dropdown.pack(side="left")
        # Redraw the chart whenever a new month is selected
        month_dropdown.bind("<<ComboboxSelected>>", lambda event: self.draw_spending_pie_chart())

        # --- Frame that will hold the matplotlib canvas ---
        # Kept as its own frame (rather than reports_tab directly) so we can
        # destroy and rebuild just the chart on redraw, without touching the dropdown above.
        self.chart_frame = ttk.Frame(self.reports_tab)
        self.chart_frame.pack(fill="both", expand=True)

        self.draw_spending_pie_chart()

    def draw_spending_pie_chart(self):
        # Draws (or redraws) a pie chart of spending by category for
        # whichever month is currently selected in the dropdown.
        # Clear out any previously drawn chart before drawing a new one
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        selected_month = self.selected_month.get()

        # --- Sum expenses by category for the selected month ---
        category_totals = {}
        for t in self.transactions_list:
            if t["Date"].strftime("%Y-%m") == selected_month and t["Amount"] < 0:
                category = t["Category"]
                category_totals[category] = category_totals.get(category, 0.0) + abs(t["Amount"])

        if not category_totals:
            ttk.Label(self.chart_frame, text=f"No spending recorded for {selected_month}.",
                    font=("Arial", 12)).pack(pady=20)
            return

        # --- Build the pie chart ---
        figure = Figure(figsize=(6, 5), dpi=100)
        axes = figure.add_subplot(111)

        categories = list(category_totals.keys())
        amounts = list(category_totals.values())

        axes.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
        axes.set_title(f"Spending by Category — {selected_month}")

        # Embed the matplotlib figure inside the Tkinter frame
        canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


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
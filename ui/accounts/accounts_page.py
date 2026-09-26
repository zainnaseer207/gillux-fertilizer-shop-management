"""
ui/accounts/accounts_page.py

Accounts section: Cash Book tab + Expenses tab. Opening Cash yahan
se set hoti hai (ek dafa, phir Cash Book usko base bana kar calculate karta hai).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QLineEdit, QComboBox,
    QDoubleSpinBox, QDialog, QFormLayout, QMessageBox
)

from ui.accounts.bank_accounts_tab import BankAccountsTab
from utils.constants import MAX_AMOUNT
from utils.formatting import rs
from services.cashbook_service import get_cash_in_hand, get_cashbook_rows, set_opening_cash, get_opening_cash
from services.expense_service import add_expense, get_expenses
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER
from services.cashbook_service import get_payment_method_summary
from utils.permissions import is_admin
from services.bankbook_service import (
    get_bank_balance, get_bankbook_rows, set_opening_bank_balance, get_opening_bank_balance
)


class SetOpeningCashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Opening Cash")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(MAX_AMOUNT)
        self.amount_input.setPrefix("Rs. ")
        self.amount_input.setValue(get_opening_cash())
        layout.addWidget(QLabel("Opening Cash (shop mein maujood shuruati cash):"))
        layout.addWidget(self.amount_input)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

    def _save(self):
        set_opening_cash(self.amount_input.value())
        self.accept()

class SetOpeningBankDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Opening Bank Balance")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(MAX_AMOUNT)
        self.amount_input.setPrefix("Rs. ")
        self.amount_input.setValue(get_opening_bank_balance())
        layout.addWidget(QLabel("Opening Bank Balance:"))
        layout.addWidget(self.amount_input)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

    def _save(self):
        set_opening_bank_balance(self.amount_input.value())
        self.accept()


class BankBookTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        top_row = QHBoxLayout()
        self.balance_label = QLabel("")
        self.balance_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_PRIMARY};")
        top_row.addWidget(self.balance_label)
        top_row.addStretch()

        opening_btn = QPushButton("Set Opening Bank Balance")
        opening_btn.setVisible(is_admin(self.user))
        opening_btn.clicked.connect(self._open_opening_bank_dialog)
        top_row.addWidget(opening_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Amount In", "Amount Out", "Balance"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        balance = get_bank_balance()
        self.balance_label.setText(f"Bank Balance: Rs. {balance}")

        rows = get_bankbook_rows()
        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            date_text = r["date"].strftime("%Y-%m-%d") if r["date"] else "—"
            self.table.setItem(row, 0, QTableWidgetItem(date_text))
            self.table.setItem(row, 1, QTableWidgetItem(r["description"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{r['amount_in']}" if r["amount_in"] else ""))
            self.table.setItem(row, 3, QTableWidgetItem(f"{r['amount_out']}" if r["amount_out"] else ""))
            self.table.setItem(row, 4, QTableWidgetItem(f"{r['balance']}"))

    def _open_opening_bank_dialog(self):
        dialog = SetOpeningBankDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


class CashBookTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        top_row = QHBoxLayout()
        self.cash_label = QLabel("")
        self.cash_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_PRIMARY};")
        top_row.addWidget(self.cash_label)
        top_row.addStretch()

        opening_btn = QPushButton("Set Opening Cash")
        opening_btn.setVisible(is_admin(self.user))
        opening_btn.clicked.connect(self._open_opening_cash_dialog)
        top_row.addWidget(opening_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Cash In", "Cash Out"])
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Cash In", "Cash Out", "Balance"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        summary_heading = QLabel("Payment Method Summary (sab methods, sab waqt)")
        summary_heading.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(summary_heading)

        self.method_summary_table = QTableWidget()
        self.method_summary_table.setColumnCount(4)
        self.method_summary_table.setHorizontalHeaderLabels(["Method", "Total In", "Total Out", "Net"])
        self.method_summary_table.setFixedHeight(150)
        self.method_summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.method_summary_table)

    def refresh(self):
        cash = get_cash_in_hand()
        self.cash_label.setText(f"Cash in Hand: {rs(cash)}")

        rows = get_cashbook_rows()
        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            date_text = r["date"].strftime("%Y-%m-%d") if r["date"] else "—"
            self.table.setItem(row, 0, QTableWidgetItem(date_text))
            self.table.setItem(row, 1, QTableWidgetItem(r["description"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{rs(r['cash_in'])}" if r["cash_in"] else ""))
            self.table.setItem(row, 3, QTableWidgetItem(f"{rs(r['cash_out'])}" if r["cash_out"] else ""))
            self.table.setItem(row, 4, QTableWidgetItem(f"{rs(r['balance'])}" if r["balance"] else ""))

        method_rows = get_payment_method_summary()
        self.method_summary_table.setRowCount(len(method_rows))
        for row, m in enumerate(method_rows):
            self.method_summary_table.setItem(row, 0, QTableWidgetItem(m["method"]))
            self.method_summary_table.setItem(row, 1, QTableWidgetItem(f"{rs(m['total_in'])}"))
            self.method_summary_table.setItem(row, 2, QTableWidgetItem(f"{rs(m['total_out'])}"))
            self.method_summary_table.setItem(row, 3, QTableWidgetItem(f"{rs(m['net'])}" if m["net"] else ""))

    def _open_opening_cash_dialog(self):
        dialog = SetOpeningCashDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


class AddExpenseDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Add Expense")
        self.resize(350, 280)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(
            ["Electricity", "Transport", "Salary", "Shop Rent", "Loading/Unloading", "Maintenance", "Other"]
        )

        self.description_input = QLineEdit()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(MAX_AMOUNT)
        self.amount_input.setPrefix("Rs. ")

        self.method_input = QComboBox()
        self.method_input.addItems(["cash", "bank transfer", "other"])

        form.addRow("Category:", self.category_input)
        form.addRow("Description:", self.description_input)
        form.addRow("Amount:", self.amount_input)
        form.addRow("Payment Method:", self.method_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        layout.addWidget(self.error_label)

        save_btn = QPushButton("Save Expense")
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        try:
            add_expense(
                category=self.category_input.currentText(),
                description=self.description_input.text(),
                amount=self.amount_input.value(),
                payment_method=self.method_input.currentText(),
                user_id=self.user.id if self.user else None,
            )
        except ValueError as e:
            self.error_label.setText(str(e))
            return
        self.accept()


class ExpensesTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        top_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Category se search karein...")
        self.search_input.textChanged.connect(self.refresh)
        top_row.addWidget(self.search_input)

        add_btn = QPushButton("+ Add Expense")
        add_btn.setVisible(is_admin(self.user))
        add_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 6px 16px; font-weight: bold;"
        )
        add_btn.clicked.connect(self._open_add_dialog)
        top_row.addWidget(add_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount", "Method"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        expenses = get_expenses(self.search_input.text().strip())
        self.table.setRowCount(len(expenses))
        for row, e in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(e.expense_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 1, QTableWidgetItem(e.category))
            self.table.setItem(row, 2, QTableWidgetItem(e.description or ""))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {e.amount}"))
            self.table.setItem(row, 4, QTableWidgetItem(e.payment_method))

    def _open_add_dialog(self):
        dialog = AddExpenseDialog(self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


class AccountsPage(QWidget):
    def __init__(self, user):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        self.cashbook_tab = CashBookTab(user)
        self.bankbook_tab = BankBookTab(user)
        self.expenses_tab = ExpensesTab(user)

        tabs.addTab(self.cashbook_tab, "Cash Book")
        tabs.addTab(self.bankbook_tab, "Bank")
        tabs.addTab(self.expenses_tab, "Expenses")
        self.bank_tab = BankAccountsTab(user)
        tabs.addTab(self.bank_tab, "بینک اکاؤنٹس")

        tabs.currentChanged.connect(
            lambda i: (self.cashbook_tab.refresh(), self.expenses_tab.refresh(), self.bank_tab.refresh())
        )

    def refresh_data(self):
        self.cashbook_tab.refresh()
        self.bankbook_tab.refresh()
        self.expenses_tab.refresh()
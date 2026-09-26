"""
ui/accounts/bank_accounts_tab.py

Bank Accounts tab — har bank ka card (naam + balance), "+ نیا بینک
اکاؤنٹ" button, aur har card par "جمع کریں"/"نکالیں" buttons.
Upar "کل نقدی" summary (Cash in Hand + sab banks).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QPushButton,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)

from services.bank_service import (
    add_bank_account, get_accounts_with_balances, record_bank_transaction,
    get_account_history, get_total_cash_all_sources
)
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER, COLOR_BORDER, COLOR_TEXT_MUTED
from utils.constants import MAX_AMOUNT
from utils.formatting import rs
from utils.permissions import is_admin


class AddBankAccountDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("نیا بینک اکاؤنٹ")
        self.resize(350, 220)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثلاً: HBL Account")

        self.opening_input = QDoubleSpinBox()
        self.opening_input.setMaximum(MAX_AMOUNT)
        self.opening_input.setPrefix("Rs. ")

        form.addRow("اکاؤنٹ کا نام:", self.name_input)
        form.addRow("شروع کا بیلنس:", self.opening_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        layout.addWidget(self.error_label)

        save_btn = QPushButton("محفوظ کریں")
        save_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;")
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        try:
            add_bank_account(self.name_input.text(), self.opening_input.value(), self.user.id if self.user else None)
        except ValueError as e:
            self.error_label.setText(str(e))
            return
        self.accept()


class BankTransactionDialog(QDialog):
    def __init__(self, account_id, account_name, transaction_type, user, parent=None):
        super().__init__(parent)
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.user = user

        title = "رقم جمع کریں" if transaction_type == "deposit" else "رقم نکالیں"
        self.setWindowTitle(f"{title} — {account_name}")
        self.resize(350, 220)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(MAX_AMOUNT)
        self.amount_input.setPrefix("Rs. ")
        layout.addWidget(QLabel("رقم:"))
        layout.addWidget(self.amount_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("تفصیل (اختیاری)")
        layout.addWidget(self.description_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        save_btn = QPushButton("محفوظ کریں")
        save_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;")
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        try:
            record_bank_transaction(
                self.account_id, self.transaction_type, self.amount_input.value(),
                self.description_input.text().strip(), self.user.id if self.user else None,
            )
        except ValueError as e:
            self.error_label.setText(str(e))
            return
        self.accept()


class AccountHistoryDialog(QDialog):
    def __init__(self, account_id, account_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"لین دین کی تفصیل — {account_name}")
        self.resize(500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["تاریخ", "قسم", "رقم", "تفصیل"])
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        history = get_account_history(account_id)
        table.setRowCount(len(history))
        for row, txn in enumerate(history):
            table.setItem(row, 0, QTableWidgetItem(txn.created_at.strftime("%Y-%m-%d")))
            table.setItem(row, 1, QTableWidgetItem("جمع" if txn.transaction_type == "deposit" else "نکاسی"))
            table.setItem(row, 2, QTableWidgetItem(f"Rs. {txn.amount}"))
            table.setItem(row, 3, QTableWidgetItem(txn.description or ""))


class BankAccountCard(QFrame):
    def __init__(self, account_data, user, on_change_callback):
        super().__init__()
        self.account_data = account_data
        self.user = user
        self.on_change_callback = on_change_callback

        self.setStyleSheet(f"""
            QFrame {{ background-color: {COLOR_WHITE}; border: 1px solid {COLOR_BORDER}; border-radius: 8px; }}
        """)
        self.setFixedHeight(140)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        self.setLayout(layout)

        name_label = QLabel(account_data["name"])
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(name_label)

        balance_label = QLabel(f"Rs. {rs(account_data['balance'])}")
        balance_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLOR_PRIMARY};")
        layout.addWidget(balance_label)

        btn_row = QHBoxLayout()

        if is_admin(user):
            deposit_btn = QPushButton("جمع کریں")
            deposit_btn.clicked.connect(self._open_deposit)
            btn_row.addWidget(deposit_btn)

            withdraw_btn = QPushButton("نکالیں")
            withdraw_btn.clicked.connect(self._open_withdraw)
            btn_row.addWidget(withdraw_btn)

        history_btn = QPushButton("تفصیل")
        history_btn.clicked.connect(self._open_history)
        btn_row.addWidget(history_btn)

        layout.addLayout(btn_row)

    def _open_deposit(self):
        dialog = BankTransactionDialog(self.account_data["id"], self.account_data["name"], "deposit", self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.on_change_callback()

    def _open_withdraw(self):
        dialog = BankTransactionDialog(self.account_data["id"], self.account_data["name"], "withdraw", self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.on_change_callback()

    def _open_history(self):
        dialog = AccountHistoryDialog(self.account_data["id"], self.account_data["name"], self)
        dialog.exec()


class BankAccountsTab(QWidget):
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
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_PRIMARY};")
        top_row.addWidget(self.summary_label)
        top_row.addStretch()

        if is_admin(self.user):
            add_btn = QPushButton("+ نیا بینک اکاؤنٹ")
            add_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 6px 16px; font-weight: bold;")
            add_btn.clicked.connect(self._open_add_dialog)
            top_row.addWidget(add_btn)

        layout.addLayout(top_row)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(14)
        layout.addLayout(self.cards_grid)
        layout.addStretch()

    def refresh(self):
        totals = get_total_cash_all_sources()
        self.summary_label.setText(
            f"کل نقدی: {rs(totals['grand_total'])}   "
            f"(ہاتھ میں: {rs(totals['cash_in_hand'])}  +  بینکوں میں: {rs(totals['total_bank'])})"
        )

        # Purani cards hatate hain
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        accounts = get_accounts_with_balances()
        for i, account_data in enumerate(accounts):
            card = BankAccountCard(account_data, self.user, self.refresh)
            row, col = divmod(i, 3)
            self.cards_grid.addWidget(card, row, col)

    def _open_add_dialog(self):
        dialog = AddBankAccountDialog(self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()
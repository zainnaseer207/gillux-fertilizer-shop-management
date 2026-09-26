"""
ui/customers/ledger_dialog.py

Khaata (Ledger) — asal Urdu کھاتہ register ke columns ke mutabiq:
تاریخ | تفصیل | حوالہ | جمع | نکاس | بقایا
Modern spacing/styling ke sath, lekin tarteeb wahi register wali.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView, QFormLayout, QDoubleSpinBox,
    QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

from services.ledger_service import get_party_ledger, record_payment
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER
from utils.permissions import is_admin
from utils.translations import t
from utils.constants import MAX_AMOUNT
from utils.formatting import rs


class RecordPaymentDialog(QDialog):
    def __init__(self, party, user, parent=None):
        super().__init__(parent)
        self.party = party
        self.user = user

        title = t("Receive Payment") if party.is_customer else t("Pay Supplier")
        self.setWindowTitle(title)
        self.resize(380, 280)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(MAX_AMOUNT)
        self.amount_input.setPrefix("Rs. ")

        self.method_input = QComboBox()
        self.method_input.addItems(["نقد", "بینک ٹرانسفر", "چیک", "دیگر"])

        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("اختیاری (چیک نمبر، رسید نمبر وغیرہ)")

        form.addRow(f"{t('Amount')}:", self.amount_input)
        form.addRow("طریقہ:", self.method_input)
        form.addRow(f"{t('Reference')}:", self.reference_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        layout.addWidget(self.error_label)

        save_btn = QPushButton(t("Save"))
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        self.error_label.setText("")
        amount = self.amount_input.value()

        if amount <= 0:
            self.error_label.setText("رقم صفر سے زیادہ ہونی چاہیے۔")
            return

        direction = "receive" if self.party.is_customer else "pay"
        method_map = {"نقد": "cash", "بینک ٹرانسفر": "bank transfer", "چیک": "cheque", "دیگر": "other"}

        try:
            record_payment(
                party_id=self.party.id,
                direction=direction,
                amount=amount,
                payment_method=method_map.get(self.method_input.currentText(), "cash"),
                reference=self.reference_input.text().strip(),
                notes="",
                user_id=self.user.id if self.user else None,
            )
        except ValueError as e:
            self.error_label.setText(str(e))
            return

        self.accept()


class LedgerDialog(QDialog):
    def __init__(self, party_id, user, parent=None):
        super().__init__(parent)
        self.party_id = party_id
        self.user = user
        self.resize(850, 550)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # ---- Register-style heading ----
        heading_frame_layout = QVBoxLayout()
        self.title_label = QLabel(t("Khaata"))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 4px;")
        heading_frame_layout.addWidget(self.title_label)

        self.name_label = QLabel("")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet(f"font-size: 15px; color: {COLOR_PRIMARY}; font-weight: bold;")
        heading_frame_layout.addWidget(self.name_label)

        layout.addLayout(heading_frame_layout)

        top_row = QHBoxLayout()
        self.balance_label = QLabel("")
        self.balance_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_PRIMARY};")
        top_row.addWidget(self.balance_label)
        top_row.addStretch()

        self.payment_btn = QPushButton("")
        self.payment_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 6px 16px; font-weight: bold;"
        )
        self.payment_btn.clicked.connect(self._open_payment_dialog)
        top_row.addWidget(self.payment_btn)

        layout.addLayout(top_row)

        # ---- Register-pattern table: تاریخ | تفصیل | حوالہ | جمع | نکاس | بقایا ----
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            t("Date"), t("Description"), t("Reference"),
            t("Credit"), t("Debit"), t("Balance"),
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 12px; }
            QHeaderView::section {
                background-color: #E8F5E9;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #C8E6C9;
            }
        """)
        layout.addWidget(self.table)

    def refresh(self):
        ledger = get_party_ledger(self.party_id)
        self.party = ledger["party"]

        self.setWindowTitle(f"{t('Khaata')} — {self.party.name}")
        self.name_label.setText(f"{self.party.name} ({self.party.party_code})")
        self.payment_btn.setText(t("Receive Payment") if self.party.is_customer else t("Pay Supplier"))
        self.payment_btn.setVisible(is_admin(self.user))

        balance = ledger["final_balance"]
        balance_note = t("Receivable") if balance >= 0 else t("Payable")
        self.balance_label.setText(f"{t('Current Balance')}: {rs(abs(balance))} — {balance_note}")

        rows = ledger["rows"]
        self.table.setRowCount(len(rows))
        for row, entry in enumerate(rows):
            date_text = entry["date"].strftime("%Y-%m-%d") if entry["date"] else "—"
            self.table.setItem(row, 0, QTableWidgetItem(date_text))
            self.table.setItem(row, 1, QTableWidgetItem(entry["description"]))
            self.table.setItem(row, 2, QTableWidgetItem(entry["reference"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"{rs(entry['credit'])}" if entry["credit"] else ""))
            self.table.setItem(row, 4, QTableWidgetItem(f"{rs(entry['debit'])}" if entry["debit"] else ""))
            self.table.setItem(row, 5, QTableWidgetItem(f"{rs(entry['balance'])}" if entry["balance"] else ""))

    def _open_payment_dialog(self):
        dialog = RecordPaymentDialog(self.party, self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()
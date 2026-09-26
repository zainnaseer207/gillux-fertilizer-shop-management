"""
ui/reports/profit_report_page.py

Profit Report screen: date filter dropdown + custom range +
result cards (Sales, Discount, COGS, Gross Profit, Expenses, Net Profit).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QDateEdit, QGridLayout
)
from PySide6.QtCore import QDate

from services.profit_service import get_profit_report
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_BORDER, COLOR_TEXT_MUTED

FILTER_OPTIONS = [
    ("آج", "today"), ("کل", "yesterday"),
    ("اس ہفتے", "this_week"), ("اس مہینے", "this_month"), ("اپنی تاریخ", "custom"),
]

RESULT_FIELDS = [
    ("کل فروخت", "total_sales"),
    ("کل رعایت", "total_discount"),
    ("مال کی لاگت", "cogs"),
    ("مجموعی منافع", "gross_profit"),
    ("کل اخراجات", "total_expenses"),
    ("خالص منافع", "net_profit"),
]


class ResultCard(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{ background-color: {COLOR_WHITE}; border: 1px solid {COLOR_BORDER}; border-radius: 8px; }}
        """)
        self.setFixedHeight(90)
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        self.setLayout(layout)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        self.value_label = QLabel("Rs. 0")
        self.value_label.setStyleSheet(f"color: {COLOR_PRIMARY}; font-size: 20px; font-weight: bold;")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class ProfitReportPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        self.setLayout(layout)

        heading = QLabel("Profit Report")
        heading.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(heading)

        filter_row = QHBoxLayout()
        self.filter_input = QComboBox()
        for label, value in FILTER_OPTIONS:
            self.filter_input.addItem(label, value)
        self.filter_input.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(QLabel("Period:"))
        filter_row.addWidget(self.filter_input)

        self.from_date_input = QDateEdit(calendarPopup=True)
        self.from_date_input.setDate(QDate.currentDate())
        self.to_date_input = QDateEdit(calendarPopup=True)
        self.to_date_input.setDate(QDate.currentDate())
        self.from_date_input.setVisible(False)
        self.to_date_input.setVisible(False)
        filter_row.addWidget(QLabel("From:"))
        filter_row.addWidget(self.from_date_input)
        filter_row.addWidget(QLabel("To:"))
        filter_row.addWidget(self.to_date_input)

        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 6px 16px; font-weight: bold;"
        )
        apply_btn.clicked.connect(self.refresh)
        filter_row.addWidget(apply_btn)
        filter_row.addStretch()

        layout.addLayout(filter_row)

        self.invoice_count_label = QLabel("")
        self.invoice_count_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.invoice_count_label)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(16)
        layout.addLayout(self.cards_grid)

        self.cards = {}
        for i, (title, key) in enumerate(RESULT_FIELDS):
            card = ResultCard(title)
            self.cards[key] = card
            row, col = divmod(i, 3)
            self.cards_grid.addWidget(card, row, col)

        layout.addStretch()

    def _on_filter_changed(self):
        is_custom = self.filter_input.currentData() == "custom"
        self.from_date_input.setVisible(is_custom)
        self.to_date_input.setVisible(is_custom)

    def refresh(self):
        filter_value = self.filter_input.currentData()
        custom_from = self.from_date_input.date().toPython() if filter_value == "custom" else None
        custom_to = self.to_date_input.date().toPython() if filter_value == "custom" else None

        report = get_profit_report(filter_value, custom_from, custom_to)

        self.invoice_count_label.setText(f"{report['invoice_count']} invoice(s) is period mein")

        for key, card in self.cards.items():
            card.value_label.setText(f"Rs. {report[key]}")
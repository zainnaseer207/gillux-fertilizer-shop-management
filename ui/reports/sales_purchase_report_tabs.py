"""
ui/reports/sales_purchase_report_tabs.py — Urdu version
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import QDate

from services.report_service import get_sales_report, get_purchase_report
from utils.excel_exporter import export_to_excel
from utils.pdf_generator import generate_report_pdf
from ui.theme import COLOR_PRIMARY, COLOR_WHITE
from ui.widgets import show_empty_state

FILTER_OPTIONS = [
    ("آج", "today"), ("کل", "yesterday"),
    ("اس ہفتے", "this_week"), ("اس مہینے", "this_month"), ("اپنی تاریخ", "custom"),
]


class SalesReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("فروخت کی رپورٹ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("مدت:"))
        self.filter_input = QComboBox()
        self.filter_input.setFixedHeight(38)
        for label, value in FILTER_OPTIONS:
            self.filter_input.addItem(label, value)
        self.filter_input.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self.filter_input)

        self.from_date = QDateEdit(calendarPopup=True)
        self.from_date.setFixedHeight(38)
        self.from_date.setDate(QDate.currentDate())
        self.to_date = QDateEdit(calendarPopup=True)
        self.to_date.setFixedHeight(38)
        self.to_date.setDate(QDate.currentDate())
        self.from_date.setVisible(False)
        self.to_date.setVisible(False)
        filter_row.addWidget(self.from_date)
        filter_row.addWidget(self.to_date)

        apply_btn = QPushButton("دکھائیں")
        apply_btn.setFixedHeight(38)
        apply_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 0 16px; font-weight: bold; border-radius: 6px;")
        apply_btn.clicked.connect(self.refresh)
        filter_row.addWidget(apply_btn)

        export_btn = QPushButton("ایکسل میں محفوظ کریں")
        export_btn.setFixedHeight(38)
        export_btn.clicked.connect(self._export_pdf)
        filter_row.addWidget(export_btn)

        filter_row.addStretch()
        layout.addLayout(filter_row)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(f"font-weight: bold; color: {COLOR_PRIMARY}; font-size: 13px;")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["رسید نمبر", "گاہک", "تاریخ", "کل رقم", "ادا شدہ", "باقی"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def _on_filter_changed(self):
        is_custom = self.filter_input.currentData() == "custom"
        self.from_date.setVisible(is_custom)
        self.to_date.setVisible(is_custom)

    def refresh(self):
        filter_value = self.filter_input.currentData()
        custom_from = self.from_date.date().toPython() if filter_value == "custom" else None
        custom_to = self.to_date.date().toPython() if filter_value == "custom" else None

        report = get_sales_report(filter_value, custom_from, custom_to)
        t = report["totals"]
        self.summary_label.setText(
            f"کل فروخت: Rs. {t['total_sales']}   |   ادا شدہ: Rs. {t['total_paid']}   |   "
            f"ادھار: Rs. {t['total_credit']}   |   رعایت: Rs. {t['total_discount']}   |   "
            f"واپسی: Rs. {t['total_returns']}"
        )

        rows = report["rows"]
        if not rows:
            self.table.setRowCount(0)
            show_empty_state(self.table, "اس مدت میں کوئی فروخت نہیں ہوئی۔")
            return

        self.table.setRowCount(len(rows))
        for row, s in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(s.invoice_number))
            self.table.setItem(row, 1, QTableWidgetItem(s.customer.name if s.customer else ""))
            self.table.setItem(row, 2, QTableWidgetItem(s.sale_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {s.total}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs. {s.paid_amount}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rs. {s.remaining_amount}"))

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "sales_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        filter_value = self.filter_input.currentData()
        custom_from = self.from_date.date().toPython() if filter_value == "custom" else None
        custom_to = self.to_date.date().toPython() if filter_value == "custom" else None
        report = get_sales_report(filter_value, custom_from, custom_to)
        t = report["totals"]

        headers = ["Invoice #", "Customer", "Date", "Total", "Paid", "Remaining"]
        rows = []
        for s in report["rows"]:
            rows.append([
                s.invoice_number,
                s.customer.name if s.customer else "",
                s.sale_date.strftime("%Y-%m-%d"),
                f"Rs. {t and s.total or s.total}",
                f"Rs. {s.paid_amount}",
                f"Rs. {s.remaining_amount}",
            ])

        summary_text = (
            f"Total Sales: Rs. {t['total_sales']}   |   Paid: Rs. {t['total_paid']}   |   "
            f"Credit: Rs. {t['total_credit']}   |   Discount: Rs. {t['total_discount']}   |   "
            f"Returns: Rs. {t['total_returns']}"
        )

        generate_report_pdf("Sales Report", headers, rows, summary_text, path)
        QMessageBox.information(self, "Success", f"PDF saved:\n{path}")


class PurchaseReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("خریداری کی رپورٹ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("مدت:"))
        self.filter_input = QComboBox()
        self.filter_input.setFixedHeight(38)
        for label, value in FILTER_OPTIONS:
            self.filter_input.addItem(label, value)
        self.filter_input.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self.filter_input)

        self.from_date = QDateEdit(calendarPopup=True)
        self.from_date.setFixedHeight(38)
        self.from_date.setDate(QDate.currentDate())
        self.to_date = QDateEdit(calendarPopup=True)
        self.to_date.setFixedHeight(38)
        self.to_date.setDate(QDate.currentDate())
        self.from_date.setVisible(False)
        self.to_date.setVisible(False)
        filter_row.addWidget(self.from_date)
        filter_row.addWidget(self.to_date)

        apply_btn = QPushButton("دکھائیں")
        apply_btn.setFixedHeight(38)
        apply_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 0 16px; font-weight: bold; border-radius: 6px;")
        apply_btn.clicked.connect(self.refresh)
        filter_row.addWidget(apply_btn)

        export_btn = QPushButton("PDF بنائیں")
        export_btn.setFixedHeight(38)
        export_btn.clicked.connect(self._export_pdf)
        filter_row.addWidget(export_btn)

        filter_row.addStretch()
        layout.addLayout(filter_row)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(f"font-weight: bold; color: {COLOR_PRIMARY}; font-size: 13px;")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["خریداری نمبر", "سپلائر", "تاریخ", "کل رقم", "ادا شدہ", "باقی"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def _on_filter_changed(self):
        is_custom = self.filter_input.currentData() == "custom"
        self.from_date.setVisible(is_custom)
        self.to_date.setVisible(is_custom)

    def refresh(self):
        filter_value = self.filter_input.currentData()
        custom_from = self.from_date.date().toPython() if filter_value == "custom" else None
        custom_to = self.to_date.date().toPython() if filter_value == "custom" else None

        report = get_purchase_report(filter_value, custom_from, custom_to)
        t = report["totals"]
        self.summary_label.setText(
            f"کل خریداری: Rs. {t['total_purchases']}   |   ادا شدہ: Rs. {t['total_paid']}   |   "
            f"ادھار: Rs. {t['total_credit']}   |   واپسی: Rs. {t['total_returns']}"
        )

        rows = report["rows"]
        if not rows:
            self.table.setRowCount(0)
            show_empty_state(self.table, "اس مدت میں کوئی خریداری نہیں ہوئی۔")
            return

        self.table.setRowCount(len(rows))
        for row, p in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(p.purchase_number))
            self.table.setItem(row, 1, QTableWidgetItem(p.supplier.name if p.supplier else ""))
            self.table.setItem(row, 2, QTableWidgetItem(p.purchase_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {p.total}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs. {p.paid_amount}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rs. {p.remaining_amount}"))

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "purchase_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        filter_value = self.filter_input.currentData()
        custom_from = self.from_date.date().toPython() if filter_value == "custom" else None
        custom_to = self.to_date.date().toPython() if filter_value == "custom" else None
        report = get_purchase_report(filter_value, custom_from, custom_to)
        t = report["totals"]

        headers = ["Purchase #", "Supplier", "Date", "Total", "Paid", "Remaining"]
        rows = []
        for p in report["rows"]:
            rows.append([
                p.purchase_number,
                p.supplier.name if p.supplier else "",
                p.purchase_date.strftime("%Y-%m-%d"),
                f"Rs. {p.total}",
                f"Rs. {p.paid_amount}",
                f"Rs. {p.remaining_amount}",
            ])

        summary_text = (
            f"Total Purchases: Rs. {t['total_purchases']}   |   Paid: Rs. {t['total_paid']}   |   "
            f"Credit: Rs. {t['total_credit']}   |   Returns: Rs. {t['total_returns']}"
        )

        generate_report_pdf("Purchase Report", headers, rows, summary_text, path)
        QMessageBox.information(self, "Success", f"PDF saved:\n{path}")
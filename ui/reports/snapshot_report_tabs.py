"""
ui/reports/snapshot_report_tabs.py — Urdu version
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from utils.pdf_generator import generate_report_pdf

from services.report_service import get_stock_report, get_customer_report, get_supplier_report
from ui.theme import COLOR_PRIMARY
from ui.widgets import show_empty_state


class StockReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("اسٹاک کی رپورٹ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        top_row = QHBoxLayout()
        top_row.addStretch()
        export_btn = QPushButton("PDF بنائیں")
        export_btn.setFixedHeight(36)
        export_btn.clicked.connect(self._export_pdf)
        top_row.addWidget(export_btn)
        layout.addLayout(top_row)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(f"font-weight: bold; color: {COLOR_PRIMARY}; font-size: 13px;")
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["چیز", "اسٹاک", "اوسط قیمت", "اسٹاک کی مالیت", "فروخت کی مالیت", "متوقع منافع"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "stock_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        report_rows = get_stock_report()
        headers = ["Product", "Stock", "Avg Cost", "Stock Value", "Sale Value", "Est. Margin"]
        rows = []
        for r in report_rows:
            rows.append([
                r["product"].name, str(r["stock"]), f"Rs. {r['avg_cost']}",
                f"Rs. {r['stock_value']}", f"Rs. {r['sale_value']}", f"Rs. {r['estimated_margin']}",
            ])

        total_stock_value = sum(r["stock_value"] for r in report_rows)
        low_count = sum(1 for r in report_rows if r["is_low"])
        summary_text = f"Total Stock Value: Rs. {round(total_stock_value, 2)}   |   Low Stock Items: {low_count}"

        generate_report_pdf("Stock Report", headers, rows, summary_text, path)
        QMessageBox.information(self, "Success", f"PDF saved:\n{path}")

    def refresh(self):
        rows = get_stock_report()

        if not rows:
            self.table.setRowCount(0)
            show_empty_state(self.table, "ابھی تک کوئی چیز شامل نہیں ہوئی۔")
            return

        total_stock_value = sum(r["stock_value"] for r in rows)
        low_count = sum(1 for r in rows if r["is_low"])
        self.summary_label.setText(f"کل اسٹاک کی مالیت: Rs. {round(total_stock_value, 2)}   |   کم اسٹاک والی اشیاء: {low_count}")

        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(r["product"].name))
            self.table.setItem(row, 1, QTableWidgetItem(str(r["stock"])))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rs. {r['avg_cost']}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {r['stock_value']}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs. {r['sale_value']}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rs. {r['estimated_margin']}"))
            if r["is_low"]:
                for col in range(6):
                    self.table.item(row, col).setBackground(QColor("#FFEBEE"))


class CustomerReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("گاہک کی رپورٹ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        top_row = QHBoxLayout()
        top_row.addStretch()
        export_btn = QPushButton("PDF بنائیں")
        export_btn.setFixedHeight(36)
        export_btn.clicked.connect(self._export_pdf)
        top_row.addWidget(export_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["گاہک", "کل فروخت", "ادا شدہ", "بقایا"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "customer_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        report_rows = get_customer_report()
        headers = ["Customer", "Total Sales", "Paid", "Balance"]
        rows = []
        for r in report_rows:
            rows.append([
                r["party"].name, f"Rs. {r['total_sales']}",
                f"Rs. {r['total_paid']}", f"Rs. {r['balance']}",
            ])

        generate_report_pdf("Customer Report", headers, rows, "", path)
        QMessageBox.information(self, "Success", f"PDF saved:\n{path}")

    def refresh(self):
        rows = get_customer_report()

        if not rows:
            self.table.setRowCount(0)
            show_empty_state(self.table, "ابھی تک کوئی گاہک شامل نہیں ہوا۔")
            return

        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(r["party"].name))
            self.table.setItem(row, 1, QTableWidgetItem(f"Rs. {r['total_sales']}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rs. {r['total_paid']}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {r['balance']}"))


class SupplierReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("سپلائر کی رپورٹ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        top_row = QHBoxLayout()
        top_row.addStretch()
        export_btn = QPushButton("PDF بنائیں")
        export_btn.setFixedHeight(36)
        export_btn.clicked.connect(self._export_pdf)
        top_row.addWidget(export_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["سپلائر", "کل خریداری", "ادا شدہ", "بقایا"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "supplier_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        report_rows = get_supplier_report()
        headers = ["Supplier", "Total Purchases", "Paid", "Balance"]
        rows = []
        for r in report_rows:
            rows.append([
                r["party"].name, f"Rs. {r['total_purchases']}",
                f"Rs. {r['total_paid']}", f"Rs. {r['balance']}",
            ])

        generate_report_pdf("Supplier Report", headers, rows, "", path)
        QMessageBox.information(self, "Success", f"PDF saved:\n{path}")

    def refresh(self):
        rows = get_supplier_report()

        if not rows:
            self.table.setRowCount(0)
            show_empty_state(self.table, "ابھی تک کوئی سپلائر شامل نہیں ہوا۔")
            return

        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(r["party"].name))
            self.table.setItem(row, 1, QTableWidgetItem(f"Rs. {r['total_purchases']}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rs. {r['total_paid']}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {r['balance']}"))
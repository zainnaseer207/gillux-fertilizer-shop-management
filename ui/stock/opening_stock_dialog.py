"""
ui/stock/opening_stock_dialog.py

Sab products ki list dikhata hai — jin ka Opening Stock set nahi hua,
unke saamne "Set" button hota hai. Set ho jane ke baad "Already Set"
dikh jata hai (dobara set nahi karne dete, taake galti se double na ho).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QHeaderView, QMessageBox, QFormLayout, QDoubleSpinBox
)

from services.stock_service import get_products_for_opening_stock, set_opening_stock
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_TEXT_MUTED


class SetOpeningStockForm(QDialog):
    def __init__(self, product: dict, user_id: int, parent=None):
        super().__init__(parent)
        self.product = product
        self.user_id = user_id
        self.setWindowTitle(f"Opening Stock — {product['name']}")
        self.resize(350, 220)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setSuffix(f" {product['unit']}")

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMaximum(9999999)
        self.cost_input.setPrefix("Rs. ")

        form.addRow("Quantity:", self.quantity_input)
        form.addRow("Cost Price (per unit):", self.cost_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        save_btn = QPushButton("Save Opening Stock")
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        qty = self.quantity_input.value()
        cost = self.cost_input.value()

        if qty <= 0:
            self.error_label.setText("Quantity 0 se zyada honi chahiye.")
            return

        try:
            set_opening_stock(self.product["id"], qty, cost, self.user_id)
            self.accept()
        except ValueError as e:
            self.error_label.setText(str(e))


class OpeningStockDialog(QDialog):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Opening Stock")
        self.resize(750, 500)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        heading = QLabel("Opening Stock — Har product ka shuruati stock set karein")
        heading.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(heading)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Product search karein...")
        self.search_input.textChanged.connect(self.refresh)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Name", "Unit", "Current Stock", "Avg Cost", "Action"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        search_text = self.search_input.text().strip()
        self.products = get_products_for_opening_stock(search_text)

        self.table.setRowCount(len(self.products))
        for row, p in enumerate(self.products):
            self.table.setItem(row, 0, QTableWidgetItem(p["code"]))
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(p["unit"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(p["current_stock"])))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs. {p['avg_cost']}"))

            if p["already_set"]:
                done_label = QLabel("✓ Already Set")
                done_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
                self.table.setCellWidget(row, 5, done_label)
            else:
                set_btn = QPushButton("Set Opening Stock")
                set_btn.clicked.connect(lambda checked, product=p: self._open_set_form(product))
                self.table.setCellWidget(row, 5, set_btn)

    def _open_set_form(self, product: dict):
        dialog = SetOpeningStockForm(product, self.user_id, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()
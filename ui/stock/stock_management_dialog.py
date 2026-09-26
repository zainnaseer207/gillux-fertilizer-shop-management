"""
ui/stock/stock_management_dialog.py

3 tabs: Stock Overview (low stock red highlight), Stock Adjustment
(manual +/- correction), Stock History (saari movements).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QComboBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QTabWidget, QWidget, QTextEdit, QRadioButton, QButtonGroup
)

from services.stock_service import (
    get_all_products_with_stock, adjust_product_stock, get_stock_movement_history
)
from services.product_service import get_products
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER
from services.product_service import get_products
from services.stock_service import get_stock_movement_history, update_movement_description


class StockOverviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Product search karein...")
        self.search_input.textChanged.connect(self.refresh)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Code", "Name", "Current Stock", "Min Level", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        products = get_all_products_with_stock(self.search_input.text().strip())
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(p["code"]))
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p['current_stock']} {p['unit']}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(p["min_stock_level"])))

            status_item = QTableWidgetItem("⚠ Low Stock" if p["is_low"] else "OK")
            if p["is_low"]:
                status_item.setForeground(Qt.red) if False else None
            self.table.setItem(row, 4, status_item)

            if p["is_low"]:
                for col in range(5):
                    self.table.item(row, col).setBackground(_light_red())


def _light_red():
    from PySide6.QtGui import QColor
    return QColor("#FFEBEE")


from PySide6.QtCore import Qt


class StockAdjustmentTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()
        self._reload_products()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

        heading = QLabel("Manual Stock Adjustment (damaged / lost / counting correction)")
        heading.setStyleSheet("font-weight: bold;")
        layout.addWidget(heading)

        self.product_input = QComboBox()
        layout.addWidget(self.product_input)

        direction_row = QHBoxLayout()
        self.increase_radio = QRadioButton("Increase (+)")
        self.decrease_radio = QRadioButton("Decrease (-)")
        self.decrease_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self.increase_radio)
        group.addButton(self.decrease_radio)
        direction_row.addWidget(self.increase_radio)
        direction_row.addWidget(self.decrease_radio)
        layout.addLayout(direction_row)

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMaximum(999999)
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(self.quantity_input)

        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Reason likhein (e.g. 'Barish se 5 bags kharab hue')")
        self.reason_input.setFixedHeight(70)
        layout.addWidget(QLabel("Reason:"))
        layout.addWidget(self.reason_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        save_btn = QPushButton("Save Adjustment")
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

        layout.addStretch()

    def _reload_products(self):
        self.product_input.clear()
        self._products_cache = get_products()
        for p in self._products_cache:
            self.product_input.addItem(f"{p.name} (Current: {p.current_stock})", p.id)

    def _handle_save(self):
        self.error_label.setText("")
        product_id = self.product_input.currentData()
        quantity = self.quantity_input.value()
        reason = self.reason_input.toPlainText().strip()

        if product_id is None:
            self.error_label.setText("Product select karein.")
            return
        if quantity <= 0:
            self.error_label.setText("Quantity 0 se zyada honi chahiye.")
            return
        if not reason:
            self.error_label.setText("Reason likhna zaroori hai.")
            return

        delta = quantity if self.increase_radio.isChecked() else -quantity

        try:
            adjust_product_stock(product_id, delta, reason, self.user.id if self.user else None)
        except ValueError as e:
            self.error_label.setText(str(e))
            return

        QMessageBox.information(self, "Success", "Stock adjustment save ho gaya.")
        self.quantity_input.setValue(0)
        self.reason_input.clear()
        self._reload_products()

    def refresh_data(self):
        self._reload_products()


class StockHistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loading = False
        self._build_ui()
        self._reload_products()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

        heading = QLabel("سٹاک رجسٹر")
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(heading)

        hint = QLabel("نوٹ: 'تفصیل' کالم پر دوبار کلک کر کے اپنی مرضی کا نوٹ لکھ سکتے ہیں۔")
        hint.setStyleSheet("color: #888; font-size: 11px; margin-bottom: 6px;")
        layout.addWidget(hint)

        self.product_filter = QComboBox()
        self.product_filter.setFixedHeight(38)
        self.product_filter.currentIndexChanged.connect(self.refresh)
        layout.addWidget(self.product_filter)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "تاریخ", "تفصیل", "صفحہ", "نام اشیاء",
            "آمد (تعداد)", "نکاس (تعداد)", "بقایا", "کیفیت",
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 12.5px; gridline-color: #C8E6C9; }
            QHeaderView::section {
                background-color: #1B5E20; color: white; font-weight: bold;
                padding: 8px 4px; border: 1px solid #145214;
            }
            QTableWidget::item { padding: 4px; }
        """)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

    def _reload_products(self):
        self.product_filter.blockSignals(True)
        self.product_filter.clear()
        self.product_filter.addItem("تمام اشیاء", None)
        for p in get_products():
            self.product_filter.addItem(p.name, p.id)
        self.product_filter.blockSignals(False)

    def refresh(self):
        self._loading = True  # itemChanged signal ko temporarily block karta hai reload ke waqt

        product_id = self.product_filter.currentData()
        history = get_stock_movement_history(product_id)

        if not history:
            self.table.setRowCount(0)
            from ui.widgets import show_empty_state
            show_empty_state(self.table, "ابھی تک کوئی حرکت (آمد/نکاس) درج نہیں ہوئی۔")
            self._loading = False
            return

        self.table.setRowCount(len(history))
        for row, m in enumerate(history):
            date_item = QTableWidgetItem(m["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, date_item)

            # ---- تفصیل: agar user ne khud kuch likha ho (notes), wo dikhega,
            # warna default type-label (خریداری/فروخت وغیرہ) dikhega — aur ye EDITABLE hai
            description_text = m["notes"] if m["notes"] else self._describe_type(m["type"])
            description_item = QTableWidgetItem(description_text)
            description_item.setData(Qt.UserRole, m["id"])  # movement id yahan save karte hain save ke waqt ke liye
            self.table.setItem(row, 1, description_item)

            page_item = QTableWidgetItem("")
            page_item.setFlags(page_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, page_item)

            name_item = QTableWidgetItem(m["product"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, name_item)

            in_item = QTableWidgetItem(str(m["qty_in"]) if m["qty_in"] else "")
            in_item.setFlags(in_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, in_item)

            out_item = QTableWidgetItem(str(m["qty_out"]) if m["qty_out"] else "")
            out_item.setFlags(out_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 5, out_item)

            balance_item = QTableWidgetItem(str(m["balance_after"]))
            balance_item.setFlags(balance_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 6, balance_item)

            quality_item = QTableWidgetItem("ٹھیک")
            quality_item.setFlags(quality_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 7, quality_item)

        self._loading = False

    def _on_item_changed(self, item):
        # Sirf تفصیل column (index 1) editable hai — usi ke changes save karte hain
        if self._loading or item.column() != 1:
            return

        movement_id = item.data(Qt.UserRole)
        if movement_id is None:
            return

        update_movement_description(movement_id, item.text())

    def _describe_type(self, movement_type: str) -> str:
        labels = {
            "opening": "ابتدائی سٹاک",
            "purchase": "خریداری",
            "sale": "فروخت",
            "sale_return": "فروخت کی واپسی",
            "purchase_return": "خریداری کی واپسی",
            "adjustment": "ترمیم",
        }
        return labels.get(movement_type, movement_type)

    def refresh_data(self):
        self._reload_products()
        self.refresh()
"""
ui/products/product_page.py

Product List + Add Product dialog + Opening Stock access.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox, QHeaderView, QInputDialog
)

from services.product_service import (
    get_categories, add_category, get_units, add_unit,
    check_duplicate_product, add_product, get_products,
    edit_product, get_product_by_id
)
from utils.permissions import is_admin

from services.product_service import (
    get_categories, add_category, get_units, add_unit,
    check_duplicate_product, add_product, get_products
)
from ui.stock.opening_stock_dialog import OpeningStockDialog
from ui.theme import COLOR_PRIMARY, COLOR_WHITE
from ui.theme import fix_spinbox_rtl
from utils.constants import MAX_AMOUNT
from services.stock_service import set_opening_stock
from utils.formatting import rs

class AddProductDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("نئی چیز شامل کریں")
        self.resize(420, 560)
        self.saved_product = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.setLayout(layout)

        heading = QLabel("نئی چیز")
        heading.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(heading)

        layout.addWidget(self._label("چیز کا نام"))
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(42)
        self.name_input.setStyleSheet(self._input_style())
        self.name_input.setPlaceholderText("مثلاً: یوریا، ڈی اے پی")
        layout.addWidget(self.name_input)

        # ---- Category + Unit ek row mein, "+ نیا" chhote buttons ke sath ----
        cat_row = QHBoxLayout()
        cat_col = QVBoxLayout()
        cat_col.addWidget(self._label("قسم"))
        cat_inner = QHBoxLayout()
        self.category_input = QComboBox()
        self.category_input.setFixedHeight(42)
        self.category_input.setStyleSheet(self._input_style())
        self._reload_categories()
        cat_inner.addWidget(self.category_input)
        new_category_btn = QPushButton("+ نیا")
        new_category_btn.setFixedHeight(42)
        new_category_btn.clicked.connect(self._add_new_category)
        cat_inner.addWidget(new_category_btn)
        cat_col.addLayout(cat_inner)
        cat_row.addLayout(cat_col)
        layout.addLayout(cat_row)

        unit_col = QVBoxLayout()
        unit_col.addWidget(self._label("یونٹ (بوری، کلو وغیرہ)"))
        unit_inner = QHBoxLayout()
        self.unit_input = QComboBox()
        self.unit_input.setFixedHeight(42)
        self.unit_input.setStyleSheet(self._input_style())
        self._reload_units()
        unit_inner.addWidget(self.unit_input)
        new_unit_btn = QPushButton("+ نیا")
        new_unit_btn.setFixedHeight(42)
        new_unit_btn.clicked.connect(self._add_new_unit)
        unit_inner.addWidget(new_unit_btn)
        unit_col.addLayout(unit_inner)
        layout.addLayout(unit_col)

        # ---- Prices — sabse zaroori 2 fields bare ----
        prices_row = QHBoxLayout()
        purchase_col = QVBoxLayout()
        purchase_col.addWidget(self._label("خریداری کی قیمت"))
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setFixedHeight(42)
        self.purchase_price_input.setMaximum(MAX_AMOUNT)
        self.purchase_price_input.setPrefix("Rs. ")
        self.purchase_price_input.setStyleSheet(self._input_style())
        purchase_col.addWidget(self.purchase_price_input)
        prices_row.addLayout(purchase_col)

        layout.addWidget(self._label("ابتدائی مقدار (اگر پہلے سے موجود ہے)"))
        self.opening_quantity_input = QDoubleSpinBox()
        self.opening_quantity_input.setFixedHeight(42)
        self.opening_quantity_input.setMaximum(MAX_AMOUNT)
        self.opening_quantity_input.setStyleSheet(self._input_style())
        layout.addWidget(self.opening_quantity_input)

        hint = QLabel("اگر یہ چیز پہلے سے دکان میں موجود ہے تو یہاں مقدار لکھ دیں — سٹاک خود بن جائے گا۔")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

        sale_col = QVBoxLayout()
        sale_col.addWidget(self._label("فروخت کی قیمت"))
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setFixedHeight(42)
        self.sale_price_input.setMaximum(MAX_AMOUNT)
        self.sale_price_input.setPrefix("Rs. ")
        self.sale_price_input.setStyleSheet(self._input_style())
        sale_col.addWidget(self.sale_price_input)
        prices_row.addLayout(sale_col)
        layout.addLayout(prices_row)

        # ---- Baaki (min sale price, stock levels) "مزید تفصیل" ke peeche ----
        self.more_details_btn = QPushButton("مزید تفصیل ▾")
        self.more_details_btn.setFlat(True)
        self.more_details_btn.setStyleSheet(f"color: {COLOR_PRIMARY}; text-align: left; border: none; font-size: 12px;")
        self.more_details_btn.clicked.connect(self._toggle_more_details)
        layout.addWidget(self.more_details_btn)

        self.more_details_frame = QWidget()
        more_layout = QVBoxLayout()
        more_layout.setContentsMargins(0, 0, 0, 0)

        more_layout.addWidget(self._label("برانڈ / کمپنی"))
        self.brand_input = QLineEdit()
        self.brand_input.setStyleSheet(self._input_style())
        more_layout.addWidget(self.brand_input)

        more_layout.addWidget(self._label("کم از کم اسٹاک کی حد"))
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setMaximum(MAX_AMOUNT)
        self.min_stock_input.setStyleSheet(self._input_style())
        more_layout.addWidget(self.min_stock_input)

        self.min_sale_price_input = QDoubleSpinBox()
        self.min_sale_price_input.setMaximum(MAX_AMOUNT)
        self.reorder_level_input = QDoubleSpinBox()
        self.reorder_level_input.setMaximum(MAX_AMOUNT)

        self.more_details_frame.setLayout(more_layout)
        self.more_details_frame.setVisible(False)
        layout.addWidget(self.more_details_frame)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        save_btn = QPushButton("✓ محفوظ کریں")
        save_btn.setFixedHeight(48)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE};
                font-weight: bold; font-size: 15px; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #2E7D32; }}
        """)
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

        fix_spinbox_rtl(self.purchase_price_input)
        fix_spinbox_rtl(self.sale_price_input)
        fix_spinbox_rtl(self.min_stock_input)
        fix_spinbox_rtl(self.min_sale_price_input)
        fix_spinbox_rtl(self.reorder_level_input)

    def _label(self, text) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 13px; font-weight: bold; color: #444;")
        return label

    def _input_style(self) -> str:
        return """
            QComboBox, QDoubleSpinBox, QLineEdit {
                border: 1.5px solid #C8E6C9; border-radius: 6px;
                padding: 0 10px; font-size: 13px; background-color: white;
            }
            QComboBox:focus, QDoubleSpinBox:focus, QLineEdit:focus { border: 1.5px solid #1B5E20; }
        """

    def _toggle_more_details(self):
        visible = not self.more_details_frame.isVisible()
        self.more_details_frame.setVisible(visible)
        self.more_details_btn.setText("مزید تفصیل ▴" if visible else "مزید تفصیل ▾")

    def _reload_categories(self):
        self.category_input.clear()
        self.category_input.addItem("(کوئی نہیں)", None)
        for cat in get_categories():
            self.category_input.addItem(cat.name, cat.id)

    def _reload_units(self):
        self.unit_input.clear()
        self.unit_input.addItem("(کوئی نہیں)", None)
        for unit in get_units():
            self.unit_input.addItem(unit.name, unit.id)

    def _add_new_category(self):
        name, ok = QInputDialog.getText(self, "نئی قسم", "قسم کا نام:")
        if ok and name.strip():
            add_category(name)
            self._reload_categories()
            self.category_input.setCurrentText(name.strip())

    def _add_new_unit(self):
        name, ok = QInputDialog.getText(self, "نیا یونٹ", "یونٹ کا نام (مثلاً بوری، کلو):")
        if ok and name.strip():
            add_unit(name)
            self._reload_units()
            self.unit_input.setCurrentText(name.strip())

    def _handle_save(self):
        self.error_label.setText("")
        name = self.name_input.text().strip()
        brand = self.brand_input.text().strip()

        if not name:
            self.error_label.setText("چیز کا نام لکھنا ضروری ہے۔")
            return

        duplicate = check_duplicate_product(name, brand)
        if duplicate:
            reply = QMessageBox.question(
                self, "پہلے سے موجود ہے",
                f"'{duplicate.name}' ({duplicate.product_code}) پہلے سے موجود ہے۔\n"
                f"کیا آپ پھر بھی نئی اندراج کرنا چاہتے ہیں؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        product = add_product(
            name=name,
            brand=brand,
            category_id=self.category_input.currentData(),
            unit_id=self.unit_input.currentData(),
            purchase_price=self.purchase_price_input.value(),
            sale_price=self.sale_price_input.value(),
            min_sale_price=self.min_sale_price_input.value(),
            min_stock_level=self.min_stock_input.value(),
            reorder_level=self.reorder_level_input.value(),
        )

        quantity = self.opening_quantity_input.value()
        if quantity > 0:
            try:
                set_opening_stock(
                    product.id, quantity, self.purchase_price_input.value(),
                    self.user.id if self.user else None
                )
            except ValueError:
                pass  # agar kisi wajah se already set ho (naye product ke liye normally nahi hoga)
        self.saved_product = product
        self.accept()

class ProductPage(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        self.setLayout(layout)

        heading = QLabel("اشیاء / سٹاک")
        heading.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(heading)

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)
        self.search_input.setPlaceholderText("نام، کوڈ یا برانڈ سے تلاش کریں...")
        self.search_input.textChanged.connect(self.refresh)
        top_bar.addWidget(self.search_input)

        add_btn = QPushButton("+ نئی چیز شامل کریں")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 0 16px; font-weight: bold; border-radius: 6px;"
        )
        add_btn.clicked.connect(self._open_add_dialog)
        top_bar.addWidget(add_btn)

        opening_stock_btn = QPushButton("ابتدائی سٹاک")
        opening_stock_btn.setFixedHeight(40)
        opening_stock_btn.clicked.connect(self._open_opening_stock_dialog)
        top_bar.addWidget(opening_stock_btn)


        layout.addLayout(top_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["کوڈ", "نام", "برانڈ", "قسم", "یونٹ", "خریداری قیمت", "فروخت قیمت", "سٹاک"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        search_text = self.search_input.text().strip()
        products = get_products(search_text)

        if not products:
            self.table.setRowCount(0)
            self.table.setColumnCount(9)
            from ui.widgets import show_empty_state
            show_empty_state(self.table, "ابھی تک کوئی چیز شامل نہیں ہوئی — '+ نئی چیز شامل کریں' سے شروع کریں۔")
            return

        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["کوڈ", "نام", "برانڈ", "قسم", "یونٹ", "خریداری قیمت", "فروخت قیمت", "سٹاک", "عمل"]
        )
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(p.product_code))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(p.brand or ""))
            self.table.setItem(row, 3, QTableWidgetItem(p.category.name if p.category else ""))
            self.table.setItem(row, 4, QTableWidgetItem(p.unit.name if p.unit else ""))
            self.table.setItem(row, 5, QTableWidgetItem(rs(p.purchase_price)))
            self.table.setItem(row, 6, QTableWidgetItem(rs(p.sale_price)))
            self.table.setItem(row, 7, QTableWidgetItem(str(p.current_stock)))

            if is_admin(self.user):
                edit_btn = QPushButton("قیمت تبدیل کریں")
                edit_btn.clicked.connect(lambda checked, pid=p.id: self._open_edit_dialog(pid))
                self.table.setCellWidget(row, 8, edit_btn)

    def _open_edit_dialog(self, product_id):
        product = get_product_by_id(product_id)
        dialog = EditProductDialog(product, self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


    def _open_opening_stock_dialog(self):
        user_id = self.user.id if self.user else None
        dialog = OpeningStockDialog(user_id, self)
        dialog.exec()
        self.refresh()

    def _open_add_dialog(self):
        dialog = AddProductDialog(self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()

    def refresh_data(self):
        self.refresh()

class EditProductDialog(QDialog):
    """
    AddProductDialog jaisa hi form, lekin existing product ki values
    se pehle se bhara hua — sirf price/naam/category update karne ke liye.
    Duplicate check nahi hota kyunki ye wahi product hai.
    """

    def __init__(self, product, user, parent=None):
        super().__init__(parent)
        self.product = product
        self.user = user
        self.setWindowTitle(f"قیمت / تفصیل تبدیل کریں — {product.name}")
        self.resize(420, 480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.setLayout(layout)

        heading = QLabel(self.product.name)
        heading.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(heading)

        layout.addWidget(self._label("چیز کا نام"))
        self.name_input = QLineEdit(self.product.name)
        self.name_input.setFixedHeight(42)
        self.name_input.setStyleSheet(self._input_style())
        layout.addWidget(self.name_input)

        prices_row = QHBoxLayout()

        purchase_col = QVBoxLayout()
        purchase_col.addWidget(self._label("خریداری کی قیمت"))
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setFixedHeight(42)
        self.purchase_price_input.setMaximum(MAX_AMOUNT)
        self.purchase_price_input.setPrefix("Rs. ")
        self.purchase_price_input.setValue(float(self.product.purchase_price or 0))
        self.purchase_price_input.setStyleSheet(self._input_style())
        purchase_col.addWidget(self.purchase_price_input)
        prices_row.addLayout(purchase_col)

        sale_col = QVBoxLayout()
        sale_col.addWidget(self._label("فروخت کی قیمت"))
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setFixedHeight(42)
        self.sale_price_input.setMaximum(MAX_AMOUNT)
        self.sale_price_input.setPrefix("Rs. ")
        self.sale_price_input.setValue(float(self.product.sale_price or 0))
        self.sale_price_input.setStyleSheet(self._input_style())
        sale_col.addWidget(self.sale_price_input)
        prices_row.addLayout(sale_col)

        layout.addLayout(prices_row)

        old_price_note = QLabel(
            f"پرانی خریداری قیمت: Rs. {self.product.purchase_price}   |   "
            f"پرانی فروخت قیمت: Rs. {self.product.sale_price}"
        )
        old_price_note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(old_price_note)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        layout.addWidget(self.error_label)

        layout.addStretch()

        save_btn = QPushButton("✓ تبدیلی محفوظ کریں")
        save_btn.setFixedHeight(48)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE};
                font-weight: bold; font-size: 15px; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #2E7D32; }}
        """)
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _label(self, text) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 13px; font-weight: bold; color: #444;")
        return label

    def _input_style(self) -> str:
        return """
            QComboBox, QDoubleSpinBox, QLineEdit {
                border: 1.5px solid #C8E6C9; border-radius: 6px;
                padding: 0 10px; font-size: 13px; background-color: white;
            }
            QComboBox:focus, QDoubleSpinBox:focus, QLineEdit:focus { border: 1.5px solid #1B5E20; }
        """

    def _handle_save(self):
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("نام لکھنا ضروری ہے۔")
            return

        edit_product(
            product_id=self.product.id,
            name=name,
            brand=self.product.brand or "",
            category_id=self.product.category_id,
            unit_id=self.product.unit_id,
            purchase_price=self.purchase_price_input.value(),
            sale_price=self.sale_price_input.value(),
            min_sale_price=float(self.product.min_sale_price or 0),
            min_stock_level=float(self.product.min_stock_level or 0),
            reorder_level=float(self.product.reorder_level or 0),
            user_id=self.user.id if self.user else None,
        )
        self.accept()
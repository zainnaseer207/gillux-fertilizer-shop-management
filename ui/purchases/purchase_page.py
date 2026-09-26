from services.purchase_service import get_suppliers, get_products, save_purchase, get_purchases
from ui.returns.return_dialog import ReturnDialog
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER
from PySide6.QtWidgets import QFileDialog, QScrollArea
from utils.pdf_generator import generate_invoice_pdf
from database.database import SessionLocal
from database.models import Purchase, PurchaseItem
from sqlalchemy.orm import joinedload
from utils.permissions import is_admin
from ui.theme import fix_spinbox_rtl
from ui.widgets import show_empty_state
from utils.constants import MAX_AMOUNT
from ui.widgets import MoneySpinBox
from utils.formatting import rs



from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QComboBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QTabWidget, QDialog, QFrame
)
from PySide6.QtCore import Qt

from services.purchase_service import get_suppliers, get_products, save_purchase, get_purchases
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER
from ui.returns.return_dialog import ReturnDialog
from utils.permissions import is_admin

from PySide6.QtWidgets import QFileDialog
from utils.pdf_generator import generate_invoice_pdf
from database.database import SessionLocal
from database.models import Purchase, PurchaseItem
from sqlalchemy.orm import joinedload

def _label(text: str) -> QWidget:
    """
    Label ko ek chhoti row mein wrap karte hain jisme stretch
    (khaali jagah) bayen taraf hai — is se label GUARANTEED
    right side (sidebar wali taraf) par aata hai.
    """
    wrapper = QWidget()
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(0)
    wrapper.setLayout(row)

    label = QLabel(text)
    label.setStyleSheet("font-size: 13px; font-weight: bold; color: #444; margin-top: 6px;")

    row.addWidget(label)
    row.addStretch()

    return wrapper


def _dropdown_style() -> str:
    return """
        QComboBox {
            border: 1.5px solid #C8E6C9;
            border-radius: 6px;
            padding: 0 10px;
            font-size: 13px;
            background-color: white;
        }
        QComboBox:focus { border: 1.5px solid #1B5E20; }
    """


def _number_field_style() -> str:
    return """
        QDoubleSpinBox {
            border: 1.5px solid #C8E6C9;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 14px;
            background-color: white;
        }
        QDoubleSpinBox:focus { border: 1.5px solid #1B5E20; }
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            width: 24px;
            subcontrol-origin: border;
        }
        QDoubleSpinBox::up-button { subcontrol-position: top left; }
        QDoubleSpinBox::down-button { subcontrol-position: bottom left; }
    """


def _make_number_field(prefix: str = "", min_width: int = 0) -> QDoubleSpinBox:
    field = QDoubleSpinBox()
    field.setFixedHeight(46)
    field.setMaximum(9999999)
    if prefix:
        field.setPrefix(prefix)
    if min_width:
        field.setMinimumWidth(min_width)
    field.setStyleSheet(_number_field_style())
    field.setLayoutDirection(Qt.LeftToRight)
    field.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return field


def _make_dropdown() -> QComboBox:
    field = QComboBox()
    field.setFixedHeight(46)
    field.setStyleSheet(_dropdown_style())
    return field


def _make_money_field(min_width: int = 0) -> MoneySpinBox:
    field = MoneySpinBox()
    if min_width:
        field.setMinimumWidth(min_width)
    return field

def _make_money_field(min_width: int = 0) -> MoneySpinBox:
    field = MoneySpinBox()
    if min_width:
        field.setMinimumWidth(min_width)
    return field

class NewPurchaseForm(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.line_items = []
        self._build_ui()
        self._reload_suppliers()
        self._reload_products()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(outer_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        outer_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        content.setLayout(layout)

        heading = QLabel("نئی خریداری")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        layout.addWidget(_label("سپلائر کا نام"))
        self.supplier_input = _make_dropdown()
        layout.addWidget(self.supplier_input)

        item_row_label = QHBoxLayout()
        item_row_label.addWidget(_label("چیز"), stretch=3)
        item_row_label.addWidget(_label("مقدار"), stretch=1)
        item_row_label.addWidget(_label("قیمت"), stretch=1)
        layout.addLayout(item_row_label)

        add_row = QHBoxLayout()

        self.product_input = _make_dropdown()
        self.product_input.currentIndexChanged.connect(self._prefill_rate)
        add_row.addWidget(self.product_input, stretch=3)

        self.quantity_input = _make_number_field(min_width=90)
        self.quantity_input.setValue(1)
        add_row.addWidget(self.quantity_input, stretch=1)

        self.rate_input = _make_money_field(min_width=110)
        add_row.addWidget(self.rate_input, stretch=1)

        layout.addLayout(add_row)

        add_item_btn = QPushButton("+ فہرست میں شامل کریں")
        add_item_btn.setFixedHeight(44)
        add_item_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white; color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY}; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #E8F5E9; }}
        """)
        add_item_btn.clicked.connect(self._add_line_item)
        layout.addWidget(add_item_btn)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["چیز", "مقدار", "قیمت", "رقم", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.setMinimumHeight(180)          # ← NAYI LINE: table ko poori jagah milegi
        self.items_table.verticalHeader().setDefaultSectionSize(38)   # ← NAYI LINE: har row ki height fix
        layout.addWidget(self.items_table)
        layout.addWidget(self.items_table)

        layout.addWidget(_label("ادائیگی کی قسم"))
        payment_row = QHBoxLayout()

        self.cash_btn = QPushButton("نقد")
        self.cash_btn.setCheckable(True)
        self.cash_btn.setChecked(True)
        self.cash_btn.setFixedHeight(46)
        self.cash_btn.clicked.connect(lambda: self._set_payment_mode("cash"))

        self.credit_btn = QPushButton("ادھار")
        self.credit_btn.setCheckable(True)
        self.credit_btn.setFixedHeight(46)
        self.credit_btn.clicked.connect(lambda: self._set_payment_mode("credit"))

        toggle_style = f"""
            QPushButton {{
                background-color: white; color: #555; border: 1.5px solid #ccc;
                border-radius: 6px; font-size: 14px; font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {COLOR_PRIMARY}; color: white; border-color: {COLOR_PRIMARY};
            }}
        """
        self.cash_btn.setStyleSheet(toggle_style)
        self.credit_btn.setStyleSheet(toggle_style)

        payment_row.addWidget(self.cash_btn)
        payment_row.addWidget(self.credit_btn)
        layout.addLayout(payment_row)

        self.paid_row = QHBoxLayout()
        self.paid_row_label = _label("کتنی رقم ادا کی؟")
        self.paid_input = _make_money_field()
        self.paid_row.addWidget(self.paid_row_label)
        self.paid_row.addWidget(self.paid_input)
        layout.addLayout(self.paid_row)
        self.paid_row_label.setVisible(False)
        self.paid_input.setVisible(False)

        self.more_details_btn = QPushButton("مزید تفصیل ▾")
        self.more_details_btn.setFlat(True)
        self.more_details_btn.setStyleSheet(f"color: {COLOR_PRIMARY}; text-align: left; border: none; font-size: 12px;")
        self.more_details_btn.clicked.connect(self._toggle_more_details)
        layout.addWidget(self.more_details_btn)

        self.more_details_frame = QFrame()
        more_layout = QHBoxLayout()
        more_layout.addWidget(_label("رسید نمبر (سپلائر کی)"))
        self.invoice_number_input = QLineEdit()
        self.invoice_number_input.setFixedHeight(42)
        self.invoice_number_input.setStyleSheet(_dropdown_style())
        more_layout.addWidget(self.invoice_number_input)
        more_layout.addWidget(_label("رعایت"))
        self.discount_input = _make_money_field()
        self.discount_input.valueChanged.connect(self._update_totals)
        more_layout.addWidget(self.discount_input)
        self.more_details_frame.setLayout(more_layout)
        self.more_details_frame.setVisible(False)
        layout.addWidget(self.more_details_frame)

        self.total_label = QLabel("کل رقم: Rs. 0")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setWordWrap(True)
        self.total_label.setMinimumHeight(50)
        self.total_label.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {COLOR_PRIMARY}; "
            f"background-color: #E8F5E9; border-radius: 8px; padding: 12px;"
        )
        layout.addWidget(self.total_label)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER}; font-size: 13px;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        save_btn = QPushButton("✓ خریداری محفوظ کریں")
        save_btn.setFixedHeight(52)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE};
                font-weight: bold; font-size: 16px; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #2E7D32; }}
        """)
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _label(self, text, stretch=None) -> QLabel:
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

    def _secondary_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: white; color: {COLOR_PRIMARY};
                border: 1.5px solid {COLOR_PRIMARY}; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #E8F5E9; }}
        """

    def _toggle_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: white; color: #555; border: 1.5px solid #ccc;
                border-radius: 6px; font-size: 14px; font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {COLOR_PRIMARY}; color: white; border-color: {COLOR_PRIMARY};
            }}
        """

    def _set_payment_mode(self, mode):
        self.cash_btn.setChecked(mode == "cash")
        self.credit_btn.setChecked(mode == "credit")
        is_credit = mode == "credit"
        self.paid_row_label.setVisible(is_credit)
        self.paid_input.setVisible(is_credit)
        if not is_credit:
            self.paid_input.setValue(0)

    def _toggle_more_details(self):
        visible = not self.more_details_frame.isVisible()
        self.more_details_frame.setVisible(visible)
        self.more_details_btn.setText("مزید تفصیل ▴" if visible else "مزید تفصیل ▾")

    def _reload_suppliers(self):
        self.supplier_input.clear()
        for s in get_suppliers():
            self.supplier_input.addItem(f"{s.name} ({s.party_code})", s.id)

    def _reload_products(self):
        self.product_input.clear()
        self._products_cache = get_products()
        for p in self._products_cache:
            self.product_input.addItem(f"{p.name} ({p.product_code})", p.id)

    def _reload_products(self):
        self.product_input.clear()
        self._products_cache = get_products()
        for p in self._products_cache:
            self.product_input.addItem(f"{p.name} ({p.product_code})", p.id)
        self._prefill_rate()

    def _prefill_rate(self):
        product_id = self.product_input.currentData()
        product = next((p for p in self._products_cache if p.id == product_id), None)
        if product:
            self.rate_input.setValue(int(product.purchase_price or 0))

    def _add_line_item(self):
        product_id = self.product_input.currentData()
        if product_id is None:
            return
        product = next((p for p in self._products_cache if p.id == product_id), None)
        quantity = self.quantity_input.value()
        rate = self.rate_input.value()

        if quantity <= 0 or rate <= 0:
            self.error_label.setText("مقدار اور قیمت صفر سے زیادہ ہونی چاہیے۔")
            return

        self.error_label.setText("")
        amount = quantity * rate
        self.line_items.append({
            "product_id": product_id, "name": product.name,
            "quantity": quantity, "rate": rate, "amount": amount,
        })
        self._refresh_items_table()
        self._update_totals()

    def _refresh_items_table(self):
        self.items_table.setRowCount(len(self.line_items))
        for row, item in enumerate(self.line_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            qty_display = str(int(item["quantity"])) if item["quantity"] == int(item["quantity"]) else str(item["quantity"])
            self.items_table.setItem(row, 1, QTableWidgetItem(qty_display))
            self.items_table.setItem(row, 2, QTableWidgetItem(rs(item['rate'])))
            self.items_table.setItem(row, 3, QTableWidgetItem(rs(item['amount'])))

            remove_btn = QPushButton("ہٹائیں")
            remove_btn.setFixedHeight(32)
            remove_btn.clicked.connect(lambda checked, r=row: self._remove_line_item(r))
            self.items_table.setCellWidget(row, 4, remove_btn)
        self.items_table.resizeRowsToContents()   # ← NAYI LINE: rows apni content ke hisaab se resize hon

    def _remove_line_item(self, row_index):
        del self.line_items[row_index]
        self._refresh_items_table()
        self._update_totals()

    def _update_totals(self):
        subtotal = sum(item["amount"] for item in self.line_items)
        total = max(subtotal - self.discount_input.value(), 0)
        self.total_label.setText(f"کل رقم: {rs(total)}")

    def _handle_save(self):
        self.error_label.setText("")
        supplier_id = self.supplier_input.currentData()

        if supplier_id is None:
            self.error_label.setText("سپلائر کا نام منتخب کریں۔")
            return
        if not self.line_items:
            self.error_label.setText("کم از کم ایک چیز شامل کریں۔")
            return

        is_credit = self.credit_btn.isChecked()
        subtotal = sum(item["amount"] for item in self.line_items)
        total = max(subtotal - self.discount_input.value(), 0)
        paid = self.paid_input.value() if is_credit else total

        try:
            purchase = save_purchase(
                supplier_id=supplier_id,
                invoice_number=self.invoice_number_input.text().strip(),
                items=self.line_items,
                discount=self.discount_input.value(),
                paid_amount=paid,
                payment_method="credit" if is_credit else "cash",
                notes="",
                user_id=self.user.id if self.user else None,
            )
        except Exception as e:
            self.error_label.setText(f"خریداری محفوظ نہیں ہو سکی: {e}")
            return

        QMessageBox.information(self, "کامیابی", f"خریداری {purchase.purchase_number} محفوظ ہو گئی۔")
        self.line_items = []
        self._refresh_items_table()
        self._update_totals()
        self.invoice_number_input.clear()
        self.paid_input.setValue(0)
        self.discount_input.setValue(0)
        self._set_payment_mode("cash")
        self._reload_products()

    def refresh_data(self):
        self._reload_suppliers()
        self._reload_products()


class PurchaseHistoryTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("خریداری کی تاریخ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("خریداری نمبر سے تلاش کریں...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.refresh)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["خریداری نمبر", "سپلائر", "تاریخ", "کل رقم", "ادا شدہ", "باقی", "عمل"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        purchases = get_purchases(self.search_input.text().strip())

        if not purchases:
            self.table.setRowCount(0)
            show_empty_state(self.table, "ابھی تک کوئی خریداری نہیں ہوئی۔")
            return

        self.table.setRowCount(len(purchases))
        for row, p in enumerate(purchases):
            self.table.setItem(row, 0, QTableWidgetItem(p.purchase_number))
            self.table.setItem(row, 1, QTableWidgetItem(p.supplier.name if p.supplier else ""))
            self.table.setItem(row, 2, QTableWidgetItem(p.purchase_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 3, QTableWidgetItem(rs(p.total)))
            self.table.setItem(row, 4, QTableWidgetItem(rs(p.paid_amount)))
            self.table.setItem(row, 5, QTableWidgetItem(rs(p.remaining_amount)))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            print_btn = QPushButton("پرنٹ")
            print_btn.clicked.connect(lambda checked, pid=p.id: self._print_invoice(pid))
            action_layout.addWidget(print_btn)

            return_btn = QPushButton("واپسی")
            return_btn.clicked.connect(lambda checked, pid=p.id, num=p.purchase_number: self._open_return_dialog(pid, num))
            return_btn.setVisible(is_admin(self.user))
            action_layout.addWidget(return_btn)

            self.table.setCellWidget(row, 6, action_widget)

    def _print_invoice(self, purchase_id):
        session = SessionLocal()
        try:
            purchase = (
                session.query(Purchase)
                .options(joinedload(Purchase.supplier), joinedload(Purchase.items).joinedload(PurchaseItem.product))
                .filter_by(id=purchase_id)
                .first()
            )
            default_name = f"{purchase.purchase_number}.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "خریداری محفوظ کریں", default_name, "PDF Files (*.pdf)")
            if not path:
                return
            generate_invoice_pdf("purchase", purchase, purchase.items, path)
            QMessageBox.information(self, "کامیابی", f"خریداری محفوظ ہو گئی:\n{path}")
        finally:
            session.close()

    def _open_return_dialog(self, purchase_id, purchase_number):
        dialog = ReturnDialog("purchase", purchase_id, purchase_number, self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


class PurchasePage(QWidget):
    def __init__(self, user):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        self.new_purchase_form = NewPurchaseForm(user)
        self.history_tab = PurchaseHistoryTab(user)

        tabs.addTab(self.new_purchase_form, "New Purchase")
        tabs.addTab(self.history_tab, "Purchase History")

        tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 1:
            self.history_tab.refresh()

    def refresh_data(self):
        self.new_purchase_form._reload_suppliers()
        self.new_purchase_form._reload_products()

    def _print_invoice(self, purchase_id):
        session = SessionLocal()
        try:
            purchase = (
                session.query(Purchase)
                .options(joinedload(Purchase.supplier), joinedload(Purchase.items).joinedload(PurchaseItem.product))
                .filter_by(id=purchase_id)
                .first()
            )

            default_name = f"{purchase.purchase_number}.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "Purchase Save Karein", default_name, "PDF Files (*.pdf)")
            if not path:
                return

            generate_invoice_pdf("purchase", purchase, purchase.items, path)
            QMessageBox.information(self, "Success", f"Purchase PDF save ho gayi:\n{path}")
        finally:
            session.close()
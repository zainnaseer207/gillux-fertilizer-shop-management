"""
ui/sales/sale_page.py

Daily Sale (نئی فروخت) — poori tarah Urdu, register-jaisa asaan
tareeqa. Structure:
  - Upar: scrollable form (customer, item, payment type)
  - Neeche: FIXED bar (kabhi scroll nahi hota) jisme Total aur
    Save button hamesha nazar aate hain, chahe form kitna bhi bara ho.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QComboBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QTabWidget, QDialog, QFrame, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt
from sqlalchemy.orm import joinedload
from ui.widgets import show_empty_state

from PySide6.QtWidgets import QSpinBox
from utils.constants import MAX_AMOUNT
from services.sale_service import get_customers, get_products, save_sale, get_sales
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER
from ui.returns.return_dialog import ReturnDialog
from utils.permissions import is_admin
from utils.pdf_generator import generate_invoice_pdf
from database.database import SessionLocal
from database.models import Sale, SaleItem
from utils.constants import MAX_AMOUNT
from ui.widgets import MoneySpinBox
from utils.formatting import rs
# Replace 'your_module_name' with the actual file/module where the function lives



# ============================================================
# STYLE HELPERS — poori file mein reuse hote hain
# ============================================================

def _label(text: str) -> QWidget:
    """
    Label ko ek chhoti row mein wrap karte hain jisme stretch
    (khaali jagah) bayen taraf hai — is se label GUARANTEED
    right side (sidebar wali taraf) par aata hai, chahe alignment
    property kuch bhi ho, RTL mirroring se conflict nahi hota.
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
    field.setMaximum(MAX_AMOUNT)
    if prefix:
        field.setPrefix(prefix)
    if min_width:
        field.setMinimumWidth(min_width)
    field.setStyleSheet("""
        QDoubleSpinBox {
            border: 1.5px solid #C8E6C9;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 14px;
            background-color: white;
        }
        QDoubleSpinBox:focus { border: 1.5px solid #1B5E20; }
    """)
    return field


def _make_money_field(min_width: int = 0) -> MoneySpinBox:
    field = MoneySpinBox()
    if min_width:
        field.setMinimumWidth(min_width)
    return field



class MoneySpinBox(QSpinBox):
    """
    Paisay ke liye reusable field — WHOLE NUMBER (float/double nahi),
    taake rounding errors kabhi na aayein (solid money math).

    setGroupSeparatorShown(True) khud-ba-khud 1,000 / 100,000 jaisa
    comma formatting deta hai — kuch extra code likhne ki zaroorat nahi.
    """

    def __init__(self, prefix: str = "Rs. ", parent=None):
        super().__init__(parent)
        self.setRange(0, MAX_AMOUNT)
        self.setGroupSeparatorShown(True)
        self.setFixedHeight(44)
        if prefix:
            self.setPrefix(prefix)
        self.setStyleSheet("""
            QSpinBox {
                border: 1.5px solid #C8E6C9;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 14px;
                background-color: white;
            }
            QSpinBox:focus { border: 1.5px solid #1B5E20; }
        """)


def _make_dropdown() -> QComboBox:
    field = QComboBox()
    field.setFixedHeight(46)
    field.setStyleSheet(_dropdown_style())
    return field


def _split_row(title: str, value_text: str = "") -> tuple:
    """
    Urdu label aur number/value ko DO ALAG labels mein deta hai.
    Order: pehle title (right side par aayega), phir value, phir
    stretch (khaali jagah) sabse aakhir mein — RTL mirroring ke
    sath ye guaranteed sahi position deta hai.
    """
    row = QHBoxLayout()

    title_label = QLabel(title)
    title_label.setStyleSheet("color: #666; font-size: 12px;")

    value_label = QLabel(value_text)
    value_label.setLayoutDirection(Qt.LeftToRight)
    value_label.setStyleSheet("color: #333; font-size: 12px; font-weight: bold;")

    row.addWidget(title_label)
    row.addWidget(value_label)
    row.addStretch()

    return row, title_label, value_label


# ============================================================
# NEW SALE FORM
# ============================================================

class NewSaleForm(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.line_items = []
        self._build_ui()
        self._reload_customers()
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

        heading = QLabel("نئی فروخت")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        layout.addWidget(_label("گاہک کا نام"))
        self.customer_input = _make_dropdown()
        layout.addWidget(self.customer_input)

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

        self.stock_hint_label = QLabel("")
        self.stock_hint_label.setStyleSheet("color: #777; font-size: 12px;")
        layout.addWidget(self.stock_hint_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["چیز", "مقدار", "قیمت", "رقم", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.setMinimumHeight(150)
        self.items_table.verticalHeader().setDefaultSectionSize(38)
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
        self.paid_row_label = _label("کتنی رقم ملی؟")
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
        more_layout.addWidget(_label("رعایت (Discount)"))
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

        save_btn = QPushButton("✓ فروخت محفوظ کریں")
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

    def _reload_customers(self):
        self.customer_input.clear()
        for c in get_customers():
            self.customer_input.addItem(f"{c.name} ({c.party_code})", c.id)

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
            self.rate_input.setValue(float(product.sale_price or 0))
            unit = product.unit.name if product.unit else ""
            self.stock_hint_label.setText(f"دستیاب اسٹاک: {product.current_stock} {unit}")
        else:
            self.stock_hint_label.setText("")

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

        already_added = sum(i["quantity"] for i in self.line_items if i["product_id"] == product_id)
        if float(product.current_stock or 0) < (already_added + quantity):
            self.error_label.setText(
                f"اسٹاک کم ہے! دستیاب: {product.current_stock}، آپ {already_added + quantity} بیچنا چاہ رہے ہیں۔"
            )
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
        customer_id = self.customer_input.currentData()

        if customer_id is None:
            self.error_label.setText("گاہک کا نام منتخب کریں۔")
            return
        if not self.line_items:
            self.error_label.setText("کم از کم ایک چیز شامل کریں۔")
            return

        is_credit = self.credit_btn.isChecked()
        subtotal = sum(item["amount"] for item in self.line_items)
        total = max(subtotal - self.discount_input.value(), 0)
        paid = self.paid_input.value() if is_credit else total

        try:
            sale = save_sale(
                customer_id=customer_id,
                items=self.line_items,
                discount=self.discount_input.value(),
                paid_amount=paid,
                payment_method="credit" if is_credit else "cash",
                notes="",
                user_id=self.user.id if self.user else None,
            )
        except ValueError as e:
            self.error_label.setText(str(e))
            return
        except Exception as e:
            self.error_label.setText(f"فروخت محفوظ نہیں ہو سکی: {e}")
            return

        QMessageBox.information(self, "کامیابی", f"رسید {sale.invoice_number} محفوظ ہو گئی۔")
        self.line_items = []
        self._refresh_items_table()
        self._update_totals()
        self.paid_input.setValue(0)
        self.discount_input.setValue(0)
        self._set_payment_mode("cash")
        self._reload_products()

    def refresh_data(self):
        self._reload_customers()
        self._reload_products()

# ============================================================
# SALES HISTORY TAB
# ============================================================

class SaleHistoryTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("فروخت کی تاریخ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("رسید نمبر سے تلاش کریں...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.refresh)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["رسید نمبر", "گاہک", "تاریخ", "کل رقم", "ادا شدہ", "باقی", "عمل"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        sales = get_sales(self.search_input.text().strip())

        if not sales:
            self.table.setRowCount(0)
            show_empty_state(self.table, "ابھی تک کوئی فروخت نہیں ہوئی۔")
            return

        self.table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(s.invoice_number))
            self.table.setItem(row, 1, QTableWidgetItem(s.customer.name if s.customer else ""))
            self.table.setItem(row, 2, QTableWidgetItem(s.sale_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 3, QTableWidgetItem(rs(s.total)))
            self.table.setItem(row, 4, QTableWidgetItem(rs(s.paid_amount)))
            self.table.setItem(row, 5, QTableWidgetItem(rs(s.remaining_amount)))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            print_btn = QPushButton("پرنٹ")
            print_btn.clicked.connect(lambda checked, sid=s.id: self._print_invoice(sid))
            action_layout.addWidget(print_btn)

            return_btn = QPushButton("واپسی")
            return_btn.clicked.connect(lambda checked, sid=s.id, inv=s.invoice_number: self._open_return_dialog(sid, inv))
            return_btn.setVisible(is_admin(self.user))
            action_layout.addWidget(return_btn)

            self.table.setCellWidget(row, 6, action_widget)

    def _print_invoice(self, sale_id):
        session = SessionLocal()
        try:
            sale = (
                session.query(Sale)
                .options(joinedload(Sale.customer), joinedload(Sale.items).joinedload(SaleItem.product))
                .filter_by(id=sale_id)
                .first()
            )
            default_name = f"{sale.invoice_number}.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "رسید محفوظ کریں", default_name, "PDF Files (*.pdf)")
            if not path:
                return
            generate_invoice_pdf("sale", sale, sale.items, path)
            QMessageBox.information(self, "کامیابی", f"رسید محفوظ ہو گئی:\n{path}")
        finally:
            session.close()

    def _open_return_dialog(self, sale_id, invoice_number):
        dialog = ReturnDialog("sale", sale_id, invoice_number, self.user, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


# ============================================================
# SALE PAGE (Container: New Sale + History Tabs)
# ============================================================

class SalePage(QWidget):
    def __init__(self, user):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.new_sale_form = NewSaleForm(user)
        self.history_tab = SaleHistoryTab(user)

        self.tabs.addTab(self.new_sale_form, "نئی فروخت")
        self.tabs.addTab(self.history_tab, "فروخت کی تاریخ")

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 1:
            self.history_tab.refresh()
        else:
            self.new_sale_form.refresh_data()

    def refresh_data(self):
        self._on_tab_changed(self.tabs.currentIndex())
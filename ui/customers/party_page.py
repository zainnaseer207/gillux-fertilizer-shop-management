"""
ui/customers/party_page.py

Ek hi PartyPage class Customers aur Suppliers dono sections ke liye
use hoti hai — bas "party_type" parameter different hota hai.

AddPartyDialog ab bara/split-screen hai:
  - Left side: naya party add karne ka form
  - Right side: existing parties ki live-filtering list (name type
    karte hi match hone wale existing customers/suppliers dikhte hain)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox, QHeaderView, QSplitter, QFrame
)
from PySide6.QtCore import Qt
from ui.customers.ledger_dialog import LedgerDialog
from ui.widgets import show_empty_state
from ui.theme import fix_spinbox_rtl
from utils.constants import MAX_AMOUNT
from utils.formatting import rs

from services.party_service import add_party, get_parties, check_duplicate, get_customer_groups, add_customer_group
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_BORDER, COLOR_TEXT_MUTED, fix_spinbox_rtl


class AddPartyDialog(QDialog):
    def __init__(self, party_type: str, parent=None):
        super().__init__(parent)
        self.party_type = party_type
        self.label = "گاہک" if party_type == "customer" else "سپلائر"
        self.setWindowTitle(f"نیا {self.label}")
        self.resize(950, 600)
        self.saved_party = None
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)

        splitter = QSplitter(Qt.Horizontal)
        outer_layout.addWidget(splitter)

        splitter.addWidget(self._build_form_panel())
        splitter.addWidget(self._build_existing_list_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        panel.setLayout(layout)

        heading = QLabel(f"نیا {self.label}")
        heading.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(heading)


        # ---- Sirf naam + mobile bare aur upar (register ka core) ----
        layout.addWidget(self._label("نام"))
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(44)
        self.name_input.setStyleSheet(self._input_style())
        self.name_input.setPlaceholderText("ضروری")
        self.name_input.textChanged.connect(self._filter_existing_list)
        layout.addWidget(self.name_input)

        layout.addWidget(self._label("موبائل نمبر"))
        self.mobile_input = QLineEdit()
        self.mobile_input.setFixedHeight(44)
        self.mobile_input.setStyleSheet(self._input_style())
        layout.addWidget(self.mobile_input)

        layout.addWidget(self._label("پرانا بقایا (اگر ہو)"))
        opening_row = QHBoxLayout()
        self.opening_balance_input = QDoubleSpinBox()
        self.opening_balance_input.setFixedHeight(44)
        self.opening_balance_input.setMaximum(MAX_AMOUNT)
        self.opening_balance_input.setPrefix("Rs. ")
        self.opening_balance_input.setStyleSheet(self._input_style())
        fix_spinbox_rtl(self.opening_balance_input)
        opening_row.addWidget(self.opening_balance_input)

        self.balance_type_input = QComboBox()
        self.balance_type_input.setFixedHeight(44)
        self.balance_type_input.addItem("وصولی باقی ہے (وہ ہمیں دیں گے)", "receivable")
        self.balance_type_input.addItem("ادائیگی باقی ہے (ہم انہیں دیں گے)", "payable")
        self.balance_type_input.setStyleSheet(self._input_style())
        opening_row.addWidget(self.balance_type_input)
        layout.addLayout(opening_row)

        # ---- Customer Group (sirf customer ke liye, supplier ke liye nahi) ----
        if self.party_type == "customer":
            layout.addWidget(self._label("گروپ (اختیاری)"))
            group_row = QHBoxLayout()

            self.group_input = QComboBox()
            self.group_input.setFixedHeight(44)
            self.group_input.setStyleSheet(self._input_style())
            self._reload_groups()
            group_row.addWidget(self.group_input)

            new_group_btn = QPushButton("+ نیا گروپ")
            new_group_btn.setFixedHeight(44)
            new_group_btn.clicked.connect(self._add_new_group)
            group_row.addWidget(new_group_btn)

            layout.addLayout(group_row)
        else:
            self.group_input = None

        # ---- Baaki optional fields "مزید تفصیل" ke peeche ----
        self.more_details_btn = QPushButton("مزید تفصیل ▾")
        self.more_details_btn.setFlat(True)
        self.more_details_btn.setStyleSheet(f"color: {COLOR_PRIMARY}; text-align: left; border: none; font-size: 12px;")
        self.more_details_btn.clicked.connect(self._toggle_more_details)
        layout.addWidget(self.more_details_btn)

        self.more_details_frame = QWidget()
        more_layout = QVBoxLayout()
        more_layout.setContentsMargins(0, 0, 0, 0)
        more_layout.setSpacing(8)

        more_layout.addWidget(self._label("والد/شوہر کا نام"))
        self.father_input = QLineEdit()
        self.father_input.setStyleSheet(self._input_style())
        more_layout.addWidget(self.father_input)

        more_layout.addWidget(self._label("شناختی کارڈ نمبر"))
        self.cnic_input = QLineEdit()
        self.cnic_input.setStyleSheet(self._input_style())
        more_layout.addWidget(self.cnic_input)

        more_layout.addWidget(self._label("پتہ"))
        self.address_input = QLineEdit()
        self.address_input.setStyleSheet(self._input_style())
        more_layout.addWidget(self.address_input)

        more_layout.addWidget(self._label("شہر"))
        self.city_input = QLineEdit()
        self.city_input.setStyleSheet(self._input_style())
        more_layout.addWidget(self.city_input)

        self.more_details_frame.setLayout(more_layout)
        self.more_details_frame.setVisible(False)
        layout.addWidget(self.more_details_frame)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        layout.addStretch()

        save_btn = QPushButton(f"✓ {self.label} محفوظ کریں")
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

        return panel

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

    def _build_existing_list_panel(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet(f"background-color: #FAFAFA; border-left: 1px solid {COLOR_BORDER};")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 20, 16, 20)
        panel.setLayout(layout)

        heading = QLabel(f"پہلے سے موجود {self.label} حضرات")
        heading.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(heading)

        hint = QLabel("نام لکھتے ہی نیچے ملتے جلتے نام دکھائی دیں گے — دہرائی سے بچنے کے لیے چیک کر لیں۔")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(hint)

        self.existing_table = QTableWidget()
        self.existing_table.setColumnCount(3)
        self.existing_table.setHorizontalHeaderLabels(["کوڈ", "نام", "موبائل"])
        self.existing_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.existing_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.existing_table)

        self._filter_existing_list()
        return panel

    def _filter_existing_list(self):
        search_text = self.name_input.text().strip()
        matches = get_parties(self.party_type, search_text)

        self.existing_table.setRowCount(len(matches))
        for row, party in enumerate(matches):
            self.existing_table.setItem(row, 0, QTableWidgetItem(party.party_code))
            self.existing_table.setItem(row, 1, QTableWidgetItem(party.name))
            self.existing_table.setItem(row, 2, QTableWidgetItem(party.mobile or ""))

    def _reload_groups(self):
        self.group_input.clear()
        self.group_input.addItem("(کوئی گروپ نہیں)", None)
        for group in get_customer_groups():
            self.group_input.addItem(group.name, group.id)

    def _add_new_group(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "نیا گروپ", "گروپ کا نام:")
        if ok and name.strip():
            add_customer_group(name)
            self._reload_groups()
            self.group_input.setCurrentText(name.strip())

    def _handle_save(self):
        self.error_label.setText("")
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()

        if not name:
            self.error_label.setText("نام لکھنا ضروری ہے۔")
            return

        duplicates = check_duplicate(name, mobile)
        if duplicates:
            existing = duplicates[0]
            reply = QMessageBox.question(
                self, "پہلے سے موجود ہے",
                f"'{existing.name}' ({existing.party_code}) اس موبائل/نام سے پہلے سے موجود ہے۔\n"
                f"کیا آپ پھر بھی نئی اندراج کرنا چاہتے ہیں؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        party = add_party(
            name=name,
            mobile=mobile,
            party_type=self.party_type,
            father_husband_name=self.father_input.text(),
            cnic=self.cnic_input.text(),
            address=self.address_input.text(),
            city=self.city_input.text(),
            opening_balance=self.opening_balance_input.value(),
            balance_type=self.balance_type_input.currentData(),
            group_id=self.group_input.currentData() if self.group_input else None,
        )
        self.saved_party = party
        self.accept()


class PartyPage(QWidget):
    def __init__(self, party_type: str, user=None):
        super().__init__()
        self.party_type = party_type
        self.user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        self.setLayout(layout)

        label = "گاہک" if self.party_type == "customer" else "سپلائر"
        heading = QLabel(f"{label} کھاتہ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(heading)

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(38)
        self.search_input.setPlaceholderText("نام، موبائل یا کوڈ سے تلاش کریں...")
        self.search_input.textChanged.connect(self.refresh)
        top_bar.addWidget(self.search_input)

        if self.party_type == "customer":
            self.group_filter = QComboBox()
            self.group_filter.setFixedHeight(38)
            self.group_filter.addItem("تمام گروپس", None)
            for group in get_customer_groups():
                self.group_filter.addItem(group.name, group.id)
            self.group_filter.currentIndexChanged.connect(self.refresh)
            top_bar.addWidget(self.group_filter)
        else:
            self.group_filter = None

        add_btn = QPushButton(f"+ نیا {label}")
        add_btn.setFixedHeight(38)
        add_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 0 16px; font-weight: bold; border-radius: 6px;"
        )
        add_btn.clicked.connect(self._open_add_dialog)
        top_bar.addWidget(add_btn)

        layout.addLayout(top_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["کوڈ", "نام", "موبائل", "شہر", "پرانا بقایا", "قسم", "گروپ", "عمل"]
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    def refresh(self):
        search_text = self.search_input.text().strip()
        group_id = self.group_filter.currentData() if self.group_filter else None
        parties = get_parties(self.party_type, search_text, group_id)

        if not parties:
            self.table.setRowCount(0)
            self.table.setColumnCount(8)
            label = "Customer" if self.party_type == "customer" else "Supplier"
            from ui.widgets import show_empty_state
            show_empty_state(self.table, f"ابھی تک کوئی {label} شامل نہیں ہوا۔")
            return

        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["کوڈ", "نام", "موبائل", "شہر", "پرانا بقایا", "قسم", "گروپ", "عمل"]
        )
        self.table.setRowCount(len(parties))
        for row, party in enumerate(parties):
            self.table.setItem(row, 0, QTableWidgetItem(party.party_code))
            self.table.setItem(row, 1, QTableWidgetItem(party.name))
            self.table.setItem(row, 2, QTableWidgetItem(party.mobile or ""))
            self.table.setItem(row, 3, QTableWidgetItem(party.city or ""))
            self.table.setItem(row, 4, QTableWidgetItem(rs(party.opening_balance)))
            self.table.setItem(row, 5, QTableWidgetItem(party.balance_type))
            self.table.setItem(row, 6, QTableWidgetItem(party.group.name if party.group else ""))

            ledger_btn = QPushButton("کھاتہ دیکھیں")
            ledger_btn.clicked.connect(lambda checked, pid=party.id: self._open_ledger(pid))
            self.table.setCellWidget(row, 7, ledger_btn)

    def _open_add_dialog(self):
        dialog = AddPartyDialog(self.party_type, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()


    def _open_ledger(self, party_id):
        dialog = LedgerDialog(party_id, self.user, self)
        dialog.exec()
        self.refresh()

    def refresh_data(self):
        self.refresh()
        
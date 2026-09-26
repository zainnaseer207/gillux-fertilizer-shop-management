"""
ui/returns/return_dialog.py

Ek hi dialog Sales Return aur Purchase Return dono ke liye — jaisa
PartyPage mein kiya tha. Original invoice ke returnable items
checkbox-jaise table mein dikhte hain, quantity edit ho sakti hai.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QDoubleSpinBox, QHeaderView, QMessageBox, QTextEdit
)

from services.return_service import (
    get_returnable_sale_items, get_returnable_purchase_items,
    save_sale_return, save_purchase_return,
)
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER


class ReturnDialog(QDialog):
    def __init__(self, return_type: str, original_id: int, invoice_label: str, user, parent=None):
        """
        return_type: "sale" ya "purchase"
        original_id: sale.id ya purchase.id
        """
        super().__init__(parent)
        self.return_type = return_type
        self.original_id = original_id
        self.user = user

        title = "Sales Return" if return_type == "sale" else "Purchase Return"
        self.setWindowTitle(f"{title} — {invoice_label}")
        self.resize(600, 450)

        self._build_ui()
        self._load_items()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        heading = QLabel("Return karne ke liye quantity likhein (0 = return nahi karna)")
        heading.setStyleSheet("font-weight: bold;")
        layout.addWidget(heading)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Product", "Available to Return", "Rate", "Return Qty"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Reason (optional) — e.g. 'quality theek nahi thi'")
        self.notes_input.setFixedHeight(60)
        layout.addWidget(self.notes_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        save_btn = QPushButton("Process Return")
        save_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _load_items(self):
        if self.return_type == "sale":
            self.items = get_returnable_sale_items(self.original_id)
        else:
            self.items = get_returnable_purchase_items(self.original_id)

        self.table.setRowCount(len(self.items))
        self.qty_inputs = []

        for row, item in enumerate(self.items):
            self.table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(item["available_qty"])))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rs. {item['rate']}"))

            qty_input = QDoubleSpinBox()
            qty_input.setMaximum(item["available_qty"])
            self.table.setCellWidget(row, 3, qty_input)
            self.qty_inputs.append(qty_input)

    def _handle_save(self):
        self.error_label.setText("")

        return_items = []
        for row, item in enumerate(self.items):
            qty = self.qty_inputs[row].value()
            if qty > 0:
                return_items.append({
                    "product_id": item["product_id"], "quantity": qty, "rate": item["rate"],
                })

        if not return_items:
            self.error_label.setText("Kam az kam ek product ki quantity likhein.")
            return

        notes = self.notes_input.toPlainText().strip()
        user_id = self.user.id if self.user else None

        try:
            if self.return_type == "sale":
                save_sale_return(self.original_id, return_items, notes, user_id)
            else:
                save_purchase_return(self.original_id, return_items, notes, user_id)
        except ValueError as e:
            self.error_label.setText(str(e))
            return

        QMessageBox.information(self, "Success", "Return process ho gaya.")
        self.accept()
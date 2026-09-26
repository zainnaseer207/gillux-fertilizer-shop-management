"""
ui/widgets.py

Chhote reusable UI helpers jo poore app mein use hote hain — taake
har jagah alag-alag empty-state code na likhna pade.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QSpinBox
from utils.constants import MAX_AMOUNT

def show_empty_state(table: QTableWidget, message: str):
    """
    Table mein koi data na ho to ek row banata hai jisme
    ek friendly message merge hoti hai (poori width mein).
    """
    table.setRowCount(1)
    table.setSpan(0, 0, 1, table.columnCount())

    item = QTableWidgetItem(message)
    item.setTextAlignment(Qt.AlignCenter)
    item.setFlags(Qt.ItemIsEnabled)  # non-editable, non-selectable
    table.setItem(0, 0, item)

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
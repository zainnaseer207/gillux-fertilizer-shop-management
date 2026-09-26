"""
ui/customers/group_summary_tab.py

Khaata section ka naya tab — har customer group ka total (کتنے گاہک،
کل وصولی باقی، کل ادائیگی باقی) ek nazar mein.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView

from services.party_service import get_group_wise_summary
from ui.theme import COLOR_PRIMARY


class GroupSummaryTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        heading = QLabel("گروپ کا خلاصہ")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(heading)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["گروپ", "گاہکوں کی تعداد", "کل وصولی باقی", "کل ادائیگی باقی"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {COLOR_PRIMARY}; color: white;
                font-weight: bold; padding: 8px;
            }}
        """)
        layout.addWidget(self.table)

    def refresh(self):
        rows = get_group_wise_summary()

        if not rows:
            self.table.setRowCount(0)
            from ui.widgets import show_empty_state
            show_empty_state(self.table, "ابھی تک کوئی گروپ نہیں بنایا گیا۔")
            return

        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(r["group_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(r["customer_count"])))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rs. {r['total_receivable']}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {r['total_payable']}"))

    def refresh_data(self):
        self.refresh()
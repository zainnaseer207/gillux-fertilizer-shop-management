"""
ui/dashboard/dashboard_page.py

GILLUX ka main Dashboard: summary cards (grid) + quick action buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QFrame, QLabel, QPushButton,
    QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from utils.formatting import format_money

from services.dashboard_service import get_dashboard_summary
from ui.theme import COLOR_PRIMARY, COLOR_TEXT_MUTED, COLOR_BORDER, COLOR_WHITE

# (Label, dictionary key, prefix jaise "Rs." — kuch cards number hain, kuch currency)
CARD_DEFINITIONS = [
    ("آج کی فروخت", "today_sales", "Rs. "),
    ("آج کی خریداری", "today_purchases", "Rs. "),
    ("کل نقدی (ہاتھ + بینک)", "cash_in_hand", "Rs. "),
    ("کل وصولی باقی", "total_receivable", "Rs. "),
    ("کل ادائیگی باقی", "total_payable", "Rs. "),
    ("اسٹاک کی مالیت", "stock_value", "Rs. "),
    ("آج کا منافع", "today_profit", "Rs. "),
    ("موجودہ اشیاء", "stock_items", ""),
]

QUICK_ACTIONS = [
    "نئی فروخت", "نئی خریداری", "نیا گاہک", "نیا سپلائر",
    "نئی چیز", "ادائیگی وصول کریں", "سپلائر کو ادا کریں", "اسٹاک دیکھیں",
]


class SummaryCard(QFrame):
    def __init__(self, title: str, value_text: str):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_WHITE};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
            }}
        """)
        self.setFixedHeight(90)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        self.setLayout(layout)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")

        self.value_label = QLabel(value_text)
        self.value_label.setStyleSheet(
            f"color: {COLOR_PRIMARY}; font-size: 22px; font-weight: bold;"
        )

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class DashboardPage(QWidget):
    quick_action_triggered = Signal(str)
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        outer_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)
        content.setLayout(content_layout)

        # ---- Summary cards grid ----
        cards_heading = QLabel("خلاصہ")
        cards_heading.setStyleSheet("font-size: 16px; font-weight: bold;")
        content_layout.addWidget(cards_heading)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(16)
        content_layout.addLayout(self.cards_grid)

        self.card_widgets = {}
        for i, (title, key, prefix) in enumerate(CARD_DEFINITIONS):
            card = SummaryCard(title, f"{prefix}0")
            self.card_widgets[key] = (card, prefix)
            row, col = divmod(i, 4)
            self.cards_grid.addWidget(card, row, col)

        # ---- Quick actions ----
        actions_heading = QLabel("فوری کام")
        actions_heading.setStyleSheet("font-size: 16px; font-weight: bold;")
        content_layout.addWidget(actions_heading)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(12)
        content_layout.addLayout(actions_grid)

        for i, action_name in enumerate(QUICK_ACTIONS):
            btn = QPushButton(action_name)
            btn.setFixedHeight(44)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_WHITE};
                    border: 1px solid {COLOR_PRIMARY};
                    color: {COLOR_PRIMARY};
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY};
                    color: {COLOR_WHITE};
                }}
            """)
            btn.clicked.connect(lambda checked, name=action_name: self._handle_quick_action(name))
            row, col = divmod(i, 4)
            actions_grid.addWidget(btn, row, col)

        content_layout.addStretch()

    def refresh(self):
        summary = get_dashboard_summary()
        for key, (card, prefix) in self.card_widgets.items():
            value = summary.get(key, 0)
            display = f"Rs. {format_money(value)}" if prefix else str(value)
            card.value_label.setText(display)

    def _handle_quick_action(self, action_name: str):
        # Ab ye MainWindow ko signal bhejta hai, jo sahi section khol kar
        # zaroorat hone par "Add" dialog bhi khud khol deta hai.
        self.quick_action_triggered.emit(action_name)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def refresh_data(self):
        self.refresh()
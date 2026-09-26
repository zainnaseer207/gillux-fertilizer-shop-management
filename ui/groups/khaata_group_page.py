"""
ui/groups/khaata_group_page.py

"Khaata" group — Customers aur Suppliers ki ledger, bilkul جیسا
asal کھاتہ بنام register hota hai (naam, jama, baqaya).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.customers.group_summary_tab import GroupSummaryTab
from ui.customers.party_page import PartyPage


class KhaataGroupPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.customers_page = PartyPage("customer", user)
        self.suppliers_page = PartyPage("supplier", user)
        self.group_summary_page = GroupSummaryTab()

        self.tabs.addTab(self.customers_page, "Customers Khaata")
        self.tabs.addTab(self.suppliers_page, "Suppliers Khaata")
        self.tabs.addTab(self.customers_page, "گاہک کھاتہ")
        self.tabs.addTab(self.suppliers_page, "سپلائر کھاتہ")
        self.tabs.addTab(self.group_summary_page, "گروپ کا خلاصہ")

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh_data"):
            widget.refresh_data()

    def refresh_data(self):
        self._on_tab_changed(self.tabs.currentIndex())

    def show_customers_tab(self):
        self.tabs.setCurrentWidget(self.customers_page)

    def show_suppliers_tab(self):
        self.tabs.setCurrentWidget(self.suppliers_page)
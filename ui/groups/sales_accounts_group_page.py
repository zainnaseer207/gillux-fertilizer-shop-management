"""
ui/groups/sales_accounts_group_page.py

"Sales & Accounts" group — Daily Sale (cash/credit) aur Accounts
(Cash in Hand, Expenses) ek jagah.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.sales.sale_page import SalePage
from ui.accounts.accounts_page import AccountsPage


class SalesAccountsGroupPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.sale_page = SalePage(user)
        self.accounts_page = AccountsPage(user)

        self.tabs.addTab(self.sale_page, "Daily Sale (Cash / Credit)")
        self.tabs.addTab(self.accounts_page, "Accounts (Cash in Hand)")

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh_data"):
            widget.refresh_data()

    def refresh_data(self):
        self._on_tab_changed(self.tabs.currentIndex())

    def show_sale_tab(self):
        self.tabs.setCurrentWidget(self.sale_page)

    def show_accounts_tab(self):
        self.tabs.setCurrentWidget(self.accounts_page)
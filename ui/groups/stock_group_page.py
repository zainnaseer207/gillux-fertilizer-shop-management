"""
ui/groups/stock_group_page.py

"Stock" group — Products, Purchases, aur ab Stock Overview/Adjustment/
Register bhi seedha tabs mein — koi popup dialog nahi, taake sab
kuch normal navigation se hamesha up-to-date rahe.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.products.product_page import ProductPage
from ui.purchases.purchase_page import PurchasePage
from ui.stock.stock_management_dialog import StockOverviewTab, StockAdjustmentTab, StockHistoryTab


class StockGroupPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.product_page = ProductPage(user)
        self.purchase_page = PurchasePage(user)
        self.overview_tab = StockOverviewTab()
        self.adjustment_tab = StockAdjustmentTab(user)
        self.history_tab = StockHistoryTab()

        self.tabs.addTab(self.product_page, "اشیاء / سٹاک")
        self.tabs.addTab(self.purchase_page, "خریداری")
        self.tabs.addTab(self.overview_tab, "سٹاک کا خلاصہ")
        self.tabs.addTab(self.adjustment_tab, "سٹاک ترمیم")
        self.tabs.addTab(self.history_tab, "سٹاک رجسٹر")

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh_data"):
            widget.refresh_data()
        elif hasattr(widget, "refresh"):
            widget.refresh()
        elif hasattr(widget, "_reload_products"):
            widget._reload_products()

    def refresh_data(self):
        self._on_tab_changed(self.tabs.currentIndex())

    def show_products_tab(self):
        self.tabs.setCurrentWidget(self.product_page)

    def show_purchases_tab(self):
        self.tabs.setCurrentWidget(self.purchase_page)

    def show_stock_register_tab(self):
        self.tabs.setCurrentWidget(self.history_tab)
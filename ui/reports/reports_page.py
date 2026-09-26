"""
ui/reports/reports_page.py

Reports section ka container — ab 6 reports hain: Profit, Sales,
Purchase, Stock, Customer, Supplier. Cash Book Report Accounts
section mein already maujood hai (Phase 13).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.reports.profit_report_page import ProfitReportPage
from ui.reports.sales_purchase_report_tabs import SalesReportTab, PurchaseReportTab
from ui.reports.snapshot_report_tabs import StockReportTab, CustomerReportTab, SupplierReportTab


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.profit_tab = ProfitReportPage()
        self.sales_tab = SalesReportTab()
        self.purchase_tab = PurchaseReportTab()
        self.stock_tab = StockReportTab()
        self.customer_tab = CustomerReportTab()
        self.supplier_tab = SupplierReportTab()

        self.tabs.addTab(self.sales_tab, "فروخت کی رپورٹ")
        self.tabs.addTab(self.purchase_tab, "خریداری کی رپورٹ")
        self.tabs.addTab(self.profit_tab, "منافع کی رپورٹ")
        self.tabs.addTab(self.stock_tab, "اسٹاک کی رپورٹ")
        self.tabs.addTab(self.customer_tab, "گاہک کی رپورٹ")
        self.tabs.addTab(self.supplier_tab, "سپلائر کی رپورٹ")

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        current = self.tabs.widget(index)
        if hasattr(current, "refresh"):
            current.refresh()

    def refresh_data(self):
        # Sidebar se aane par current tab refresh ho jaye
        self._on_tab_changed(self.tabs.currentIndex())
from ui.groups.stock_group_page import StockGroupPage
from ui.groups.khaata_group_page import KhaataGroupPage
from ui.groups.sales_accounts_group_page import SalesAccountsGroupPage
from utils.translations import t

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from ui.dashboard.dashboard_page import DashboardPage
from ui.reports.reports_page import ReportsPage
from ui.settings.settings_page import SettingsPage

from config.settings import APP_NAME, APP_SUBTITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from ui.stock.opening_stock_dialog import OpeningStockDialog
from ui.theme import (
    sidebar_stylesheet, header_stylesheet, logout_button_stylesheet, COLOR_TEXT_MUTED
)

# Sidebar sections — Phase 6 se aage har naam ka apna real module banega
SECTIONS = [
    "Dashboard",
    "Stock",
    "Khaata",
    "Sales & Accounts",
    "Reports",
    "Settings",
]


class PlaceholderPage(QWidget):
    """Abhi khaali page — sirf naam dikhata hai. Baad mein real module isko replace karega."""

    def __init__(self, title: str):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        label = QLabel(f"{title}\n\n(Ye module abhi build nahi hua — agle phases mein aayega)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"font-size: 16px; color: {COLOR_TEXT_MUTED};")
        layout.addWidget(label)


class MainWindow(QMainWindow):

    logout_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("لیاقت گل اینڈ کمیشن شاپ")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        central.setLayout(outer_layout)

        outer_layout.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body.setLayout(body_layout)
        outer_layout.addWidget(body, stretch=1)

        content_area = self._build_content_area()
        sidebar = self._build_sidebar()

        body_layout.addWidget(sidebar)
        body_layout.addWidget(content_area, stretch=1)

        outer_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(header_stylesheet())

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        header.setLayout(layout)

        brand_label = QLabel("لیاقت گل اینڈ کمیشن شاپ")
        brand_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(brand_label)

        layout.addStretch()

        user_label = QLabel(f"{self.user.full_name}  ({self.user.role.name})")
        user_label.setStyleSheet("color: white; font-size: 13px;")
        layout.addWidget(user_label)

        logout_btn = QPushButton(t("Logout"))
        logout_btn.setStyleSheet(logout_button_stylesheet())
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

        return header

    def _build_footer(self) -> QWidget:
        footer = QFrame()
        footer.setFixedHeight(38)
        footer.setStyleSheet("background-color: #3E2723;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 4, 0, 4)
        footer.setLayout(layout)

        rights_label = QLabel("© 2026 Liaqat Gill & Commission Shop. All rights reserved.")
        rights_label.setAlignment(Qt.AlignCenter)
        rights_label.setStyleSheet("color: #BCAAA4; font-size: 9.5px;")
        layout.addWidget(rights_label)

        powered_by_label = QLabel("Powered by GILLUX")
        powered_by_label.setAlignment(Qt.AlignCenter)
        powered_by_label.setStyleSheet("color: #8D6E63; font-size: 8.5px;")
        layout.addWidget(powered_by_label)

        return footer

    def _build_sidebar(self) -> QWidget:
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(sidebar_stylesheet())

        from ui.theme import SECTION_ICONS
        for section in SECTIONS:
            icon = SECTION_ICONS.get(section, "•")
            QListWidgetItem(f"{icon}   {t(section)}", self.sidebar)

        self.sidebar.currentRowChanged.connect(self._on_section_changed)
        self.sidebar.setCurrentRow(0)  # Dashboard default selected

        return self.sidebar

    def _on_section_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, "refresh_data"):
            current_widget.refresh_data()

    def _navigate_to_section(self, section_name: str):
            """Sidebar ko us section par switch karta hai jaisa user ne khud click kiya ho."""
            index = SECTIONS.index(section_name)
            self.sidebar.setCurrentRow(index)  # ye khud _on_section_changed() ko trigger karega
            return self.stack.widget(index)

    def _handle_quick_action(self, action_name: str):
        if action_name == "نئی فروخت":
            self._navigate_to_section("Sales & Accounts")
            self.sales_accounts_group.show_sale_tab()

        elif action_name == "نئی خریداری":
            self._navigate_to_section("Stock")
            self.stock_group.show_purchases_tab()

        elif action_name == "نیا گاہک":
            self._navigate_to_section("Khaata")
            self.khaata_group.show_customers_tab()
            self.khaata_group.customers_page._open_add_dialog()

        elif action_name == "نیا سپلائر":
            self._navigate_to_section("Khaata")
            self.khaata_group.show_suppliers_tab()
            self.khaata_group.suppliers_page._open_add_dialog()

        elif action_name == "نئی چیز":
            self._navigate_to_section("Stock")
            self.stock_group.show_products_tab()
            self.stock_group.product_page._open_add_dialog()

        elif action_name == "ادائیگی وصول کریں":
            self._navigate_to_section("Khaata")
            self.khaata_group.show_customers_tab()

        elif action_name == "سپلائر کو ادا کریں":
            self._navigate_to_section("Khaata")
            self.khaata_group.show_suppliers_tab()

        elif action_name == "اسٹاک دیکھیں":
            self._navigate_to_section("Stock")
            self.stock_group.show_stock_register_tab()

    def _build_content_area(self) -> QWidget:
        self.stack = QStackedWidget()

        for section in SECTIONS:
            if section == "Dashboard":
                self.dashboard_page = DashboardPage()
                self.dashboard_page.quick_action_triggered.connect(self._handle_quick_action)
                self.stack.addWidget(self.dashboard_page)
            elif section == "Stock":
                self.stock_group = StockGroupPage(self.user)
                self.stack.addWidget(self.stock_group)
            elif section == "Khaata":
                self.khaata_group = KhaataGroupPage(self.user)
                self.stack.addWidget(self.khaata_group)
            elif section == "Sales & Accounts":
                self.sales_accounts_group = SalesAccountsGroupPage(self.user)
                self.stack.addWidget(self.sales_accounts_group)
            elif section == "Reports":
                self.stack.addWidget(ReportsPage())
            elif section == "Settings":
                self.stack.addWidget(SettingsPage(self.user))
            else:
                self.stack.addWidget(PlaceholderPage(section))

        return self.stack
    

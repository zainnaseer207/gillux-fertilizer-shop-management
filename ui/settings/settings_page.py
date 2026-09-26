"""
ui/settings/settings_page.py

Settings section: Backup/Restore sabke liye, lekin User Management
aur Audit Log SIRF Admin ke liye dikhte hain (Section 33 — security).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel

from ui.settings.backup_dialog import BackupRestoreDialog
from ui.settings.audit_log_page import AuditLogPage
from ui.settings.user_management_page import UserManagementPage
from ui.theme import COLOR_PRIMARY, COLOR_WHITE
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


class GeneralSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        self.setLayout(layout)

        heading = QLabel("عمومی ترتیبات")
        heading.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(heading)

        backup_btn = QPushButton("ڈیٹا بیک اپ / بحال کریں")
        backup_btn.setFixedWidth(280)
        backup_btn.setFixedHeight(44)
        backup_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; font-weight: bold; border-radius: 6px;"
        )
        backup_btn.clicked.connect(self._open_backup_dialog)
        layout.addWidget(backup_btn)
        layout.addStretch()

        from web.mobile_server import get_mobile_url

        mobile_heading = QLabel("موبائل ویو (صرف دیکھنے کے لیے)")
        mobile_heading.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(mobile_heading)

        mobile_hint = QLabel(
            "موبائل پر یہ ایڈریس براؤزر میں کھولیں (اسی WiFi پر ہونا ضروری ہے):"
        )
        mobile_hint.setWordWrap(True)
        mobile_hint.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(mobile_hint)

        mobile_url_label = QLabel(get_mobile_url())
        mobile_url_label.setStyleSheet(
            "background-color: #E8F5E9; padding: 10px; border-radius: 6px; "
            "font-size: 15px; font-weight: bold; color: #1B5E20;"
        )
        mobile_url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(mobile_url_label)


    def _open_backup_dialog(self):
        dialog = BackupRestoreDialog(self)
        dialog.exec()




class SettingsPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        tabs.addTab(GeneralSettingsTab(), "عمومی")

        is_admin = user and user.role and user.role.name == "Admin"
        if is_admin:
            tabs.addTab(UserManagementPage(user), "صارفین کا انتظام")
            tabs.addTab(AuditLogPage(), "سرگرمی کا ریکارڈ")
        else:
            restricted = QWidget()
            restricted_layout = QVBoxLayout()
            restricted_layout.addWidget(QLabel("یہ حصہ صرف ایڈمن کے لیے ہے۔"))
            restricted.setLayout(restricted_layout)
            tabs.addTab(restricted, "محدود")
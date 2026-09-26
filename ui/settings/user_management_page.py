"""
ui/settings/user_management_page.py

Admin-only screen — naya user banana, disable/enable, password reset.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox, QLabel, QMessageBox
)

from services.user_management_service import (
    get_all_users, get_roles, create_new_user, toggle_user_active, reset_user_password
)
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER


class AddUserDialog(QDialog):
    def __init__(self, admin_user_id, parent=None):
        super().__init__(parent)
        self.admin_user_id = admin_user_id
        self.setWindowTitle("Add New User")
        self.resize(350, 280)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        self.full_name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_input = QComboBox()
        for role in get_roles():
            self.role_input.addItem(role.name, role.id)

        form.addRow("Full Name:", self.full_name_input)
        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)
        form.addRow("Role:", self.role_input)
        layout.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        layout.addWidget(self.error_label)

        save_btn = QPushButton("Create User")
        save_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;")
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        full_name = self.full_name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not full_name or not username or len(password) < 4:
            self.error_label.setText("Sab fields bharein, password kam az kam 4 characters ka ho.")
            return

        try:
            create_new_user(username, full_name, password, self.role_input.currentData(), self.admin_user_id)
        except ValueError as e:
            self.error_label.setText(str(e))
            return

        self.accept()


class ResetPasswordDialog(QDialog):
    def __init__(self, user_id, admin_user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.admin_user_id = admin_user_id
        self.setWindowTitle("Reset Password")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Naya password")
        layout.addWidget(QLabel("Naya Password:"))
        layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_DANGER};")
        layout.addWidget(self.error_label)

        save_btn = QPushButton("Reset Password")
        save_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;")
        save_btn.clicked.connect(self._handle_save)
        layout.addWidget(save_btn)

    def _handle_save(self):
        password = self.password_input.text()
        if len(password) < 4:
            self.error_label.setText("Password kam az kam 4 characters ka ho.")
            return

        reset_user_password(self.user_id, password, self.admin_user_id)
        self.accept()


class UserManagementPage(QWidget):
    def __init__(self, admin_user):
        super().__init__()
        self.admin_user = admin_user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        top_row = QHBoxLayout()
        heading = QLabel("User Management")
        heading.setStyleSheet("font-size: 15px; font-weight: bold;")
        top_row.addWidget(heading)
        top_row.addStretch()

        add_btn = QPushButton("+ Add User")
        add_btn.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 6px 16px; font-weight: bold;")
        add_btn.clicked.connect(self._open_add_dialog)
        top_row.addWidget(add_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Full Name", "Username", "Role", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        users = get_all_users()
        self.table.setRowCount(len(users))
        for row, u in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(u.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(u.username))
            self.table.setItem(row, 2, QTableWidgetItem(u.role.name if u.role else ""))
            self.table.setItem(row, 3, QTableWidgetItem("Active" if u.is_active else "Disabled"))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            toggle_btn = QPushButton("Disable" if u.is_active else "Enable")
            toggle_btn.clicked.connect(lambda checked, uid=u.id: self._toggle_active(uid))
            action_layout.addWidget(toggle_btn)

            reset_btn = QPushButton("Reset Password")
            reset_btn.clicked.connect(lambda checked, uid=u.id: self._open_reset_dialog(uid))
            action_layout.addWidget(reset_btn)

            self.table.setCellWidget(row, 4, action_widget)

    def _open_add_dialog(self):
        dialog = AddUserDialog(self.admin_user.id, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh()

    def _toggle_active(self, user_id):
        if user_id == self.admin_user.id:
            QMessageBox.warning(self, "Not Allowed", "Aap apna hi account disable nahi kar sakte.")
            return
        toggle_user_active(user_id, self.admin_user.id)
        self.refresh()

    def _open_reset_dialog(self, user_id):
        dialog = ResetPasswordDialog(user_id, self.admin_user.id, self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Success", "Password reset ho gaya.")
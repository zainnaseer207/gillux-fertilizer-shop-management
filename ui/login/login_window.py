"""
ui/login/login_window.py

GILLUX ka professional login screen — shop-branded banner (photo ke
bina, gradient + pattern se), Username/Password side-by-side,
Remember Me, aur developer credit footer.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QCheckBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import QRectF

from config.settings import APP_NAME
from services.authentication_service import (
    any_user_exists, create_first_admin, authenticate
)

SHOP_NAME = "Liaqat Gill & Commission Shop"
SHOP_NAME_URDU = "لیاقت گل اینڈ کمیشن شاپ"
APP_YEAR = "2026"


class FertilizerSackIcon(QWidget):
    """
    Khaad ki bori (fertilizer sack) ka simple, clean icon — QPainter se
    khud draw kiya hua, kisi image file ki zaroorat nahi.
    """

    def __init__(self):
        super().__init__()
        self.setFixedSize(56, 56)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # ---- Bori ka main body (beige/tan sack shape) ----
        sack_color = QColor("#E8D4A8")
        outline_color = QColor("#8D6E33")

        painter.setBrush(QBrush(sack_color))
        painter.setPen(QPen(outline_color, 1.5))

        body_rect = QRectF(8, 16, 40, 34)
        painter.drawRoundedRect(body_rect, 6, 6)

        # ---- Upar ki gathan/tie (bori ka bandha hua muh) ----
        painter.setBrush(QBrush(QColor("#33691E")))
        painter.setPen(QPen(QColor("#1B5E20"), 1))
        tie_rect = QRectF(20, 8, 16, 12)
        painter.drawRoundedRect(tie_rect, 3, 3)

        # ---- Bori ke oopar chhoti lakeer (fold line) ----
        painter.setPen(QPen(outline_color, 1))
        painter.drawLine(8, 24, 48, 24)

        # ---- Beech mein chhota label/patti (jaise fertilizer bag par hota hai) ----
        painter.setBrush(QBrush(QColor("#1B5E20")))
        painter.setPen(Qt.NoPen)
        label_rect = QRectF(14, 30, 28, 12)
        painter.drawRoundedRect(label_rect, 2, 2)

        painter.end()

class LoginWindow(QWidget):

    from PySide6.QtCore import Signal
    login_successful = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("لیاقت گل اینڈ کمیشن شاپ - لاگ ان")
        self.setMinimumSize(480, 640)
        self.setStyleSheet("background-color: #FDF6E9;")

        self.setup_mode = not any_user_exists()
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        self.setLayout(outer_layout)

        outer_layout.addWidget(self._build_banner())
        outer_layout.addWidget(self._build_form_card(), stretch=1)
        outer_layout.addWidget(self._build_footer())

    # ---------------- BANNER (photo ke bina, gradient + branding) ----------------

    def _build_banner(self) -> QWidget:
        banner = QFrame()
        banner.setFixedHeight(150)
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1B5E20, stop:1 #2E7D32
                );
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        banner.setLayout(layout)

        icon_widget = FertilizerSackIcon()
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_widget)
        layout.addLayout(icon_layout)

        shop_name_label = QLabel(SHOP_NAME)
        shop_name_label.setAlignment(Qt.AlignCenter)
        shop_name_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: white; letter-spacing: 1px;"
        )
        layout.addWidget(shop_name_label)

        subtitle_label = QLabel("Fertilizer Shop Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 11px; color: #C8E6C9;")
        layout.addWidget(subtitle_label)

        return banner

    # ---------------- FORM CARD ----------------

    def _build_form_card(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet("background-color: #FDF6E9;")

        layout = QVBoxLayout()
        layout.setContentsMargins(36, 28, 36, 20)
        layout.setSpacing(6)
        card.setLayout(layout)

        shop_name_label = QLabel(SHOP_NAME)
        shop_name_label.setAlignment(Qt.AlignCenter)
        shop_name_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B5E20;"
        )
        layout.addWidget(shop_name_label)

        shop_name_urdu_label = QLabel(SHOP_NAME_URDU)
        shop_name_urdu_label.setAlignment(Qt.AlignCenter)
        shop_name_urdu_label.setStyleSheet(
            "font-size: 16px; color: #33691E; font-weight: bold;"
        )
        layout.addWidget(shop_name_urdu_label)

        welcome_label = QLabel(
            "Create Admin Account" if self.setup_mode else "WELCOME TO SOFTWARE LOGIN"
        )
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(
            "font-size: 11px; color: #6D4C41; font-weight: bold; letter-spacing: 1px; margin-top: 6px; margin-bottom: 14px;"
        )
        layout.addWidget(welcome_label)

        # ---- Setup-mode ke liye Full Name field (login mode mein nahi chahiye) ----
        if self.setup_mode:
            layout.addWidget(self._field_label("Full Name"))
            self.full_name_input = self._styled_input("Apna pura naam likhein")
            layout.addWidget(self.full_name_input)
            layout.addSpacing(10)

        # ---- Username / Password side-by-side (jaisa design mein hai) ----
        fields_row = QHBoxLayout()
        fields_row.setSpacing(14)

        username_col = QVBoxLayout()
        username_col.addWidget(self._field_label("Username / ID"))
        self.username_input = self._styled_input("Enter Username")
        username_col.addWidget(self.username_input)
        fields_row.addLayout(username_col)

        password_col = QVBoxLayout()
        password_col.addWidget(self._field_label("Password"))
        self.password_input = self._styled_input("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_col.addWidget(self.password_input)
        fields_row.addLayout(password_col)

        layout.addLayout(fields_row)

        if self.setup_mode:
            layout.addSpacing(10)
            layout.addWidget(self._field_label("Confirm Password"))
            self.confirm_password_input = self._styled_input("Password dobara likhein")
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.confirm_password_input)

        # # ---- Remember Me + Forgot Password row ----
        # options_row = QHBoxLayout()
        # self.remember_checkbox = QCheckBox("Remember Me")
        # self.remember_checkbox.setStyleSheet("font-size: 11px; color: #555;")
        # options_row.addWidget(self.remember_checkbox)
        # options_row.addStretch()

        # if not self.setup_mode:
        #     forgot_label = QLabel("<a href='#' style='color:#1B5E20;'>Forgot Password?</a>")
        #     forgot_label.setStyleSheet("font-size: 11px;")
        #     forgot_label.setOpenExternalLinks(False)
        #     options_row.addWidget(forgot_label)

        # layout.addSpacing(10)
        # layout.addLayout(options_row)

        # ---- Show Password ----
        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.setStyleSheet("font-size: 11px; color: #555;")
        self.show_password_checkbox.stateChanged.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        layout.addSpacing(6)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #C62828; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        # ---- LOGIN button ----
        action_button = QPushButton("Create Admin Account" if self.setup_mode else "LOGIN")
        action_button.setFixedHeight(44)
        action_button.setStyleSheet("""
            QPushButton {
                background-color: #1B5E20;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
        """)
        action_button.clicked.connect(self._handle_submit)
        layout.addWidget(action_button)

        layout.addStretch()
        return card

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 11px; color: #5D4037; font-weight: bold;")
        return label

    def _styled_input(self, placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(38)
        field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #D7CCC8;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #1B5E20;
            }
        """)
        return field

    # ---------------- FOOTER ----------------

    def _build_footer(self) -> QWidget:
        footer = QFrame()
        footer.setFixedHeight(42)
        footer.setStyleSheet("background-color: #3E2723;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 4, 0, 4)
        footer.setLayout(layout)

        rights_label = QLabel(f"© {APP_YEAR} {SHOP_NAME}. All rights reserved.")
        rights_label.setAlignment(Qt.AlignCenter)
        rights_label.setStyleSheet("color: #BCAAA4; font-size: 9.5px;")
        layout.addWidget(rights_label)

        powered_by_label = QLabel("Powered by GILLUX")
        powered_by_label.setAlignment(Qt.AlignCenter)
        powered_by_label.setStyleSheet("color: #8D6E63; font-size: 8.5px;")
        layout.addWidget(powered_by_label)

        return footer

    # ---------------- LOGIC (Phase 3 se bilkul same) ----------------

    def _toggle_password_visibility(self, state):
        mode = QLineEdit.Normal if state else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        if self.setup_mode:
            self.confirm_password_input.setEchoMode(mode)

    def _handle_submit(self):
        self.error_label.setText("")
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("Username aur Password zaroori hain.")
            return

        if self.setup_mode:
            full_name = self.full_name_input.text().strip()
            confirm = self.confirm_password_input.text()

            if not full_name:
                self.error_label.setText("Full Name zaroori hai.")
                return
            if len(password) < 4:
                self.error_label.setText("Password kam az kam 4 characters ka ho.")
                return
            if password != confirm:
                self.error_label.setText("Password match nahi kar raha.")
                return

            user = create_first_admin(username, full_name, password)
            QMessageBox.information(self, "Success", "Admin account ban gaya! Ab login karein.")
            self.login_successful.emit(user)
        else:
            user = authenticate(username, password)
            if user is None:
                self.error_label.setText("Username ya Password ghalat hai.")
                return
            self.login_successful.emit(user)
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from database.database import init_db
from ui.login.login_window import LoginWindow
from ui.main_window import MainWindow
from web.mobile_server import start_mobile_server


class GilluxApp:
    """
    Login aur MainWindow ke beech switch karne ki responsibility yahan hai.
    Isko alag class banaya hai taake window references zinda rahein
    (warna Python unko garbage-collect karke turant band kar deta).
    """

    def __init__(self):
        self.login_window = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self, user):
        self.login_window.close()
        self.login_window = None

        self.main_window = MainWindow(user)
        self.main_window.logout_requested.connect(self.handle_logout)
        self.main_window.show()

    def handle_logout(self):
        self.main_window.close()
        self.main_window = None
        self.show_login()

    def handle_app_exit(self):
        """App band hote waqt automatic backup — data-loss risk kam karne ke liye."""
        try:
            from utils.backup import create_backup
            create_backup()
        except Exception:
            pass  # backup fail ho to bhi app close hone se na roke


def main():
    init_db()
    start_mobile_server()  # mobile view background mein chalna shuru ho jata hai

    app = QApplication(sys.argv)
    app_font = QFont("Jameel Noori Nastaleeq", 15)
    app_font.setBold(True)
    app.setFont(app_font)
    ...
    gillux_app = GilluxApp()  # reference zinda rakhna zaroori hai
    app.aboutToQuit.connect(gillux_app.handle_app_exit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
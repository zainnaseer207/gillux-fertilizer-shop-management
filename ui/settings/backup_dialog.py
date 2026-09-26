"""
ui/settings/backup_dialog.py

Backup/Restore screen. Restore par 2 confirmation steps hain
(1: file select karna, 2: "pakka overwrite karna hai?" warning)
taake koi galti se apna data na kho de.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox
)

from utils.backup import create_backup, restore_backup, list_backups
from ui.theme import COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER, COLOR_TEXT_MUTED


class BackupRestoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup / Restore")
        self.resize(550, 450)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        heading = QLabel("Database Backup")
        heading.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(heading)

        backup_row = QHBoxLayout()
        backup_btn = QPushButton("Create Backup Now")
        backup_btn.setStyleSheet(
            f"background-color: {COLOR_PRIMARY}; color: {COLOR_WHITE}; padding: 8px; font-weight: bold;"
        )
        backup_btn.clicked.connect(self._handle_backup)
        backup_row.addWidget(backup_btn)

        backup_custom_btn = QPushButton("Backup to Custom Location...")
        backup_custom_btn.clicked.connect(self._handle_backup_custom)
        backup_row.addWidget(backup_custom_btn)

        layout.addLayout(backup_row)

        hint = QLabel("Backups automatically 'backups' folder mein save hoti hain, aur app band karte waqt bhi khud-ba-khud ek backup ban jati hai.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; margin-top: 4px;")
        layout.addWidget(hint)

        restore_heading = QLabel("Restore Database")
        restore_heading.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 16px;")
        layout.addWidget(restore_heading)

        self.backups_list = QListWidget()
        layout.addWidget(self.backups_list)

        restore_row = QHBoxLayout()
        restore_selected_btn = QPushButton("Restore Selected Backup")
        restore_selected_btn.setStyleSheet(f"color: {COLOR_DANGER}; font-weight: bold;")
        restore_selected_btn.clicked.connect(self._handle_restore_selected)
        restore_row.addWidget(restore_selected_btn)

        restore_custom_btn = QPushButton("Restore from File...")
        restore_custom_btn.clicked.connect(self._handle_restore_custom)
        restore_row.addWidget(restore_custom_btn)

        layout.addLayout(restore_row)

    def refresh(self):
        self.backups_list.clear()
        for path in list_backups():
            item = QListWidgetItem(os.path.basename(path))
            item.setData(1, path)  # actual path store karte hain item ke andar
            self.backups_list.addItem(item)

    def _handle_backup(self):
        try:
            path = create_backup()
            QMessageBox.information(self, "Success", f"Backup ban gayi:\n{path}")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup nahi ban saki:\n{e}")

    def _handle_backup_custom(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup Kahan Save Karein", "gillux_backup.db", "Database Files (*.db)")
        if not path:
            return
        try:
            create_backup(custom_path=path)
            QMessageBox.information(self, "Success", f"Backup ban gayi:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup nahi ban saki:\n{e}")

    def _confirm_and_restore(self, backup_path):
        # Step 1: warning ke saath confirmation — restore current data OVERWRITE karega
        reply = QMessageBox.warning(
            self, "Pakka Restore Karna Hai?",
            "Ye action aapki CURRENT database ko is backup se OVERWRITE kar dega.\n\n"
            "Current data ka bhi ek safety-backup automatically ban jayega restore se pehle, "
            "lekin phir bhi ye action dhyan se karein.\n\n"
            "Kya aap pakka restore karna chahte hain?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            safety_backup_path = restore_backup(backup_path)
            QMessageBox.information(
                self, "Success",
                f"Database restore ho gayi.\n\n"
                f"Aapke restore se pehle wali database yahan safe hai:\n{safety_backup_path}\n\n"
                f"App ko band karke dobara kholein taake changes nazar aayein."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Restore nahi ho saka:\n{e}")

    def _handle_restore_selected(self):
        selected = self.backups_list.currentItem()
        if selected is None:
            QMessageBox.warning(self, "Select Karein", "Pehle list se ek backup select karein.")
            return
        backup_path = selected.data(1)
        self._confirm_and_restore(backup_path)

    def _handle_restore_custom(self):
        path, _ = QFileDialog.getOpenFileName(self, "Backup File Select Karein", "", "Database Files (*.db)")
        if not path:
            return
        self._confirm_and_restore(path)
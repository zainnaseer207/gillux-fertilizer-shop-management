"""
utils/backup.py

Database backup/restore — SQLite hone ki wajah se ye sirf file
copy/paste hai, koi complex export-import nahi chahiye.
"""

import os
import shutil
from datetime import datetime

from config.settings import DATABASE_PATH, BASE_DIR

BACKUP_FOLDER = os.path.join(BASE_DIR, "backups")


def _ensure_backup_folder():
    os.makedirs(BACKUP_FOLDER, exist_ok=True)


def create_backup(custom_path: str = None) -> str:
    """
    Database file ko copy karta hai. Agar custom_path diya gaya hai
    (user ne khud location choose ki), wahan save karta hai — warna
    default backups/ folder mein timestamp ke saath.

    Return: backup file ka path
    """
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError("Database file nahi mili.")

    if custom_path:
        destination = custom_path
        os.makedirs(os.path.dirname(destination), exist_ok=True)
    else:
        _ensure_backup_folder()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        destination = os.path.join(BACKUP_FOLDER, f"gillux_backup_{timestamp}.db")

    shutil.copy2(DATABASE_PATH, destination)
    return destination


def restore_backup(backup_path: str) -> str:
    """
    Restore se PEHLE current database ka bhi ek safety-backup bana leta
    hai (agar restore galti se ho jaye to bhi purana wapas mil sake),
    phir backup_path ko current database bana deta hai.

    Return: safety-backup ka path (jo restore se pehle bana)
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError("Backup file nahi mili.")

    safety_backup_path = create_backup()  # current state ka backup, restore se pehle
    shutil.copy2(backup_path, DATABASE_PATH)
    return safety_backup_path


def list_backups():
    """Default backups/ folder mein saari backup files, sabse nayi pehle."""
    _ensure_backup_folder()
    files = [
        os.path.join(BACKUP_FOLDER, f) for f in os.listdir(BACKUP_FOLDER)
        if f.endswith(".db")
    ]
    files.sort(key=os.path.getmtime, reverse=True)
    return files
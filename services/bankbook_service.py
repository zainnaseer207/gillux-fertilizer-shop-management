"""
services/bankbook_service.py
"""

from database.database import SessionLocal
from database.repositories import bankbook_repository as repo
from database.repositories.settings_repository import set_setting


def get_bank_balance() -> float:
    session = SessionLocal()
    try:
        return repo.get_bank_balance(session)
    finally:
        session.close()


def get_bankbook_rows():
    session = SessionLocal()
    try:
        return repo.build_bankbook_entries(session)
    finally:
        session.close()


def set_opening_bank_balance(amount: float):
    session = SessionLocal()
    try:
        set_setting(session, "opening_bank_balance", str(amount))
    finally:
        session.close()


def get_opening_bank_balance() -> float:
    session = SessionLocal()
    try:
        return repo.get_opening_bank_balance(session)
    finally:
        session.close()
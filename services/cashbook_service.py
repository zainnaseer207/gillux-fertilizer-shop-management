"""
services/cashbook_service.py
"""

from database.database import SessionLocal
from database.repositories import cashbook_repository as repo
from database.repositories.settings_repository import set_setting


def get_cash_in_hand() -> float:
    session = SessionLocal()
    try:
        return repo.get_cash_in_hand(session)
    finally:
        session.close()


def get_cashbook_rows():
    session = SessionLocal()
    try:
        return repo.build_cashbook_entries(session)
    finally:
        session.close()


def set_opening_cash(amount: float):
    session = SessionLocal()
    try:
        set_setting(session, "opening_cash", str(amount))
    finally:
        session.close()


def get_opening_cash() -> float:
    session = SessionLocal()
    try:
        return repo.get_opening_cash(session)
    finally:
        session.close()

def get_payment_method_summary():
    session = SessionLocal()
    try:
        return repo.get_payment_method_summary(session)
    finally:
        session.close()
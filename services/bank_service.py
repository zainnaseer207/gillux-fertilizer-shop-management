"""
services/bank_service.py
"""

from database.database import SessionLocal
from database.repositories import bank_repository as repo
from services.cashbook_service import get_cash_in_hand
from services.audit_service import log_action


def add_bank_account(name: str, opening_balance: float, user_id):
    if not name.strip():
        raise ValueError("اکاؤنٹ کا نام لکھنا ضروری ہے۔")

    session = SessionLocal()
    try:
        account = repo.create_account(session, name, opening_balance)
        log_action(user_id, "Bank Account Created", reference=account.name, description=f"Opening: Rs. {opening_balance}")
        return account
    finally:
        session.close()


def get_accounts_with_balances():
    session = SessionLocal()
    try:
        accounts = repo.list_accounts(session)
        return [
            {"id": a.id, "name": a.name, "balance": repo.get_account_balance(session, a.id)}
            for a in accounts
        ]
    finally:
        session.close()


def record_bank_transaction(account_id, transaction_type, amount, description, user_id):
    if amount <= 0:
        raise ValueError("رقم صفر سے زیادہ ہونی چاہیے۔")

    session = SessionLocal()
    try:
        txn = repo.record_transaction(session, account_id, transaction_type, amount, description, user_id)
        action = "Bank Deposit" if transaction_type == "deposit" else "Bank Withdrawal"
        log_action(user_id, action, reference=str(account_id), description=f"Rs. {amount}")
        return txn
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_account_history(account_id):
    session = SessionLocal()
    try:
        return repo.get_account_transactions(session, account_id)
    finally:
        session.close()


def get_total_cash_all_sources() -> dict:
    """Cash in Hand + sab banks ka total mila kar deta hai."""
    session = SessionLocal()
    try:
        cash_in_hand = get_cash_in_hand()
        total_bank = repo.get_total_bank_balance(session)
        return {
            "cash_in_hand": round(cash_in_hand, 2),
            "total_bank": round(total_bank, 2),
            "grand_total": round(cash_in_hand + total_bank, 2),
        }
    finally:
        session.close()
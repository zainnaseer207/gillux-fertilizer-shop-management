"""
services/ledger_service.py
"""

from database.database import SessionLocal
from database.repositories import ledger_repository as repo
from database.repositories import payment_repository as payment_repo
from services.audit_service import log_action


def get_party_ledger(party_id: int):
    session = SessionLocal()
    try:
        return repo.build_ledger(session, party_id)
    finally:
        session.close()


def record_payment(party_id, direction, amount, payment_method, reference, notes, user_id):
    if amount <= 0:
        raise ValueError("Amount 0 se zyada honi chahiye.")

    session = SessionLocal()
    try:
        payment = payment_repo.create_payment(
            session, party_id, direction, amount, payment_method, reference, notes, user_id
        )
        action = "Payment Received" if direction == "receive" else "Payment Paid"
        log_action(user_id, action, reference=reference, description=f"Rs. {amount}")
    finally:
        session.close()
    return payment
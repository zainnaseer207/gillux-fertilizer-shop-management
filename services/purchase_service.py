"""
services/purchase_service.py

UI (purchase_page.py) sirf inhi functions ko call karega.
"""

from database.database import SessionLocal
from database.repositories import purchase_repository as repo
from database.repositories.party_repository import list_parties
from database.repositories.product_repository import list_products
from services.audit_service import log_action


def get_suppliers(search_text: str = ""):
    session = SessionLocal()
    try:
        return list_parties(session, "supplier", search_text)
    finally:
        session.close()


def get_products(search_text: str = ""):
    session = SessionLocal()
    try:
        return list_products(session, search_text)
    finally:
        session.close()


def save_purchase(supplier_id, invoice_number, items, discount, paid_amount,
                   payment_method, notes, user_id):
    if not items:
        raise ValueError("Kam az kam ek product add karna zaroori hai.")

    session = SessionLocal()
    try:
        purchase = repo.create_purchase(
            session, supplier_id, invoice_number, items, discount,
            paid_amount, payment_method, notes, user_id,
        )
        log_action(user_id, "Purchase Created", reference=purchase.invoice_number, description=f"Total: Rs. {purchase.total}")
        return purchase
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_purchases(search_text: str = ""):
    session = SessionLocal()
    try:
        return repo.list_purchases(session, search_text)
    finally:
        session.close()
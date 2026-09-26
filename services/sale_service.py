"""
services/sale_service.py

UI (sale_page.py) sirf inhi functions ko call karega.
"""

from database.database import SessionLocal
from database.repositories import sale_repository as repo
from database.repositories.party_repository import list_parties
from database.repositories.product_repository import list_products
from services.audit_service import log_action

def get_customers(search_text: str = ""):
    session = SessionLocal()
    try:
        return list_parties(session, "customer", search_text)
    finally:
        session.close()


def get_products(search_text: str = ""):
    session = SessionLocal()
    try:
        return list_products(session, search_text)
    finally:
        session.close()


def save_sale(customer_id, items, discount, paid_amount, payment_method, notes, user_id):
    if not items:
        raise ValueError("Kam az kam ek product add karna zaroori hai.")

    session = SessionLocal()
    try:
        sale = repo.create_sale(
            session, customer_id, items, discount, paid_amount,
            payment_method, notes, user_id,
        )
        log_action(user_id, "Sale Created", reference=sale.invoice_number, description=f"Total: Rs. {sale.total}")
        return sale
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_sales(search_text: str = ""):
    session = SessionLocal()
    try:
        return repo.list_sales(session, search_text)
    finally:
        session.close()
"""
services/return_service.py
"""

from database.database import SessionLocal
from database.repositories import return_repository as repo


def get_returnable_sale_items(sale_id):
    session = SessionLocal()
    try:
        return repo.get_sale_items_for_return(session, sale_id)
    finally:
        session.close()


def get_returnable_purchase_items(purchase_id):
    session = SessionLocal()
    try:
        return repo.get_purchase_items_for_return(session, purchase_id)
    finally:
        session.close()


def save_sale_return(sale_id, items, notes, user_id):
    if not items:
        raise ValueError("Kam az kam ek product return karna zaroori hai.")
    session = SessionLocal()
    try:
        return repo.create_sale_return(session, sale_id, items, notes, user_id)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_purchase_return(purchase_id, items, notes, user_id):
    if not items:
        raise ValueError("Kam az kam ek product return karna zaroori hai.")
    session = SessionLocal()
    try:
        return repo.create_purchase_return(session, purchase_id, items, notes, user_id)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
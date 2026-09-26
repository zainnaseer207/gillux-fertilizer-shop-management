"""
services/expense_service.py
"""

from database.database import SessionLocal
from database.repositories import expense_repository as repo
from services.audit_service import log_action


def add_expense(category, description, amount, payment_method, user_id):
    if not category.strip():
        raise ValueError("Category likhna zaroori hai.")
    if amount <= 0:
        raise ValueError("Amount 0 se zyada honi chahiye.")

    session = SessionLocal()
    try:
        expense = repo.create_expense(session, category.strip(), description.strip(), amount, payment_method, user_id)
        log_action(user_id, "Expense Added", reference=category, description=f"Rs. {amount}")
        return expense
    finally:
        session.close()


def get_expenses(search_text: str = ""):
    session = SessionLocal()
    try:
        return repo.list_expenses(session, search_text)
    finally:
        session.close()
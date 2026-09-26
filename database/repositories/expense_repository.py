"""
database/repositories/expense_repository.py
"""

from datetime import datetime
from sqlalchemy.orm import joinedload
from database.models import Expense


def create_expense(session, category, description, amount, payment_method, user_id):
    expense = Expense(
        category=category, description=description, amount=amount,
        payment_method=payment_method, user_id=user_id,
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


def list_expenses(session, search_text: str = ""):
    query = session.query(Expense).options(joinedload(Expense.user))
    if search_text:
        query = query.filter(Expense.category.ilike(f"%{search_text}%"))
    return query.order_by(Expense.expense_date.desc()).all()


def sum_expenses(session, only_cash=True, date_from=None, date_to=None):
    query = session.query(Expense)
    if only_cash:
        query = query.filter(Expense.payment_method == "cash")
    if date_from:
        query = query.filter(Expense.expense_date >= date_from)
    if date_to:
        query = query.filter(Expense.expense_date <= date_to)
    return sum(float(e.amount) for e in query.all())
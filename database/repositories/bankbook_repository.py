"""
database/repositories/bankbook_repository.py

Bank Book bhi Cash Book jaisa hi COMPUTE hota hai — koi alag stored
balance nahi. Farq sirf itna hai: sirf payment_method == "bank transfer"
wale transactions count hote hain, aur opening balance ki key alag hai
("opening_bank_balance" vs "opening_cash").
"""

from database.models import Sale, Purchase, Payment, Expense
from database.repositories.settings_repository import get_setting


def get_opening_bank_balance(session) -> float:
    return float(get_setting(session, "opening_bank_balance", "0") or 0)


def get_bank_balance(session) -> float:
    opening = get_opening_bank_balance(session)

    bank_sales = sum(
        float(s.paid_amount) for s in session.query(Sale)
        .filter(Sale.payment_method == "bank transfer").all()
    )
    bank_purchases = sum(
        float(p.paid_amount) for p in session.query(Purchase)
        .filter(Purchase.payment_method == "bank transfer").all()
    )
    payments_received = sum(
        float(p.amount) for p in session.query(Payment)
        .filter_by(direction="receive", payment_method="bank transfer").all()
    )
    payments_paid = sum(
        float(p.amount) for p in session.query(Payment)
        .filter_by(direction="pay", payment_method="bank transfer").all()
    )
    bank_expenses = sum(
        float(e.amount) for e in session.query(Expense)
        .filter_by(payment_method="bank transfer").all()
    )

    return opening + bank_sales + payments_received - bank_purchases - payments_paid - bank_expenses


def build_bankbook_entries(session):
    """Bank Book screen ke liye har bank transaction ki list, date order mein."""
    entries = []

    for s in session.query(Sale).filter(Sale.payment_method == "bank transfer").all():
        if float(s.paid_amount) > 0:
            entries.append({
                "date": s.sale_date, "description": f"Bank Sale — {s.invoice_number}",
                "amount_in": float(s.paid_amount), "amount_out": 0,
            })

    for p in session.query(Purchase).filter(Purchase.payment_method == "bank transfer").all():
        if float(p.paid_amount) > 0:
            entries.append({
                "date": p.purchase_date, "description": f"Bank Purchase — {p.purchase_number}",
                "amount_in": 0, "amount_out": float(p.paid_amount),
            })

    for pay in session.query(Payment).filter_by(payment_method="bank transfer").all():
        if pay.direction == "receive":
            entries.append({
                "date": pay.payment_date, "description": "Payment Received (Bank)",
                "amount_in": float(pay.amount), "amount_out": 0,
            })
        else:
            entries.append({
                "date": pay.payment_date, "description": "Payment Paid to Supplier (Bank)",
                "amount_in": 0, "amount_out": float(pay.amount),
            })

    for e in session.query(Expense).filter_by(payment_method="bank transfer").all():
        entries.append({
            "date": e.expense_date, "description": f"Expense — {e.category}",
            "amount_in": 0, "amount_out": float(e.amount),
        })

    entries.sort(key=lambda x: x["date"])

    running_balance = get_opening_bank_balance(session)
    rows = [{"date": None, "description": "Opening Bank Balance", "amount_in": running_balance, "amount_out": 0, "balance": running_balance}]

    for e in entries:
        running_balance += e["amount_in"] - e["amount_out"]
        rows.append({**e, "balance": running_balance})

    return rows
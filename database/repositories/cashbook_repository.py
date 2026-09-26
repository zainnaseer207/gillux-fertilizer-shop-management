"""
database/repositories/cashbook_repository.py

Cash Book yahan se COMPUTE hota hai — koi alag stored balance nahi,
taake conflicting sources na banein (Section 19 ki requirement).
"""

from database.models import Sale, Purchase, Payment, Expense
from database.repositories.settings_repository import get_setting


def get_opening_cash(session) -> float:
    return float(get_setting(session, "opening_cash", "0") or 0)


def get_cash_in_hand(session) -> float:
    opening = get_opening_cash(session)

    cash_sales = sum(
        float(s.paid_amount) for s in session.query(Sale)
        .filter(Sale.payment_method.in_(["cash", "partial"])).all()
    )
    cash_purchases = sum(
        float(p.paid_amount) for p in session.query(Purchase)
        .filter(Purchase.payment_method.in_(["cash", "partial"])).all()
    )
    payments_received = sum(
        float(p.amount) for p in session.query(Payment)
        .filter_by(direction="receive", payment_method="cash").all()
    )
    payments_paid = sum(
        float(p.amount) for p in session.query(Payment)
        .filter_by(direction="pay", payment_method="cash").all()
    )
    cash_expenses = sum(
        float(e.amount) for e in session.query(Expense)
        .filter_by(payment_method="cash").all()
    )

    return opening + cash_sales + payments_received - cash_purchases - payments_paid - cash_expenses


def build_cashbook_entries(session):
    """Cash Book screen ke liye har cash transaction ki list, date order mein."""
    entries = []

    for s in session.query(Sale).filter(Sale.payment_method.in_(["cash", "partial"])).all():
        if float(s.paid_amount) > 0:
            entries.append({
                "date": s.sale_date, "description": f"Cash Sale — {s.invoice_number}",
                "cash_in": float(s.paid_amount), "cash_out": 0,
            })

    for p in session.query(Purchase).filter(Purchase.payment_method.in_(["cash", "partial"])).all():
        if float(p.paid_amount) > 0:
            entries.append({
                "date": p.purchase_date, "description": f"Cash Purchase — {p.purchase_number}",
                "cash_in": 0, "cash_out": float(p.paid_amount),
            })

    for pay in session.query(Payment).filter_by(payment_method="cash").all():
        if pay.direction == "receive":
            entries.append({
                "date": pay.payment_date, "description": "Payment Received",
                "cash_in": float(pay.amount), "cash_out": 0,
            })
        else:
            entries.append({
                "date": pay.payment_date, "description": "Payment Paid to Supplier",
                "cash_in": 0, "cash_out": float(pay.amount),
            })

    for e in session.query(Expense).filter_by(payment_method="cash").all():
        entries.append({
            "date": e.expense_date, "description": f"Expense — {e.category}",
            "cash_in": 0, "cash_out": float(e.amount),
        })

    entries.sort(key=lambda x: x["date"])

    running_balance = get_opening_cash(session)
    rows = [{"date": None, "description": "Opening Cash", "cash_in": running_balance, "cash_out": 0, "balance": running_balance}]

    for e in entries:
        running_balance += e["cash_in"] - e["cash_out"]
        rows.append({**e, "balance": running_balance})

    return rows

def get_payment_method_summary(session):
    """
    Har payment method (cash, bank transfer, cheque, other) ka net total
    dikhata hai — taake non-cash transactions bhi kahin visible rahein,
    chahe wo Cash in Hand mein count na hon.
    """
    from database.models import Sale, Purchase, Payment, Expense

    methods = {}

    def add_to_method(method, amount_in=0, amount_out=0):
        if method not in methods:
            methods[method] = {"in": 0.0, "out": 0.0}
        methods[method]["in"] += amount_in
        methods[method]["out"] += amount_out

    for s in session.query(Sale).all():
        if float(s.paid_amount) > 0:
            add_to_method(s.payment_method, amount_in=float(s.paid_amount))

    for p in session.query(Purchase).all():
        if float(p.paid_amount) > 0:
            add_to_method(p.payment_method, amount_out=float(p.paid_amount))

    for pay in session.query(Payment).all():
        if pay.direction == "receive":
            add_to_method(pay.payment_method, amount_in=float(pay.amount))
        else:
            add_to_method(pay.payment_method, amount_out=float(pay.amount))

    for e in session.query(Expense).all():
        add_to_method(e.payment_method, amount_out=float(e.amount))

    result = []
    for method, totals in methods.items():
        result.append({
            "method": method,
            "total_in": round(totals["in"], 2),
            "total_out": round(totals["out"], 2),
            "net": round(totals["in"] - totals["out"], 2),
        })
    return result
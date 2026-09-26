"""
database/repositories/ledger_repository.py

Ek party ki poori ledger banata hai: opening balance + sales/purchases
+ returns + payments, sab ko date-order mein arrange karke running
balance calculate karta hai.
"""

from database.models import Party, Sale, Purchase, Payment, ReturnTransaction


def build_ledger(session, party_id: int):
    party = session.query(Party).filter_by(id=party_id).first()
    if party is None:
        raise ValueError("Party nahi mili.")

    entries = []

    if party.is_customer:
        sales = session.query(Sale).filter_by(customer_id=party_id).all()
        for s in sales:
            entries.append({
                "date": s.sale_date,
                "description": "Sale",
                "reference": s.invoice_number,
                "debit": float(s.total),
                "credit": 0,
            })

    if party.is_supplier:
        purchases = session.query(Purchase).filter_by(supplier_id=party_id).all()
        for p in purchases:
            entries.append({
                "date": p.purchase_date,
                "description": "Purchase",
                "reference": p.purchase_number,
                "debit": 0,
                "credit": float(p.total),
            })

    return_txns = session.query(ReturnTransaction).filter_by(party_id=party_id).all()
    for r in return_txns:
        if r.return_type == "sale_return":
            entries.append({
                "date": r.return_date,
                "description": "Sale Return",
                "reference": r.return_number,
                "debit": 0,
                "credit": float(r.total),
            })
        else:
            entries.append({
                "date": r.return_date,
                "description": "Purchase Return",
                "reference": r.return_number,
                "debit": float(r.total),
                "credit": 0,
            })

    payments = session.query(Payment).filter_by(party_id=party_id).all()
    for pay in payments:
        if pay.direction == "receive":
            entries.append({
                "date": pay.payment_date,
                "description": "Payment Received",
                "reference": pay.reference or "",
                "debit": 0,
                "credit": float(pay.amount),
            })
        else:
            entries.append({
                "date": pay.payment_date,
                "description": "Payment Paid",
                "reference": pay.reference or "",
                "debit": float(pay.amount),
                "credit": 0,
            })

    # Date ke hisaab se sort (purani transaction pehle) taake running balance sahi bane
    entries.sort(key=lambda e: e["date"])

    opening = float(party.opening_balance or 0)

    if party.balance_type == "receivable":
        running_balance = opening
    else:
        running_balance = -opening

    ledger_rows = [{
        "date": None,
        "description": "Opening Balance",
        "reference": "",
        "debit": opening if party.balance_type == "receivable" else 0,
        "credit": opening if party.balance_type == "payable" else 0,
        "balance": running_balance,
    }]

    for e in entries:
        running_balance += e["debit"] - e["credit"]
        ledger_rows.append({
            "date": e["date"],
            "description": e["description"],
            "reference": e["reference"],
            "debit": e["debit"],
            "credit": e["credit"],
            "balance": running_balance,
        })

    return {
        "party": party,
        "rows": ledger_rows,
        "final_balance": running_balance,
    }
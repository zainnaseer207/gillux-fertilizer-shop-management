"""
database/repositories/reports_repository.py

Har report ki raw database query yahan hai.
"""

from sqlalchemy.orm import joinedload
from database.models import Sale, Purchase, Product, Party, ReturnTransaction


def sales_report(session, start, end):
    sales = (
        session.query(Sale)
        .options(joinedload(Sale.customer))
        .filter(Sale.sale_date.between(start, end))
        .order_by(Sale.sale_date.desc())
        .all()
    )
    total_sales = sum(float(s.total) for s in sales)
    total_paid = sum(float(s.paid_amount) for s in sales)
    total_credit = sum(float(s.remaining_amount) for s in sales)
    total_discount = sum(float(s.discount) for s in sales)

    returns = (
        session.query(ReturnTransaction)
        .filter(ReturnTransaction.return_type == "sale_return")
        .filter(ReturnTransaction.return_date.between(start, end))
        .all()
    )
    total_returns = sum(float(r.total) for r in returns)

    return {
        "rows": sales,
        "totals": {
            "total_sales": round(total_sales, 2),
            "total_paid": round(total_paid, 2),
            "total_credit": round(total_credit, 2),
            "total_discount": round(total_discount, 2),
            "total_returns": round(total_returns, 2),
        },
    }


def purchase_report(session, start, end):
    purchases = (
        session.query(Purchase)
        .options(joinedload(Purchase.supplier))
        .filter(Purchase.purchase_date.between(start, end))
        .order_by(Purchase.purchase_date.desc())
        .all()
    )
    total_purchases = sum(float(p.total) for p in purchases)
    total_paid = sum(float(p.paid_amount) for p in purchases)
    total_credit = sum(float(p.remaining_amount) for p in purchases)

    returns = (
        session.query(ReturnTransaction)
        .filter(ReturnTransaction.return_type == "purchase_return")
        .filter(ReturnTransaction.return_date.between(start, end))
        .all()
    )
    total_returns = sum(float(r.total) for r in returns)

    return {
        "rows": purchases,
        "totals": {
            "total_purchases": round(total_purchases, 2),
            "total_paid": round(total_paid, 2),
            "total_credit": round(total_credit, 2),
            "total_returns": round(total_returns, 2),
        },
    }


def stock_report(session):
    products = (
        session.query(Product)
        .options(joinedload(Product.unit))
        .filter(Product.is_active == True)
        .order_by(Product.name)
        .all()
    )
    rows = []
    for p in products:
        stock = float(p.current_stock or 0)
        avg_cost = float(p.avg_cost or 0)
        sale_price = float(p.sale_price or 0)
        stock_value = stock * avg_cost
        sale_value = stock * sale_price
        rows.append({
            "product": p, "stock": stock, "avg_cost": avg_cost,
            "stock_value": round(stock_value, 2), "sale_value": round(sale_value, 2),
            "estimated_margin": round(sale_value - stock_value, 2),
            "is_low": stock <= float(p.min_stock_level or 0) and p.min_stock_level > 0,
        })
    return rows


def customer_report(session):
    from database.repositories.ledger_repository import build_ledger

    customers = session.query(Party).filter_by(is_customer=True, is_active=True).all()
    rows = []
    for c in customers:
        total_sales = sum(float(s.total) for s in session.query(Sale).filter_by(customer_id=c.id).all())
        total_paid = sum(float(s.paid_amount) for s in session.query(Sale).filter_by(customer_id=c.id).all())
        ledger = build_ledger(session, c.id)
        rows.append({
            "party": c, "total_sales": round(total_sales, 2),
            "total_paid": round(total_paid, 2), "balance": round(ledger["final_balance"], 2),
        })
    return rows


def supplier_report(session):
    from database.repositories.ledger_repository import build_ledger

    suppliers = session.query(Party).filter_by(is_supplier=True, is_active=True).all()
    rows = []
    for s in suppliers:
        total_purchases = sum(float(p.total) for p in session.query(Purchase).filter_by(supplier_id=s.id).all())
        total_paid = sum(float(p.paid_amount) for p in session.query(Purchase).filter_by(supplier_id=s.id).all())
        ledger = build_ledger(session, s.id)
        rows.append({
            "party": s, "total_purchases": round(total_purchases, 2),
            "total_paid": round(total_paid, 2), "balance": round(ledger["final_balance"], 2),
        })
    return rows
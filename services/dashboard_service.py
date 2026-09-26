"""
services/dashboard_service.py

Dashboard cards ab asal database se calculate hote hain.
"""

from datetime import datetime, time
from database.database import SessionLocal
from database.models import Sale, Purchase, Product, SaleItem, Party
from services.cashbook_service import get_cash_in_hand
from services.bank_service import get_total_cash_all_sources


def _today_range():
    today = datetime.utcnow().date()
    return datetime.combine(today, time.min), datetime.combine(today, time.max)


def get_dashboard_summary() -> dict:
    session = SessionLocal()
    try:
        start, end = _today_range()

        today_sales = sum(
            float(s.total) for s in session.query(Sale)
            .filter(Sale.sale_date.between(start, end)).all()
        )
        today_purchases = sum(
            float(p.total) for p in session.query(Purchase)
            .filter(Purchase.purchase_date.between(start, end)).all()
        )

        # Today's profit: aaj ki har sale item ka (rate - cost_price) * quantity
        today_sale_ids = [
            s.id for s in session.query(Sale).filter(Sale.sale_date.between(start, end)).all()
        ]
        today_profit = 0.0
        if today_sale_ids:
            items = session.query(SaleItem).filter(SaleItem.sale_id.in_(today_sale_ids)).all()
            today_profit = sum(
                (float(i.rate) - float(i.cost_price)) * float(i.quantity) for i in items
            )

        products = session.query(Product).filter_by(is_active=True).all()
        stock_value = sum(float(p.current_stock or 0) * float(p.avg_cost or 0) for p in products)
        stock_items = len(products)

        # Receivable/Payable: har party ka opening balance + transactions - payments,
        # simplified yahan (poori ledger detail Phase 12 ki screen mein hai)
        from database.repositories.ledger_repository import build_ledger

        total_receivable = 0.0
        total_payable = 0.0
        for party in session.query(Party).filter_by(is_active=True).all():
            ledger = build_ledger(session, party.id)
            balance = ledger["final_balance"]
            if balance > 0:
                total_receivable += balance
            elif balance < 0:
                total_payable += abs(balance)


        total_cash = get_total_cash_all_sources()

        return {
            "today_sales": round(today_sales, 2),
            "today_purchases": round(today_purchases, 2),
            "cash_in_hand": total_cash["grand_total"],
            "total_receivable": round(total_receivable, 2),
            "total_payable": round(total_payable, 2),
            "stock_value": round(stock_value, 2),
            "today_profit": round(today_profit, 2),
            "stock_items": stock_items,
        }
    finally:
        session.close()
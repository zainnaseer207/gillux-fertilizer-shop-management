"""
database/repositories/profit_repository.py

Profit Report ke liye saari calculation yahan hoti hai.
"""

from database.models import Sale, SaleItem, Expense


def calculate_profit_report(session, start_datetime, end_datetime):
    sales = session.query(Sale).filter(Sale.sale_date.between(start_datetime, end_datetime)).all()

    total_sales = sum(float(s.total) for s in sales)
    total_discount = sum(float(s.discount) for s in sales)

    sale_ids = [s.id for s in sales]
    cogs = 0.0
    if sale_ids:
        items = session.query(SaleItem).filter(SaleItem.sale_id.in_(sale_ids)).all()
        cogs = sum(float(i.cost_price) * float(i.quantity) for i in items)

    gross_profit = total_sales - cogs

    expenses = session.query(Expense).filter(
        Expense.expense_date.between(start_datetime, end_datetime)
    ).all()
    total_expenses = sum(float(e.amount) for e in expenses)

    net_profit = gross_profit - total_expenses

    return {
        "total_sales": round(total_sales, 2),
        "total_discount": round(total_discount, 2),
        "cogs": round(cogs, 2),
        "gross_profit": round(gross_profit, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "invoice_count": len(sales),
    }
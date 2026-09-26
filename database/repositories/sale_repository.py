"""
database/repositories/sale_repository.py

Sale create karne ki transaction. Stock validation yahan hoti hai —
agar available quantity se zyada bechne ki koshish ho, ValueError
raise hota hai aur POORI transaction rollback ho jati hai (koi
partial save nahi hota).
"""

from sqlalchemy.orm import joinedload
from database.models import Sale, SaleItem, Product
from database.repositories.stock_repository import record_movement


def generate_next_invoice_number(session) -> str:
    count = session.query(Sale).count()
    return f"INV{count + 1:05d}"


def create_sale(session, customer_id, items, discount, paid_amount,
                 payment_method, notes, user_id):
    """
    items: list of dicts -> [{"product_id":.., "quantity":.., "rate":..}, ...]

    STOCK VALIDATION: har item ke liye check karta hai ke kaafi stock
    hai ya nahi — na ho to ValueError raise hota hai, sale save nahi hoti.
    """
    for item in items:
        product = session.query(Product).filter_by(id=item["product_id"]).first()
        if product is None:
            raise ValueError("Product nahi mila.")
        if float(product.current_stock or 0) < item["quantity"]:
            raise ValueError(
                f"'{product.name}' ka stock kam hai. Available: {product.current_stock}, "
                f"Requested: {item['quantity']}"
            )

    subtotal = sum(item["quantity"] * item["rate"] for item in items)
    total = subtotal - discount
    remaining = max(total - paid_amount, 0)

    sale = Sale(
        invoice_number=generate_next_invoice_number(session),
        customer_id=customer_id,
        subtotal=subtotal,
        discount=discount,
        total=total,
        paid_amount=paid_amount,
        remaining_amount=remaining,
        payment_method=payment_method,
        notes=notes,
        user_id=user_id,
    )
    session.add(sale)
    session.flush()

    for item in items:
        product = session.query(Product).filter_by(id=item["product_id"]).first()
        amount = item["quantity"] * item["rate"]

        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            rate=item["rate"],
            amount=amount,
            cost_price=float(product.avg_cost or 0),
        )
        session.add(sale_item)

        record_movement(
            session,
            product_id=item["product_id"],
            movement_type="sale",
            quantity_out=item["quantity"],
            reference=f"Sale #{sale.invoice_number}",
            user_id=user_id,
        )

    session.commit()
    session.refresh(sale)
    return sale


def list_sales(session, search_text: str = ""):
    query = session.query(Sale).options(joinedload(Sale.customer))
    if search_text:
        like = f"%{search_text}%"
        query = query.filter(Sale.invoice_number.ilike(like))
    return query.order_by(Sale.created_at.desc()).all()
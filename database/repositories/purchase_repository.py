"""
database/repositories/purchase_repository.py

Purchase create karne ki asal DATABASE TRANSACTION yahan hoti hai.
Sab steps (purchase save + items save + stock update) ek hi
session/commit ke andar hain — agar beech mein error aaye, sab
rollback ho jayega (koi adha-adhura data save nahi hoga).
"""

from database.models import Purchase, PurchaseItem
from sqlalchemy.orm import joinedload
from database.repositories.stock_repository import record_movement
from database.models import Purchase, PurchaseItem, Product


def generate_next_purchase_number(session) -> str:
    count = session.query(Purchase).count()
    return f"PUR{count + 1:05d}"


def create_purchase(session, supplier_id, invoice_number, items, discount,
                     paid_amount, payment_method, notes, user_id):
    """
    items: list of dicts -> [{"product_id":.., "quantity":.., "rate":..}, ...]

    Return: saved Purchase object
    """
    subtotal = sum(item["quantity"] * item["rate"] for item in items)
    total = subtotal - discount
    remaining = max(total - paid_amount, 0)

    purchase = Purchase(
        purchase_number=generate_next_purchase_number(session),
        supplier_id=supplier_id,
        invoice_number=invoice_number,
        subtotal=subtotal,
        discount=discount,
        total=total,
        paid_amount=paid_amount,
        remaining_amount=remaining,
        payment_method=payment_method,
        notes=notes,
        user_id=user_id,
    )
    session.add(purchase)
    session.flush()  # purchase.id turant chahiye items ke liye, commit se pehle

    for item in items:
        amount = item["quantity"] * item["rate"]
        purchase_item = PurchaseItem(
            purchase_id=purchase.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            rate=item["rate"],
            amount=amount,
        )
        session.add(purchase_item)

        # Stock increase — Phase 8 ka hi function reuse ho raha hai
        record_movement(
            session,
            product_id=item["product_id"],
            movement_type="purchase",
            quantity_in=item["quantity"],
            unit_cost=item["rate"],
            reference=f"Purchase #{purchase.purchase_number}",
            user_id=user_id,
        )


        # Product ki reference purchase price ko is naye rate se update kar dete hain,
        # taake agli baar Purchase/Add Product form mein alag-alag values na likhni parein
        product = session.query(Product).filter_by(id=item["product_id"]).first()
        if product:
            product.purchase_price = item["rate"]

    session.commit()
    session.refresh(purchase)
    return purchase


def list_purchases(session, search_text: str = ""):
    query = session.query(Purchase).options(joinedload(Purchase.supplier))
    if search_text:
        like = f"%{search_text}%"
        query = query.filter(
            (Purchase.purchase_number.ilike(like)) |
            (Purchase.invoice_number.ilike(like))
        )
    return query.order_by(Purchase.created_at.desc()).all()
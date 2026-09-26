"""
database/repositories/return_repository.py

Return ki transaction: stock reverse + return record save, ek hi
commit ke andar (Section 25 — data integrity).
"""

from sqlalchemy.orm import joinedload
from database.models import (
    ReturnTransaction, ReturnItem, Sale, SaleItem, Purchase, PurchaseItem, Product
)
from database.repositories.stock_repository import record_movement


def generate_next_return_number(session) -> str:
    count = session.query(ReturnTransaction).count()
    return f"RET{count + 1:05d}"


def get_already_returned_qty(session, original_sale_id, original_purchase_id, product_id):
    """Is product ka is invoice se pehle kitna return ho chuka hai — double return rokne ke liye."""
    query = session.query(ReturnTransaction).join(ReturnItem)
    if original_sale_id:
        query = query.filter(ReturnTransaction.original_sale_id == original_sale_id)
    else:
        query = query.filter(ReturnTransaction.original_purchase_id == original_purchase_id)

    returns = query.filter(ReturnItem.product_id == product_id).all()
    total = 0.0
    for r in returns:
        for item in r.items:
            if item.product_id == product_id:
                total += float(item.quantity)
    return total


def create_sale_return(session, sale_id, items, notes, user_id):
    """
    items: [{"product_id":.., "quantity":.., "rate":..}, ...]

    Validation: return quantity original sale item quantity se zyada nahi honi chahiye
    (already-returned quantity minus kar ke).
    """
    sale = session.query(Sale).options(joinedload(Sale.items)).filter_by(id=sale_id).first()
    if sale is None:
        raise ValueError("Original sale nahi mili.")

    for item in items:
        original_item = next((i for i in sale.items if i.product_id == item["product_id"]), None)
        if original_item is None:
            raise ValueError("Ye product is invoice mein nahi tha.")

        already_returned = get_already_returned_qty(session, sale_id, None, item["product_id"])
        available_to_return = float(original_item.quantity) - already_returned

        if item["quantity"] > available_to_return:
            raise ValueError(
                f"Sirf {available_to_return} units hi return ho sakti hain (already {already_returned} return ho chuki)."
            )

    total = sum(item["quantity"] * item["rate"] for item in items)

    return_txn = ReturnTransaction(
        return_number=generate_next_return_number(session),
        return_type="sale_return",
        party_id=sale.customer_id,
        original_sale_id=sale_id,
        total=total,
        notes=notes,
        user_id=user_id,
    )
    session.add(return_txn)
    session.flush()

    for item in items:
        amount = item["quantity"] * item["rate"]
        session.add(ReturnItem(
            return_id=return_txn.id, product_id=item["product_id"],
            quantity=item["quantity"], rate=item["rate"], amount=amount,
        ))
        # Stock wapas aata hai
        record_movement(
            session, product_id=item["product_id"], movement_type="sale_return",
            quantity_in=item["quantity"], reference=f"Return #{return_txn.return_number}",
            user_id=user_id,
        )

    session.commit()
    session.refresh(return_txn)
    return return_txn


def create_purchase_return(session, purchase_id, items, notes, user_id):
    purchase = session.query(Purchase).options(joinedload(Purchase.items)).filter_by(id=purchase_id).first()
    if purchase is None:
        raise ValueError("Original purchase nahi mili.")

    for item in items:
        original_item = next((i for i in purchase.items if i.product_id == item["product_id"]), None)
        if original_item is None:
            raise ValueError("Ye product is invoice mein nahi tha.")

        already_returned = get_already_returned_qty(session, None, purchase_id, item["product_id"])
        available_to_return = float(original_item.quantity) - already_returned

        if item["quantity"] > available_to_return:
            raise ValueError(
                f"Sirf {available_to_return} units hi return ho sakti hain (already {already_returned} return ho chuki)."
            )

        # Stock check — agar wo maal aage sale ho chuka hai to wapas nahi kar sakte
        product = session.query(Product).filter_by(id=item["product_id"]).first()
        if float(product.current_stock or 0) < item["quantity"]:
            raise ValueError(
                f"'{product.name}' ka stock kam hai return karne ke liye "
                f"(available: {product.current_stock}) — shayad ye maal pehle hi bik chuka hai."
            )

    total = sum(item["quantity"] * item["rate"] for item in items)

    return_txn = ReturnTransaction(
        return_number=generate_next_return_number(session),
        return_type="purchase_return",
        party_id=purchase.supplier_id,
        original_purchase_id=purchase_id,
        total=total,
        notes=notes,
        user_id=user_id,
    )
    session.add(return_txn)
    session.flush()

    for item in items:
        amount = item["quantity"] * item["rate"]
        session.add(ReturnItem(
            return_id=return_txn.id, product_id=item["product_id"],
            quantity=item["quantity"], rate=item["rate"], amount=amount,
        ))
        # Stock wapas jata hai
        record_movement(
            session, product_id=item["product_id"], movement_type="purchase_return",
            quantity_out=item["quantity"], reference=f"Return #{return_txn.return_number}",
            user_id=user_id,
        )

    session.commit()
    session.refresh(return_txn)
    return return_txn


def get_sale_items_for_return(session, sale_id):
    sale = session.query(Sale).options(joinedload(Sale.items).joinedload(SaleItem.product)).filter_by(id=sale_id).first()
    result = []
    for item in sale.items:
        already_returned = get_already_returned_qty(session, sale_id, None, item.product_id)
        available = float(item.quantity) - already_returned
        if available > 0:
            result.append({
                "product_id": item.product_id, "name": item.product.name,
                "rate": float(item.rate), "available_qty": available,
            })
    return result


def get_purchase_items_for_return(session, purchase_id):
    purchase = session.query(Purchase).options(
        joinedload(Purchase.items).joinedload(PurchaseItem.product)
    ).filter_by(id=purchase_id).first()
    result = []
    for item in purchase.items:
        already_returned = get_already_returned_qty(session, None, purchase_id, item.product_id)
        available = float(item.quantity) - already_returned
        if available > 0:
            result.append({
                "product_id": item.product_id, "name": item.product.name,
                "rate": float(item.rate), "available_qty": available,
            })
    return result
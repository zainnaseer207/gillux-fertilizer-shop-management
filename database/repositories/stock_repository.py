"""
database/repositories/stock_repository.py

Stock movements ki queries. Opening Stock is phase mein use ho raha hai,
lekin record_movement() function generic hai — Purchases/Sales/Returns
(agle phases) bhi isi ko reuse karenge.
"""

from sqlalchemy.orm import joinedload
from database.models import Product, StockMovement


def has_opening_stock(session, product_id: int) -> bool:
    """Ek product ke liye Opening Stock sirf ek hi baar set ho sakta hai."""
    return (
        session.query(StockMovement)
        .filter_by(product_id=product_id, movement_type="opening")
        .first()
        is not None
    )


def record_movement(
    session, product_id: int, movement_type: str,
    quantity_in: float = 0, quantity_out: float = 0,
    unit_cost: float = 0, reference: str = "", notes: str = "",
    user_id: int = None,
):
    """
    Generic stock movement banata hai AUR product.current_stock /
    avg_cost ko usi hisaab se update karta hai.

    Weighted Average Cost formula (Phase 14 mein detail se explain karenge):
        new_avg_cost = (old_stock * old_avg_cost + qty_in * unit_cost)
                       / (old_stock + qty_in)
    """
    product = session.query(Product).filter_by(id=product_id).first()
    if product is None:
        raise ValueError("Product nahi mila.")

    old_stock = float(product.current_stock or 0)
    old_avg_cost = float(product.avg_cost or 0)

    if quantity_in > 0:
        new_total_qty = old_stock + quantity_in
        if new_total_qty > 0:
            product.avg_cost = (
                (old_stock * old_avg_cost) + (quantity_in * unit_cost)
            ) / new_total_qty
        product.current_stock = new_total_qty
    elif quantity_out > 0:
        product.current_stock = old_stock - quantity_out
        # avg_cost sale/out par change nahi hota, sirf naye purchase par hota hai

    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity_in=quantity_in,
        quantity_out=quantity_out,
        unit_cost=unit_cost,
        balance_after=product.current_stock,
        reference=reference,
        notes=notes,
        user_id=user_id,
    )
    session.add(movement)
    session.flush()
    return movement


def list_products_with_stock_status(session, search_text: str = ""):
    query = (
        session.query(Product)
        .options(joinedload(Product.unit))
        .filter(Product.is_active == True)
    )
    if search_text:
        like = f"%{search_text}%"
        query = query.filter(Product.name.ilike(like))
    return query.order_by(Product.name).all()

def adjust_stock(session, product_id: int, delta_quantity: float, reason: str, user_id: int):
    """
    delta_quantity: positive ho to stock badhega (jaise galat kam gina tha),
                    negative ho to stock ghategaa (jaise damaged/lost)

    "adjustment" movement type record hota hai — history mein saaf dikhega
    ke ye manual correction thi, purchase/sale nahi.
    """
    if delta_quantity == 0:
        raise ValueError("Adjustment quantity zero nahi ho sakti.")

    if delta_quantity > 0:
        movement = record_movement(
            session, product_id=product_id, movement_type="adjustment",
            quantity_in=delta_quantity, reference="Manual Adjustment",
            notes=reason, user_id=user_id,
        )
    else:
        product = session.query(Product).filter_by(id=product_id).first()
        if product is None:
            raise ValueError("Product nahi mila.")
        if float(product.current_stock or 0) < abs(delta_quantity):
            raise ValueError(
                f"Itna stock kam nahi kar sakte — available: {product.current_stock}"
            )
        movement = record_movement(
            session, product_id=product_id, movement_type="adjustment",
            quantity_out=abs(delta_quantity), reference="Manual Adjustment",
            notes=reason, user_id=user_id,
        )

    session.commit()
    return movement


def list_low_stock(session):
    """Wo products jinka current_stock unke min_stock_level se kam/barabar hai."""
    products = (
        session.query(Product)
        .options(joinedload(Product.unit))
        .filter(Product.is_active == True)
        .all()
    )
    return [p for p in products if float(p.current_stock or 0) <= float(p.min_stock_level or 0) and p.min_stock_level > 0]


def get_stock_history(session, product_id: int = None):
    query = session.query(StockMovement).options(
        joinedload(StockMovement.product), joinedload(StockMovement.user)
    )
    if product_id:
        query = query.filter_by(product_id=product_id)
    return query.order_by(StockMovement.created_at.desc()).all()

def update_movement_notes(session, movement_id: int, notes: str):
    movement = session.query(StockMovement).filter_by(id=movement_id).first()
    if movement is None:
        raise ValueError("ریکارڈ نہیں ملا۔")
    movement.notes = notes
    session.commit()
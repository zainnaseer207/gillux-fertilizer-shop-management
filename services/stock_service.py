"""
services/stock_service.py

UI (opening_stock_dialog.py) sirf inhi functions ko call karega.
"""

from database.database import SessionLocal
from database.repositories import stock_repository as repo
from services.audit_service import log_action


def get_products_for_opening_stock(search_text: str = ""):
    session = SessionLocal()
    try:
        products = repo.list_products_with_stock_status(session, search_text)
        result = []
        for p in products:
            result.append({
                "id": p.id,
                "code": p.product_code,
                "name": p.name,
                "unit": p.unit.name if p.unit else "",
                "current_stock": float(p.current_stock or 0),
                "avg_cost": float(p.avg_cost or 0),
                "already_set": repo.has_opening_stock(session, p.id),
            })
        return result
    finally:
        session.close()


def set_opening_stock(product_id: int, quantity: float, cost_price: float, user_id: int):
    session = SessionLocal()
    try:
        if repo.has_opening_stock(session, product_id):
            raise ValueError("Is product ka Opening Stock pehle hi set ho chuka hai.")

        movement = repo.record_movement(
            session,
            product_id=product_id,
            movement_type="opening",
            quantity_in=quantity,
            unit_cost=cost_price,
            reference="Opening Stock",
            user_id=user_id,
        )
        session.commit()
        log_action(user_id, "Opening Stock Set", reference=str(product_id), description=f"Qty: {quantity}")
        return movement
    finally:
        session.close()

def get_all_products_with_stock(search_text: str = ""):
    session = SessionLocal()
    try:
        products = repo.list_products_with_stock_status(session, search_text)
        return [{
            "id": p.id,
            "code": p.product_code,
            "name": p.name,
            "unit": p.unit.name if p.unit else "",
            "current_stock": float(p.current_stock or 0),
            "min_stock_level": float(p.min_stock_level or 0),
            "avg_cost": float(p.avg_cost or 0),
            "is_low": float(p.current_stock or 0) <= float(p.min_stock_level or 0) and p.min_stock_level > 0,
        } for p in products]
    finally:
        session.close()


def adjust_product_stock(product_id: int, delta_quantity: float, reason: str, user_id: int):
    session = SessionLocal()
    try:
        movement = repo.adjust_stock(session, product_id, delta_quantity, reason, user_id)
        log_action(user_id, "Stock Adjusted", reference=str(product_id), description=f"{delta_quantity} — {reason}")
        return movement
    finally:
        session.close()


def get_stock_movement_history(product_id: int = None):
    session = SessionLocal()
    try:
        movements = repo.get_stock_history(session, product_id)
        return [{
            "id": m.id,
            "date": m.created_at.strftime("%Y-%m-%d %H:%M"),
            "product": m.product.name if m.product else "",
            "type": m.movement_type,
            "qty_in": float(m.quantity_in or 0),
            "qty_out": float(m.quantity_out or 0),
            "balance_after": float(m.balance_after or 0),
            "reference": m.reference or "",
            "notes": m.notes or "",
            "user": m.user.full_name if m.user else "",
        } for m in movements]
    finally:
        session.close()


def update_movement_description(movement_id: int, description: str):
    session = SessionLocal()
    try:
        repo.update_movement_notes(session, movement_id, description)
    finally:
        session.close()
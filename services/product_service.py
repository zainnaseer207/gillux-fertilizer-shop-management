"""
services/product_service.py

UI (product_page.py) sirf inhi functions ko call karega.
"""

from database.database import SessionLocal
from database.repositories import product_repository as repo
from services.audit_service import log_action

def get_categories():
    session = SessionLocal()
    try:
        return repo.list_categories(session)
    finally:
        session.close()


def add_category(name: str):
    session = SessionLocal()
    try:
        return repo.create_category(session, name)
    finally:
        session.close()


def get_units():
    session = SessionLocal()
    try:
        return repo.list_units(session)
    finally:
        session.close()


def add_unit(name: str):
    session = SessionLocal()
    try:
        return repo.create_unit(session, name)
    finally:
        session.close()


def check_duplicate_product(name: str, brand: str):
    session = SessionLocal()
    try:
        return repo.find_duplicate_product(session, name, brand)
    finally:
        session.close()


def add_product(
    name, brand, category_id, unit_id,
    purchase_price, sale_price, min_sale_price,
    min_stock_level, reorder_level, notes=""
):
    session = SessionLocal()
    try:
        return repo.create_product(
            session,
            name=name.strip(),
            brand=brand.strip(),
            category_id=category_id,
            unit_id=unit_id,
            purchase_price=purchase_price,
            sale_price=sale_price,
            min_sale_price=min_sale_price,
            min_stock_level=min_stock_level,
            reorder_level=reorder_level,
            notes=notes.strip(),
        )
        product = repo.create_product(session, ...)  # (jo pehle se hai, waisa hi rehne dein)
        log_action(None, "Product Created", reference=product.product_code, description=product.name)
        return product
    finally:
        session.close()


def get_products(search_text: str = ""):
    session = SessionLocal()
    try:
        return repo.list_products(session, search_text)
    finally:
        session.close()

def edit_product(product_id, name, brand, category_id, unit_id,
                  purchase_price, sale_price, min_sale_price,
                  min_stock_level, reorder_level, user_id):
    session = SessionLocal()
    try:
        product = repo.update_product(
            session, product_id,
            name=name.strip(), brand=brand.strip(),
            category_id=category_id, unit_id=unit_id,
            purchase_price=purchase_price, sale_price=sale_price,
            min_sale_price=min_sale_price, min_stock_level=min_stock_level,
            reorder_level=reorder_level,
        )
        log_action(
            user_id, "Product Price Updated", reference=product.product_code,
            description=f"نئی خریداری قیمت: Rs. {purchase_price}, نئی فروخت قیمت: Rs. {sale_price}"
        )
        return product
    finally:
        session.close()


def get_product_by_id(product_id):
    from database.models import Product
    from sqlalchemy.orm import joinedload
    session = SessionLocal()
    try:
        return (
            session.query(Product)
            .options(joinedload(Product.category), joinedload(Product.unit))
            .filter_by(id=product_id)
            .first()
        )
    finally:
        session.close()
"""
database/repositories/product_repository.py

Product/Category/Unit se related saari database queries.
"""

from sqlalchemy.orm import joinedload
from database.models import Product, Category, Unit


def generate_next_product_code(session) -> str:
    count = session.query(Product).count()
    return f"PR{count + 1:04d}"


def list_categories(session):
    return session.query(Category).order_by(Category.name).all()


def create_category(session, name: str) -> Category:
    category = Category(name=name.strip())
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def list_units(session):
    return session.query(Unit).order_by(Unit.name).all()


def create_unit(session, name: str) -> Unit:
    unit = Unit(name=name.strip())
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit


def find_duplicate_product(session, name: str, brand: str):
    query = session.query(Product).filter(Product.name.ilike(name.strip()))
    if brand:
        query = query.filter(Product.brand.ilike(brand.strip()))
    return query.first()


def create_product(session, **fields) -> Product:
    fields["product_code"] = generate_next_product_code(session)
    product = Product(**fields)
    session.add(product)
    session.commit()

    product_id = product.id
    return (
        session.query(Product)
        .options(joinedload(Product.category), joinedload(Product.unit))
        .filter_by(id=product_id)
        .first()
    )


def list_products(session, search_text: str = ""):
    query = (
        session.query(Product)
        .options(joinedload(Product.category), joinedload(Product.unit))
        .filter(Product.is_active == True)
    )

    if search_text:
        like = f"%{search_text}%"
        query = query.filter(
            (Product.name.ilike(like)) |
            (Product.product_code.ilike(like)) |
            (Product.brand.ilike(like))
        )

    return query.order_by(Product.name).all()

def update_product(session, product_id, **fields):
    product = session.query(Product).filter_by(id=product_id).first()
    if product is None:
        raise ValueError("چیز نہیں ملی۔")

    for key, value in fields.items():
        setattr(product, key, value)

    session.commit()
    session.refresh(product)
    return product
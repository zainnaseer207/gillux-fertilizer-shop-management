"""
database/models/product.py

Category aur Unit chhoti lookup tables hain — inhe hum Product form
ke andar se hi "+ New" button se add kar sakenge.

Product table mein current_stock abhi ek simple number hai. Phase 11
(Stock Management) mein hum ek alag "stock_movements" table banayenge
jo har stock change ki history rakhegi, aur current_stock ko
calculate/update karegi.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Category {self.name}>"


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Unit {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped["Category"] = relationship()

    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=True)
    unit: Mapped["Unit"] = relationship()

    purchase_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    sale_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    min_sale_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    # Phase 11 se aage stock_movements se update hoga; abhi 0 se start.
    current_stock: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    avg_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    min_stock_level: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    reorder_level: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.product_code} {self.name}>"
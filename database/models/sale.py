"""
database/models/sale.py

Sale = invoice header (customer, date, totals, payment)
SaleItem = har product line, jisme cost_price bhi save hota hai
           taake profit baad mein calculate ho sake (avg_cost us
           waqt ka jab sale hui thi — future purchases se change
           nahi hoga).
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.party import Party
from database.models.product import Product
from database.models.user import User


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), nullable=False)
    customer: Mapped["Party"] = relationship()

    sale_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    remaining_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")

    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale {self.invoice_number}>"


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=False)
    sale: Mapped["Sale"] = relationship(back_populates="items")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship()

    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    def __repr__(self):
        return f"<SaleItem product={self.product_id} qty={self.quantity}>"
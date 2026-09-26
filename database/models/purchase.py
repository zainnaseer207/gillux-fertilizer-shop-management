"""
database/models/purchase.py

Purchase = invoice header (supplier, date, totals, payment status)
PurchaseItem = har product line jo us purchase mein shamil hai

Ye "header + line items" pattern hai — Sales (Phase 10) mein bhi
bilkul yehi structure repeat hoga.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.product import Product

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.party import Party
    from database.models.user import User


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    supplier_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), nullable=False)
    supplier: Mapped["Party"] = relationship()

    purchase_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=True)  # supplier ka apna invoice #

    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    remaining_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")  # cash, credit, partial

    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["PurchaseItem"]] = relationship(back_populates="purchase", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Purchase {self.purchase_number}>"


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"), nullable=False)
    purchase: Mapped["Purchase"] = relationship(back_populates="items")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship()

    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)  # quantity * rate

    def __repr__(self):
        return f"<PurchaseItem product={self.product_id} qty={self.quantity}>"
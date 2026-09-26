"""
database/models/return_transaction.py

Return = header (kis original invoice ka return hai, kis party ka)
ReturnItem = kaunse products, kitni quantity return hui

return_type: "sale_return" ya "purchase_return"
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.party import Party
    from database.models.user import User
    from database.models.product import Product


class ReturnTransaction(Base):
    __tablename__ = "returns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    return_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    return_type: Mapped[str] = mapped_column(String(20), nullable=False)  # sale_return / purchase_return

    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), nullable=False)
    party: Mapped["Party"] = relationship()

    original_sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=True)
    original_purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"), nullable=True)

    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    return_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["ReturnItem"]] = relationship(back_populates="return_transaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Return {self.return_number} {self.return_type}>"


class ReturnItem(Base):
    __tablename__ = "return_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    return_id: Mapped[int] = mapped_column(ForeignKey("returns.id"), nullable=False)
    return_transaction: Mapped["ReturnTransaction"] = relationship(back_populates="items")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship()

    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    def __repr__(self):
        return f"<ReturnItem product={self.product_id} qty={self.quantity}>"
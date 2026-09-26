"""
database/models/stock.py

StockMovement har stock change ki history rakhta hai — chahe wo
Opening Stock ho, Purchase ho, Sale ho, ya Adjustment.

Product.current_stock is table se calculate/update hota hai,
lekin history yahan permanently mehfooz rehti hai.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.product import Product
    from database.models.user import User

from database.models.product import Product
from database.models.base import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship()

    # "opening", "purchase", "sale", "sale_return", "purchase_return",
    # "adjustment", "damaged", "lost"
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)

    quantity_in: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    quantity_out: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    balance_after: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    reference: Mapped[str] = mapped_column(String(150), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StockMovement {self.movement_type} product={self.product_id}>"
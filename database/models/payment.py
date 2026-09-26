"""
database/models/payment.py

Payment ek party (customer/supplier) ke against paisay ka lena-dena
record karta hai.

direction:
  "receive" -> customer se paisay mile (receivable kam hota hai)
  "pay"     -> supplier ko paisay diye (payable kam hota hai)
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), nullable=False)
    party: Mapped["Party"] = relationship()

    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # "receive" ya "pay"
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")

    reference: Mapped[str] = mapped_column(String(150), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Payment {self.direction} {self.amount} party={self.party_id}>"
"""
database/models/party.py

Party ek unified table hai — customer aur supplier dono isi table
mein rehte hain, kyunki (jaisa master prompt mein likha) ek party
dono role nibha sakti hai.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped,  mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.customer_group import CustomerGroup

from database.models.base import Base


class Party(Base):
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    party_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    father_husband_name: Mapped[str] = mapped_column(String(150), nullable=True)
    cnic: Mapped[str] = mapped_column(String(20), nullable=True)

    mobile: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    alternate_mobile: Mapped[str] = mapped_column(String(20), nullable=True)

    address: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)

    # Ek party dono ho sakti hai — isliye do alag flags, ek "type" field nahi.
    is_customer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("customer_groups.id"), nullable=True)
    group: Mapped["CustomerGroup"] = relationship()

    opening_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    # "receivable" = party humein paisay dega, "payable" = hum party ko dene hain
    balance_type: Mapped[str] = mapped_column(String(20), default="receivable")

    notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Party {self.party_code} {self.name}>"
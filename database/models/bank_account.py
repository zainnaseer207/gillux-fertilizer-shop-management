"""
database/models/bank_account.py

BankAccount = ek bank ka account (naam + starting balance)
BankTransaction = us account mein jama/nikasi ki history
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.product import Product
    from database.models.user import User


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "HBL Account"
    opening_balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BankAccount {self.name}>"


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    account_id: Mapped[int] = mapped_column(ForeignKey("bank_accounts.id"), nullable=False)
    account: Mapped["BankAccount"] = relationship()

    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "deposit" / "withdraw"
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BankTransaction {self.transaction_type} {self.amount}>"
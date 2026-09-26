"""
database/models/customer_group.py

Customer groups — jaise "عام گاہک"، "خاص گاہک" وغیرہ۔
"""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class CustomerGroup(Base):
    __tablename__ = "customer_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<CustomerGroup {self.name}>"
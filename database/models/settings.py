"""
database/models/settings.py

Simple key-value settings table. Opening Cash yahan store hoga.
Section 28 (Shop Settings) mein hum isi table ko aage extend karenge.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"
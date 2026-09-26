"""
database/models/audit_log.py

Har important action ka permanent record — kabhi delete/edit nahi
hota, sirf naye records add hote hain (immutable history).
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship()

    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Sale Created"
    reference: Mapped[str] = mapped_column(String(150), nullable=True)  # e.g. "INV00012"
    description: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} ref={self.reference}>"
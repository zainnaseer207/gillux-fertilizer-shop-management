"""
database/models/user.py

Ye file 2 tables define karti hai: Role aur User.

WHY ROLE ALAG TABLE HAI?
Hum roles ko hardcode ("admin", "employee" strings) nahi karna chahte,
kyunki aage chal kar naye roles add karne ki zaroorat pad sakti hai
(jaise "Cashier", "Manager"). Isliye Role ek proper table hai jisme
Admin future mein naye roles bhi add kar sakega.

RELATIONSHIP:
Ek Role ke multiple Users ho sakte hain (one-to-many).
Isliye User table mein role_id ek FOREIGN KEY hai jo Role.id ko point karta hai.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class Role(Base):
    """
    Roles table.

    Example rows:
        id=1, name="Admin"
        id=2, name="Employee"
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # "users" attribute se hum Python mein directly role.users likh kar
    # us role ke saare users nikal sakenge (list ki tarah).
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<Role id={self.id} name={self.name}>"


class User(Base):
    """
    Users table — login credentials aur account info yahan store hongi.

    IMPORTANT: password_hash mein KABHI plain text password store nahi hoga.
    Phase 3 mein bcrypt se hash banayenge.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Foreign key: is column mein hamesha koi valid roles.id hoga
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship(back_populates="users")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

"""
utils/security.py

Password hashing ke liye helper functions.
Kabhi bhi plain password database mein nahi jata — sirf hash jata hai.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """Plain password ko bcrypt hash mein convert karta hai (storage ke liye)."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Login ke waqt entered password ko stored hash ke against check karta hai."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
"""
services/authentication_service.py

Login/user-creation ki business logic.
"""

from sqlalchemy.orm import joinedload

from database.database import SessionLocal
from database.models import User, Role
from utils.security import hash_password, verify_password
from services.audit_service import log_action


def any_user_exists() -> bool:
    session = SessionLocal()
    try:
        return session.query(User).first() is not None
    finally:
        session.close()


def create_first_admin(username: str, full_name: str, password: str) -> User:
    session = SessionLocal()
    try:
        admin_role = session.query(Role).filter_by(name="Admin").first()
        if admin_role is None:
            admin_role = Role(name="Admin")
            session.add(admin_role)
            session.flush()

        new_user = User(
            username=username,
            full_name=full_name,
            password_hash=hash_password(password),
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(new_user)
        session.commit()

        user_id = new_user.id
        return (
            session.query(User)
            .options(joinedload(User.role))
            .filter_by(id=user_id)
            .first()
        )
    finally:
        session.close()


def authenticate(username: str, password: str):
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .options(joinedload(User.role))
            .filter_by(username=username)
            .first()
        )

        if user is None:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        log_action(user.id, "Login", reference=user.username)
        return user
    finally:
        session.close()
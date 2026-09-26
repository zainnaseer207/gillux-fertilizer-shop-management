"""
services/user_management_service.py

Admin-only user management: naye users banana, disable/enable
karna, password reset karna.
"""

from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import User, Role
from utils.security import hash_password
from services.audit_service import log_action


def get_all_users():
    session = SessionLocal()
    try:
        return (
            session.query(User)
            .options(joinedload(User.role))
            .order_by(User.full_name)
            .all()
        )
    finally:
        session.close()


def get_roles():
    session = SessionLocal()
    try:
        return session.query(Role).all()
    finally:
        session.close()


def create_new_user(username, full_name, password, role_id, admin_user_id):
    session = SessionLocal()
    try:
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            raise ValueError("Ye username pehle se maujood hai.")

        user = User(
            username=username, full_name=full_name,
            password_hash=hash_password(password), role_id=role_id, is_active=True,
        )
        session.add(user)
        session.commit()

        log_action(admin_user_id, "User Created", reference=username, description=full_name)
        return user
    finally:
        session.close()


def toggle_user_active(user_id, admin_user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user is None:
            raise ValueError("User nahi mila.")

        user.is_active = not user.is_active
        session.commit()

        action = "User Enabled" if user.is_active else "User Disabled"
        log_action(admin_user_id, action, reference=user.username)
    finally:
        session.close()


def reset_user_password(user_id, new_password, admin_user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user is None:
            raise ValueError("User nahi mila.")

        user.password_hash = hash_password(new_password)
        session.commit()

        log_action(admin_user_id, "Password Reset", reference=user.username)
    finally:
        session.close()
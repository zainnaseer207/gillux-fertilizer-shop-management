"""
services/settings_service.py
"""

from database.database import SessionLocal
from database.repositories.settings_repository import get_shop_info


def get_shop_settings() -> dict:
    session = SessionLocal()
    try:
        return get_shop_info(session)
    finally:
        session.close()
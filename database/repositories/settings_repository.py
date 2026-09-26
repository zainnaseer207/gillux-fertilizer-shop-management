"""
database/repositories/settings_repository.py
"""

from database.models import Setting


def get_setting(session, key: str, default=None):
    row = session.query(Setting).filter_by(key=key).first()
    return row.value if row else default


def set_setting(session, key: str, value: str):
    row = session.query(Setting).filter_by(key=key).first()
    if row:
        row.value = value
    else:
        row = Setting(key=key, value=value)
        session.add(row)
    session.commit()

DEFAULT_SHOP_SETTINGS = {
    "shop_name": "Your Shop Name",
    "shop_phone": "0300-0000000",
    "shop_address": "Your Shop Address, City",
    "shop_owner": "",
}


def ensure_default_shop_settings(session):
    """
    Pehli baar app chale to shop settings ko default values se
    initialize karta hai. Agar already set hain, kuch overwrite nahi karta.
    """
    for key, default_value in DEFAULT_SHOP_SETTINGS.items():
        existing = get_setting(session, key)
        if existing is None:
            set_setting(session, key, default_value)


def get_shop_info(session) -> dict:
    return {
        key: get_setting(session, key, default)
        for key, default in DEFAULT_SHOP_SETTINGS.items()
    }
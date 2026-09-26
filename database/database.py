"""
database/database.py

Ye file 3 kaam karti hai:
  1. Engine banati hai — yani gillux.db file se actual connection
  2. SessionLocal banati hai — jise hum data read/write ke liye use karenge
  3. init_db() function deti hai jo missing tables bana deta hai

HOW TO USE (aage ke phases mein):

    from database.database import SessionLocal

    session = SessionLocal()
    try:
        # session.add(...), session.query(...) waghera
        session.commit()
    finally:
        session.close()
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_PATH
from database.models import Base

# Data folder maujood na ho to bana dein (data/gillux.db yahan banegi)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# SQLite engine. "check_same_thread=False" desktop apps ke liye zaroori hai
# kyunki Qt kabhi kabhi background threads use karta hai.
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,  # True karenge jab SQL queries debug karni hon
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """
    Database file mein woh tables banata hai jo abhi maujood nahi hain,
    aur zaroori default data seed karta hai (shop settings, roles).
    """
    Base.metadata.create_all(bind=engine)

    from database.repositories.settings_repository import ensure_default_shop_settings
    from database.models import Role

    session = SessionLocal()
    try:
        ensure_default_shop_settings(session)

        # Default roles seed karte hain — taake User Management mein
        # "Employee" role bhi dropdown mein available ho
        for role_name in ["Admin", "Employee"]:
            existing = session.query(Role).filter_by(name=role_name).first()
            if existing is None:
                session.add(Role(name=role_name))
        session.commit()
    finally:
        session.close()

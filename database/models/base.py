"""
database/models/base.py

Ye file ek "Base" class deti hai jisko har model (User, Role, aur aage
Product, Customer waghera) inherit karega.

SQLAlchemy ko pata chalta hai ke kaunse Python classes actually
database tables hain sirf isliye kyunki wo is Base ko inherit karti hain.

Isko hum ek "master blueprint" samajh sakte hain — har table ka blueprint
isi ek jagah se nikalta hai.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

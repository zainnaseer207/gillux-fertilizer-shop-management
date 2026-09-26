"""
test_phase2.py

Ye ek chhota standalone test hai — GILLUX app se alag chalta hai —
sirf ye confirm karne ke liye ke database aur models sahi kaam kar rahe hain.

RUN KARNE KA TARIQA:
    python test_phase2.py

Ye karega:
  1. init_db() call — tables banayega agar nahi bani
  2. Ek "Admin" role add karega (agar pehle se nahi hai)
  3. Us role ko wapas database se parh kar print karega

Agar ye bina error ke chal jaye aur "Test Passed" print ho, Phase 2 theek hai.
"""

from database.database import init_db, SessionLocal
from database.models import Role

init_db()

session = SessionLocal()
try:
    existing = session.query(Role).filter_by(name="Admin").first()

    if existing is None:
        new_role = Role(name="Admin")
        session.add(new_role)
        session.commit()
        print(f"Naya role bana: {new_role}")
    else:
        print(f"Role already maujood hai: {existing}")

    all_roles = session.query(Role).all()
    print("Database mein saare roles:", all_roles)

    print("\n✅ Test Passed — database aur models sahi kaam kar rahe hain.")
finally:
    session.close()

"""
services/audit_service.py

log_action() ye function hai jo baaki saare services call karenge
har important action ke baad. Isko generic aur simple rakha hai
taake integrate karna asaan ho.
"""

from database.database import SessionLocal
from database.repositories import audit_repository as repo


def log_action(user_id, action, reference="", description=""):
    session = SessionLocal()
    try:
        repo.create_log(session, user_id, action, reference, description)
    finally:
        session.close()


def get_logs(search_text: str = ""):
    session = SessionLocal()
    try:
        return repo.list_logs(session, search_text)
    finally:
        session.close()
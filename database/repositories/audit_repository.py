"""
database/repositories/audit_repository.py
"""

from sqlalchemy.orm import joinedload
from database.models import AuditLog


def create_log(session, user_id, action, reference="", description=""):
    log = AuditLog(user_id=user_id, action=action, reference=reference, description=description)
    session.add(log)
    session.commit()
    return log


def list_logs(session, search_text: str = ""):
    query = session.query(AuditLog).options(joinedload(AuditLog.user))
    if search_text:
        like = f"%{search_text}%"
        query = query.filter(
            (AuditLog.action.ilike(like)) |
            (AuditLog.reference.ilike(like))
        )
    return query.order_by(AuditLog.created_at.desc()).limit(500).all()
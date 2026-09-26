"""
services/profit_service.py
"""

from database.database import SessionLocal
from database.repositories import profit_repository as repo
from utils.date_ranges import get_range


def get_profit_report(filter_name: str, custom_from=None, custom_to=None):
    start, end = get_range(filter_name, custom_from, custom_to)
    session = SessionLocal()
    try:
        report = repo.calculate_profit_report(session, start, end)
        report["period_start"] = start
        report["period_end"] = end
        return report
    finally:
        session.close()
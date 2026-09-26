"""
services/report_service.py
"""

from database.database import SessionLocal
from database.repositories import reports_repository as repo
from utils.date_ranges import get_range


def get_sales_report(filter_name, custom_from=None, custom_to=None):
    start, end = get_range(filter_name, custom_from, custom_to)
    session = SessionLocal()
    try:
        return repo.sales_report(session, start, end)
    finally:
        session.close()


def get_purchase_report(filter_name, custom_from=None, custom_to=None):
    start, end = get_range(filter_name, custom_from, custom_to)
    session = SessionLocal()
    try:
        return repo.purchase_report(session, start, end)
    finally:
        session.close()


def get_stock_report():
    session = SessionLocal()
    try:
        return repo.stock_report(session)
    finally:
        session.close()


def get_customer_report():
    session = SessionLocal()
    try:
        return repo.customer_report(session)
    finally:
        session.close()


def get_supplier_report():
    session = SessionLocal()
    try:
        return repo.supplier_report(session)
    finally:
        session.close()
"""
services/party_service.py

Business logic: duplicate checking + party creation/listing.
UI (party_page.py) sirf inhi functions ko call karega.
"""

from database.database import SessionLocal
from database.repositories import party_repository as repo
from services.audit_service import log_action


def check_duplicate(name: str, mobile: str):
    """Return: list of matching Party objects (khaali list = koi duplicate nahi)."""
    session = SessionLocal()
    try:
        return repo.find_possible_duplicates(session, name, mobile)
    finally:
        session.close()


def add_party(
    name, mobile, party_type,
    father_husband_name="", cnic="", alternate_mobile="",
    address="", city="", opening_balance=0, balance_type="receivable",
    notes="", group_id=None
):
    session = SessionLocal()
    try:
        party = repo.create_party(
            session,
            name=name.strip(),
            mobile=mobile.strip(),
            father_husband_name=father_husband_name.strip(),
            cnic=cnic.strip(),
            alternate_mobile=alternate_mobile.strip(),
            address=address.strip(),
            city=city.strip(),
            is_customer=(party_type == "customer"),
            is_supplier=(party_type == "supplier"),
            opening_balance=opening_balance,
            balance_type=balance_type,
            notes=notes.strip(),
            group_id=group_id,
        )
        return party
    finally:
        session.close()


def get_parties(party_type: str, search_text: str = "", group_id: int = None):
    session = SessionLocal()
    try:
        return repo.list_parties(session, party_type, search_text, group_id)
    finally:
        session.close()

def get_customer_groups():
    session = SessionLocal()
    try:
        return repo.list_customer_groups(session)
    finally:
        session.close()


def add_customer_group(name: str):
    session = SessionLocal()
    try:
        return repo.create_customer_group(session, name)
    finally:
        session.close()

def get_group_wise_summary():
    """
    Har customer group ka: kitne customers hain, total receivable,
    total payable — taake ek nazar mein groups ka hisaab pata chale.
    """
    from database.repositories.ledger_repository import build_ledger

    session = SessionLocal()
    try:
        groups = repo.list_customer_groups(session)
        summary = []

        for group in groups:
            customers = repo.list_customers_by_group(session, group.id)
            total_receivable = 0.0
            total_payable = 0.0
            for c in customers:
                ledger = build_ledger(session, c.id)
                balance = ledger["final_balance"]
                if balance > 0:
                    total_receivable += balance
                elif balance < 0:
                    total_payable += abs(balance)

            summary.append({
                "group_name": group.name,
                "customer_count": len(customers),
                "total_receivable": round(total_receivable, 2),
                "total_payable": round(total_payable, 2),
            })

        # Bina group wale customers bhi ek "غیر گروپ شدہ" row mein
        ungrouped = repo.list_ungrouped_customers(session)
        if ungrouped:
            total_receivable = 0.0
            total_payable = 0.0
            for c in ungrouped:
                ledger = build_ledger(session, c.id)
                balance = ledger["final_balance"]
                if balance > 0:
                    total_receivable += balance
                elif balance < 0:
                    total_payable += abs(balance)

            summary.append({
                "group_name": "غیر گروپ شدہ گاہک",
                "customer_count": len(ungrouped),
                "total_receivable": round(total_receivable, 2),
                "total_payable": round(total_payable, 2),
            })

        return summary
    finally:
        session.close()
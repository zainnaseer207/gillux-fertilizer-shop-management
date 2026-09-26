"""
database/repositories/party_repository.py

Party se related saari database queries yahan hain. Service layer
(party_service.py) isi repository ko call karega — UI kabhi directly
database query nahi likhegi, ye clean architecture principle hai.
"""

from database.models import Party
from database.models import Party, CustomerGroup
from sqlalchemy.orm import joinedload


def generate_next_party_code(session) -> str:
    """Naya party code banata hai: P0001, P0002, ... (existing count par based)."""
    count = session.query(Party).count()
    return f"P{count + 1:04d}"


def find_possible_duplicates(session, name: str, mobile: str):
    """
    Duplicate check: agar mobile number pehle se kisi party ke paas hai,
    ya bilkul same naam maujood hai, to unhe wapas bhejta hai.
    """
    query = session.query(Party)
    matches = []

    if mobile:
        matches += query.filter(Party.mobile == mobile).all()

    if name:
        name_matches = query.filter(Party.name.ilike(name.strip())).all()
        for m in name_matches:
            if m not in matches:
                matches.append(m)

    return matches


def create_party(session, **fields) -> Party:
    fields["party_code"] = generate_next_party_code(session)
    party = Party(**fields)
    session.add(party)
    session.commit()
    session.refresh(party)
    return party


def list_parties(session, party_type: str, search_text: str = "", group_id: int = None):
    query = session.query(Party).options(joinedload(Party.group)).filter(Party.is_active == True)

    if party_type == "customer":
        query = query.filter(Party.is_customer == True)
    elif party_type == "supplier":
        query = query.filter(Party.is_supplier == True)

    if group_id is not None:
        query = query.filter(Party.group_id == group_id)

    if search_text:
        like = f"%{search_text}%"
        query = query.filter(
            (Party.name.ilike(like)) |
            (Party.mobile.ilike(like)) |
            (Party.party_code.ilike(like))
        )

    return query.order_by(Party.name).all()

def list_customer_groups(session):
    return session.query(CustomerGroup).order_by(CustomerGroup.name).all()


def create_customer_group(session, name: str):
    group = CustomerGroup(name=name.strip())
    session.add(group)
    session.commit()
    session.refresh(group)
    return group

def list_customers_by_group(session, group_id):
    return session.query(Party).filter_by(is_customer=True, is_active=True, group_id=group_id).all()


def list_ungrouped_customers(session):
    return session.query(Party).filter_by(is_customer=True, is_active=True, group_id=None).all()
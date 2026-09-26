"""
database/repositories/payment_repository.py
"""

from database.models import Payment


def create_payment(session, party_id, direction, amount, payment_method, reference, notes, user_id):
    payment = Payment(
        party_id=party_id,
        direction=direction,
        amount=amount,
        payment_method=payment_method,
        reference=reference,
        notes=notes,
        user_id=user_id,
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment
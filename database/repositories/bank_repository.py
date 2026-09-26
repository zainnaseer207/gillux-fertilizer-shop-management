"""
database/repositories/bank_repository.py
"""

from database.models import BankAccount, BankTransaction


def create_account(session, name: str, opening_balance: float):
    account = BankAccount(name=name.strip(), opening_balance=opening_balance, is_active=1)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def list_accounts(session):
    return session.query(BankAccount).filter_by(is_active=1).order_by(BankAccount.name).all()


def get_account_balance(session, account_id: int) -> float:
    account = session.query(BankAccount).filter_by(id=account_id).first()
    if account is None:
        return 0.0

    deposits = sum(
        float(t.amount) for t in
        session.query(BankTransaction).filter_by(account_id=account_id, transaction_type="deposit").all()
    )
    withdrawals = sum(
        float(t.amount) for t in
        session.query(BankTransaction).filter_by(account_id=account_id, transaction_type="withdraw").all()
    )
    return float(account.opening_balance or 0) + deposits - withdrawals


def record_transaction(session, account_id, transaction_type, amount, description, user_id):
    if transaction_type == "withdraw":
        current_balance = get_account_balance(session, account_id)
        if current_balance < amount:
            raise ValueError(f"اکاؤنٹ میں اتنی رقم نہیں ہے۔ موجودہ بیلنس: Rs. {current_balance}")

    txn = BankTransaction(
        account_id=account_id, transaction_type=transaction_type,
        amount=amount, description=description, user_id=user_id,
    )
    session.add(txn)
    session.commit()
    return txn


def get_account_transactions(session, account_id):
    return (
        session.query(BankTransaction)
        .filter_by(account_id=account_id)
        .order_by(BankTransaction.created_at.desc())
        .all()
    )


def get_total_bank_balance(session) -> float:
    accounts = list_accounts(session)
    return sum(get_account_balance(session, a.id) for a in accounts)
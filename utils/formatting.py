"""
utils/formatting.py

Paisay ko hamesha ek jaisa, saaf format mein dikhane ke liye —
1000.00 ki jagah sirf 1,000 (whole number + comma).
Poori app mein isi function ko use karna hai jahan bhi "Rs. {x}" likha ho.
"""


def format_money(value) -> str:
    """
    Decimal/float/int koi bhi ho, ye hamesha whole-number + comma
    formatted string deta hai. Example: 1000.00 -> "1,000"
    """
    try:
        return f"{int(round(float(value))):,}"
    except (TypeError, ValueError):
        return "0"


def rs(value) -> str:
    """Shortcut: 'Rs. 1,000' jaisa poora string deta hai."""
    return f"Rs. {format_money(value)}"
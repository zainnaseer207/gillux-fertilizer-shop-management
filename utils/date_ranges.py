"""
utils/date_ranges.py

Reports mein baar baar date-range calculate karna padega
(Today/Yesterday/This Week/This Month/Custom) — isliye ek hi
jagah se ye logic milega, Phase 16 (Reports) mein bhi reuse hoga.
"""

from datetime import datetime, time, timedelta


def get_range(filter_name: str, custom_from=None, custom_to=None):
    """
    filter_name: "today", "yesterday", "this_week", "this_month", "custom"
    Return: (start_datetime, end_datetime)
    """
    today = datetime.utcnow().date()

    if filter_name == "today":
        start_date = end_date = today
    elif filter_name == "yesterday":
        start_date = end_date = today - timedelta(days=1)
    elif filter_name == "this_week":
        start_date = today - timedelta(days=today.weekday())  # Monday
        end_date = today
    elif filter_name == "this_month":
        start_date = today.replace(day=1)
        end_date = today
    elif filter_name == "custom":
        start_date = custom_from
        end_date = custom_to
    else:
        start_date = end_date = today

    start = datetime.combine(start_date, time.min)
    end = datetime.combine(end_date, time.max)
    return start, end
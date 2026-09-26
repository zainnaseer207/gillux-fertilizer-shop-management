"""
utils/translations.py

GILLUX ki poori Urdu translation dictionary — ek hi jagah se sab
labels milte hain. Naya label chahiye ho to yahan add karein,
phir UI files mein t("Key") se use karein.
"""

UR = {
    # ---- App Branding ----
    "GILLUX": "گلکس",
    "Fertilizer Shop Management System": "کھاد کی دکان کا نظام",

    # ---- Sidebar ----
    "Dashboard": "ڈیش بورڈ",
    "Stock": "اسٹاک",
    "Khaata": "کھاتہ",
    "Sales & Accounts": "فروخت اور حساب",
    "Reports": "رپورٹس",
    "Settings": "ترتیبات",
    "Logout": "لاگ آؤٹ",

    # ---- Common Actions ----
    "Add": "شامل کریں",
    "Save": "محفوظ کریں",
    "Cancel": "منسوخ کریں",
    "Delete": "حذف کریں",
    "Edit": "ترمیم کریں",
    "Search": "تلاش کریں",
    "Print": "پرنٹ کریں",
    "Export": "ایکسپورٹ کریں",
    "Close": "بند کریں",

    # ---- Khaata / Ledger (register jaisa) ----
    "Date": "تاریخ",
    "Description": "تفصیل",
    "Page": "صفحہ",
    "Name": "نام",
    "Credit": "جمع",
    "Debit": "نکاس",
    "Balance": "بقایا",
    "Reference": "حوالہ",
    "Opening Balance": "پرانا بقایا",
    "Customer Khaata": "گاہک کھاتہ",
    "Supplier Khaata": "سپلائر کھاتہ",
    "Receive Payment": "ادائیگی وصول کریں",
    "Pay Supplier": "سپلائر کو ادا کریں",
    "Current Balance": "موجودہ بقایا",
    "Receivable": "وصولی باقی",
    "Payable": "ادائیگی باقی",

    # ---- Stock Register ----
    "Item Name": "نام اشیاء",
    "Incoming": "آمد",
    "Outgoing": "نکاس",
    "Quantity": "تعداد",
    "Stock Register": "اسٹاک رجسٹر",
    "Available Stock": "دستیاب اسٹاک",

    # ---- Sales/Purchase ----
    "Customer": "گاہک",
    "Supplier": "سپلائر",
    "Product": "چیز",
    "Rate": "قیمت",
    "Amount": "رقم",
    "Total": "کل رقم",
    "Discount": "رعایت",
    "Paid": "ادا شدہ",
    "Remaining": "باقی",
    "Cash": "نقد",
    "Credit Sale": "ادھار",

    # ---- Accounts ----
    "Cash in Hand": "ہاتھ میں نقدی",
    "Bank": "بینک",
    "Expenses": "اخراجات",
    "Cash Book": "کیش بک",

    # ---- Messages ----
    "Already Exists": "پہلے سے موجود ہے",
    "Success": "کامیابی",
    "Error": "خرابی",
    "Required": "ضروری ہے",
}


def t(key: str) -> str:
    """
    Translation helper — agar Urdu mojood hai to wo deta hai,
    warna original English key hi wapas kar deta hai (safe fallback).
    """
    return UR.get(key, key)
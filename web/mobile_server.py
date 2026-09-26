"""
web/mobile_server.py

Ek halka Flask web server jo GILLUX ki wahi database parhta hai
(koi separate data nahi) — sirf DEKHNE ke liye (Dashboard/Stock/Khaata).
Mobile browser se local WiFi network par khola ja sakta hai.

Ye poori tarah "read-only" hai — koi add/edit yahan se nahi hota.
"""

import socket
import threading

from flask import Flask, request

from services.dashboard_service import get_dashboard_summary
from services.product_service import get_products
from services.party_service import get_parties
from services.ledger_service import get_party_ledger
from utils.formatting import format_money

app = Flask(__name__)

_mobile_url = None  # server start hone ke baad yahan URL store hota hai


BASE_STYLE = """
<style>
    * { box-sizing: border-box; }
    body {
        font-family: -apple-system, "Segoe UI", Tahoma, sans-serif;
        background: #F5F5F5; margin: 0; padding: 0; color: #212121;
    }
    .header {
        background: #1B5E20; color: white; padding: 16px;
        text-align: center;
    }
    .header h1 { margin: 0; font-size: 18px; }
    .header p { margin: 4px 0 0; font-size: 12px; color: #C8E6C9; }
    .nav {
        display: flex; background: #2E7D32; overflow-x: auto;
    }
    .nav a {
        color: white; text-decoration: none; padding: 12px 16px;
        font-size: 13px; white-space: nowrap; flex: 1; text-align: center;
    }
    .nav a:hover, .nav a.active { background: #1B5E20; font-weight: bold; }
    .content { padding: 16px; }
    .card {
        background: white; border-radius: 8px; padding: 14px;
        margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .card-title { font-size: 12px; color: #757575; margin-bottom: 4px; }
    .card-value { font-size: 22px; font-weight: bold; color: #1B5E20; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
    th { background: #1B5E20; color: white; padding: 8px; font-size: 12px; text-align: left; }
    td { padding: 8px; font-size: 13px; border-bottom: 1px solid #eee; }
    tr:nth-child(even) { background: #FAFAFA; }
    input[type=text] {
        width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px;
        margin-bottom: 10px; font-size: 14px;
    }
    .badge { background: #E8F5E9; color: #1B5E20; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
    .empty { text-align: center; color: #999; padding: 30px; }
</style>
"""


def _page(title: str, active: str, body: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — GILLUX</title>
    {BASE_STYLE}
</head>
<body>
    <div class="header">
        <h1>Liaqat Gill &amp; Commission Shop</h1>
        <p>GILLUX — Mobile View (Read Only)</p>
    </div>
    <div class="nav">
        <a href="/" class="{'active' if active=='dashboard' else ''}">Dashboard</a>
        <a href="/stock" class="{'active' if active=='stock' else ''}">Stock</a>
        <a href="/khaata/customer" class="{'active' if active=='customer' else ''}">Customers</a>
        <a href="/khaata/supplier" class="{'active' if active=='supplier' else ''}">Suppliers</a>
    </div>
    <div class="content">
        {body}
    </div>
</body>
</html>
"""


@app.route("/")
def dashboard():
    summary = get_dashboard_summary()
    cards = [
        ("Today's Sales", summary["today_sales"]),
        ("Today's Purchases", summary["today_purchases"]),
        ("Cash in Hand", summary["cash_in_hand"]),
        ("Total Receivable", summary["total_receivable"]),
        ("Total Payable", summary["total_payable"]),
        ("Stock Value", summary["stock_value"]),
        ("Today's Profit", summary["today_profit"]),
    ]
    body = "".join(
        f'<div class="card"><div class="card-title">{title}</div>'
        f'<div class="card-value">Rs. {format_money(value)}</div></div>'
        for title, value in cards
    )
    body += (
        f'<div class="card"><div class="card-title">Current Stock Items</div>'
        f'<div class="card-value">{summary["stock_items"]}</div></div>'
    )
    return _page("Dashboard", "dashboard", body)


@app.route("/stock")
def stock():
    search = request.args.get("q", "")
    products = get_products(search)

    rows = "".join(
        f"<tr><td>{p.product_code}</td><td>{p.name}</td>"
        f"<td>{p.unit.name if p.unit else ''}</td>"
        f"<td>{p.current_stock}</td>"
        f"<td>Rs. {format_money(p.sale_price)}</td></tr>"
        for p in products
    )
    if not rows:
        table = '<div class="empty">Koi product nahi mila۔</div>'
    else:
        table = f"""
        <table>
            <tr><th>Code</th><th>Name</th><th>Unit</th><th>Stock</th><th>Sale Price</th></tr>
            {rows}
        </table>
        """

    body = f"""
        <form method="get">
            <input type="text" name="q" placeholder="Search product..." value="{search}">
        </form>
        {table}
    """
    return _page("Stock", "stock", body)


@app.route("/khaata/<party_type>")
def khaata_list(party_type):
    if party_type not in ("customer", "supplier"):
        party_type = "customer"

    search = request.args.get("q", "")
    parties = get_parties(party_type, search)

    rows = "".join(
        f'<tr><td>{p.party_code}</td><td>{p.name}</td><td>{p.mobile or ""}</td>'
        f'<td><a href="/khaata/{party_type}/{p.id}" class="badge">View Ledger</a></td></tr>'
        for p in parties
    )
    if not rows:
        table = '<div class="empty">Koi party nahi mili۔</div>'
    else:
        table = f"""
        <table>
            <tr><th>Code</th><th>Name</th><th>Mobile</th><th></th></tr>
            {rows}
        </table>
        """

    body = f"""
        <form method="get">
            <input type="text" name="q" placeholder="Search..." value="{search}">
        </form>
        {table}
    """
    return _page("Khaata", party_type, body)


@app.route("/khaata/<party_type>/<int:party_id>")
def khaata_detail(party_type, party_id):
    ledger = get_party_ledger(party_id)
    party = ledger["party"]
    balance = ledger["final_balance"]
    note = "Receivable" if balance >= 0 else "Payable"

    rows = "".join(
        f"<tr><td>{r['date'].strftime('%Y-%m-%d') if r['date'] else '—'}</td>"
        f"<td>{r['description']}</td>"
        f"<td>{format_money(r['debit']) if r['debit'] else ''}</td>"
        f"<td>{format_money(r['credit']) if r['credit'] else ''}</td>"
        f"<td>{format_money(r['balance'])}</td></tr>"
        for r in ledger["rows"]
    )

    body = f"""
        <div class="card">
            <div class="card-title">{party.name} ({party.party_code})</div>
            <div class="card-value">Rs. {format_money(abs(balance))} — {note}</div>
        </div>
        <table>
            <tr><th>Date</th><th>Description</th><th>Debit</th><th>Credit</th><th>Balance</th></tr>
            {rows}
        </table>
        <p style="margin-top:16px;"><a href="/khaata/{party_type}">&larr; Back to list</a></p>
    """
    return _page(party.name, party_type, body)


def _get_lan_ip() -> str:
    """LAN IP address nikalta hai (jo mobile se accessible ho, 127.0.0.1 nahi)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def start_mobile_server(port: int = 5000):
    """
    Flask server ko background thread mein start karta hai — taake
    GILLUX ki main desktop app (PySide6) normally chalti rahe.

    Return: mobile se access karne ka URL (e.g. http://192.168.1.5:5000)
    """
    global _mobile_url
    ip = _get_lan_ip()
    _mobile_url = f"http://{ip}:{port}"

    def run_server():
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    return _mobile_url


def get_mobile_url() -> str:
    return _mobile_url or "Server abhi start nahi hua"
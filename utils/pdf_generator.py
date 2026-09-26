"""
utils/pdf_generator.py

Invoice PDF banata hai — Sale ya Purchase dono ke liye reusable
function. Header ek colored band hai: bara shop name, phone number,
aur address — professional commercial invoice jaisa look.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from services.settings_service import get_shop_settings
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Windows ke system fonts jo Urdu/Arabic script support karte hain
_URDU_FONT_CANDIDATES = [
    ("Tahoma", r"C:\Windows\Fonts\tahoma.ttf"),
    ("Tahoma-Bold", r"C:\Windows\Fonts\tahomabd.ttf"),
    ("SegoeUI", r"C:\Windows\Fonts\segoeui.ttf"),
    ("SegoeUI-Bold", r"C:\Windows\Fonts\segoeuib.ttf"),
    ("JameelNoori", r"C:\Windows\Fonts\JameelNooriNastaleeqRegular.ttf"),
    ("JameelNoori", r"C:\Windows\Fonts\Jameel Noori Nastaleeq Regular.ttf"),
    ("JameelNoori", r"C:\Windows\Fonts\JameelNooriNastaleeq.ttf"),
    ("JameelNoori", r"C:\Windows\Fonts\Jameel Noori Nastaleeq.ttf"),
    ("JameelNoori-Kasheeda", r"C:\Windows\Fonts\Jameel Noori Nastaleeq Kasheeda.ttf"),
    # Fallback agar upar wale na milein
    ("Tahoma", r"C:\Windows\Fonts\tahoma.ttf"),
    ("Tahoma-Bold", r"C:\Windows\Fonts\tahomabd.ttf"),
]

URDU_FONT_NAME = "Helvetica"       # agar koi Urdu font na mile to fallback
URDU_FONT_BOLD = "Helvetica-Bold"

for font_name, font_path in _URDU_FONT_CANDIDATES:
    if os.path.exists(font_path) and font_name not in pdfmetrics.getRegisteredFontNames():
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            URDU_FONT_NAME = font_name
            URDU_FONT_BOLD = font_name  # Jameel Noori mein alag bold file na ho to same use hoga
        except Exception:
            pass

GREEN = colors.HexColor("#1B5E20")
LIGHT_GREEN = colors.HexColor("#E8F5E9")


def generate_invoice_pdf(invoice_type: str, invoice, items, output_path: str):
    """
    invoice_type: "sale" ya "purchase"
    invoice: Sale ya Purchase object
    items: list of SaleItem/PurchaseItem objects
    output_path: kahan save karni hai PDF
    """
    shop = get_shop_settings()
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=0, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm,
    )
    elements = []

    # ---- HEADER: Bara colored band shop name/phone/address ke saath ----
    shop_name_style = ParagraphStyle(
        "ShopName", parent=styles["Title"], fontSize=26, leading=30,
        alignment=TA_CENTER, textColor=colors.white, fontName=URDU_FONT_BOLD,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontSize=10.5,
        alignment=TA_CENTER, textColor=colors.white, fontName=URDU_FONT_NAME,
    )
    contact_style = ParagraphStyle(
        "Contact", parent=styles["Normal"], fontSize=11,
        alignment=TA_CENTER, textColor=colors.white, fontName=URDU_FONT_BOLD,
    )

    header_content = [
        [Paragraph(shop.get("shop_name", "").upper(), shop_name_style)],
        [Paragraph("Fertilizer Shop Management System — GILLUX", subtitle_style)],
        [Spacer(1, 6)],
        [Paragraph(
            f"&#9742; {shop.get('shop_phone', '')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"&#128205; {shop.get('shop_address', '')}",
            contact_style
        )],
    ]

    header_table = Table(header_content, colWidths=[170*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("TOPPADDING", (0, 0), (0, 0), 22),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, -1), (0, -1), 4),
        ("BOTTOMPADDING", (0, -1), (0, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)

    # Thin accent line neeche
    line_table = Table([[""]], colWidths=[170*mm], rowHeights=[3])
    line_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0D3D11"))]))
    elements.append(line_table)

    elements.append(Spacer(1, 20))

    # ---- Invoice Meta ----
    if invoice_type == "sale":
        number_label, number_value = "Invoice #", invoice.invoice_number
        party_label, party = "Customer", invoice.customer
        date_value = invoice.sale_date
    else:
        number_label, number_value = "Purchase #", invoice.purchase_number
        party_label, party = "Supplier", invoice.supplier
        date_value = invoice.purchase_date

    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=10.5)
    meta_table_data = [
        [Paragraph(f"<b>{number_label}:</b> {number_value}", meta_style),
         Paragraph(f"<b>Date:</b> {date_value.strftime('%Y-%m-%d')}", meta_style)],
        [Paragraph(f"<b>{party_label}:</b> {party.name if party else ''}", meta_style),
         Paragraph(f"<b>Mobile:</b> {party.mobile if party else ''}", meta_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[85*mm, 85*mm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 16))

    # ---- Items Table ----
    table_data = [["Sr.", "Product", "Qty", "Rate", "Amount"]]
    for i, item in enumerate(items, start=1):
        table_data.append([
            str(i), item.product.name if item.product else "",
            str(item.quantity), f"Rs. {item.rate}", f"Rs. {item.amount}",
        ])

    items_table = Table(table_data, colWidths=[20*mm, 70*mm, 25*mm, 27*mm, 28*mm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 14))

    # ---- Totals ----
    totals_data = [
        ["Subtotal:", f"Rs. {invoice.subtotal}"],
        ["Discount:", f"Rs. {invoice.discount}"],
        ["Grand Total:", f"Rs. {invoice.total}"],
        ["Paid:", f"Rs. {invoice.paid_amount}"],
        ["Balance:", f"Rs. {invoice.remaining_amount}"],
        ["Payment Method:", invoice.payment_method],
    ]
    totals_table = Table(totals_data, colWidths=[120*mm, 50*mm])
    totals_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), URDU_FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), URDU_FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))

    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], alignment=TA_CENTER,
        textColor=colors.grey, fontSize=9,
    )
    elements.append(Paragraph("Shukriya! Dobara tashreef laayein.", footer_style))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.build(elements)
    return output_path

def generate_report_pdf(title: str, headers: list, rows: list, summary_text: str, output_path: str):
    """
    Kisi bhi report (Sales, Purchase, Stock, Customer, Supplier) ke liye
    generic, branded PDF banata hai — invoice jaisa hi green header
    band, shop name/phone/address ke saath.

    headers: ["کالم 1", "کالم 2", ...]
    rows: [["val1", "val2", ...], ...]
    summary_text: report ke upar ek line summary (optional, khaali "" bhi chal sakta hai)
    """
    shop = get_shop_settings()
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=0, bottomMargin=20*mm, leftMargin=15*mm, rightMargin=15*mm,
    )
    elements = []

    # ---- HEADER: wahi green band jo invoice mein hai ----
    shop_name_style = ParagraphStyle(
        "ShopName", parent=styles["Title"], fontSize=22, leading=26,
        alignment=TA_CENTER, textColor=colors.white, fontName=URDU_FONT_BOLD,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontSize=10,
        alignment=TA_CENTER, textColor=colors.white,
    )
    contact_style = ParagraphStyle(
        "Contact", parent=styles["Normal"], fontSize=10,
        alignment=TA_CENTER, textColor=colors.white, fontName=URDU_FONT_BOLD,
    )

    header_content = [
        [Paragraph(shop.get("shop_name", "").upper(), shop_name_style)],
        [Paragraph("Fertilizer Shop Management System — GILLUX", subtitle_style)],
        [Spacer(1, 6)],
        [Paragraph(
            f"&#9742; {shop.get('shop_phone', '')} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"&#128205; {shop.get('shop_address', '')}",
            contact_style
        )],
    ]

    header_table = Table(header_content, colWidths=[180*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("TOPPADDING", (0, 0), (0, 0), 18),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, -1), (0, -1), 4),
        ("BOTTOMPADDING", (0, -1), (0, -1), 16),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)

    line_table = Table([[""]], colWidths=[180*mm], rowHeights=[3])
    line_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0D3D11"))]))
    elements.append(line_table)

    elements.append(Spacer(1, 16))

    # ---- Report Title ----
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Heading1"], fontSize=15,
        alignment=TA_CENTER, textColor=GREEN,
    )
    elements.append(Paragraph(title, title_style))

    date_style = ParagraphStyle(
        "DateStamp", parent=styles["Normal"], fontSize=9,
        alignment=TA_CENTER, textColor=colors.grey,
    )
    from datetime import datetime
    elements.append(Paragraph(f"تیار کردہ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
    elements.append(Spacer(1, 10))

    # ---- Summary line (agar di gayi ho) ----
    if summary_text:
        summary_style = ParagraphStyle(
            "Summary", parent=styles["Normal"], fontSize=10.5,
            alignment=TA_CENTER, textColor=GREEN, fontName=URDU_FONT_BOLD,
        )
        elements.append(Paragraph(summary_text, summary_style))
        elements.append(Spacer(1, 12))

    # ---- Data Table ----
    table_data = [headers] + rows
    col_count = len(headers)
    available_width = 180 * mm
    col_width = available_width / col_count

    data_table = Table(table_data, colWidths=[col_width] * col_count, repeatRows=1)
    data_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), URDU_FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), URDU_FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(data_table)
    elements.append(Spacer(1, 24))

    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], alignment=TA_CENTER,
        textColor=colors.grey, fontSize=8.5,
    )
    elements.append(Paragraph("Liaqat Gill & Commission Shop — GILLUX Software", footer_style))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.build(elements)
    return output_path
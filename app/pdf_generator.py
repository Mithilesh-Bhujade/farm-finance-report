# app/pdf_generator.py
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime
from pathlib import Path
from reportlab.lib.utils import ImageReader

from app.chart import generate_chart

DEFAULT_FOOTER = "Proudly maintained accounting with GramIQ"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=1))

# Project static folder
STATIC = Path(__file__).resolve().parent.parent / "static"
STATIC.mkdir(parents=True, exist_ok=True)

# Acceptable logo filenames
LOGO_CANDIDATES = [STATIC / "gramiq_logo.png", STATIC / "logo.png"]

def _get_logo_path():
    for p in LOGO_CANDIDATES:
        if p.exists():
            return str(p)
    return None

def _format_iso_to_ddmm(date_str: str) -> str:
    """
    Convert ISO 'YYYY-MM-DD' to 'DD-MM-YYYY'. If parsing fails,
    try common dd-mm-yyyy input, otherwise return the original string.
    """
    if not date_str:
        return ""
    # Try ISO first
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        pass
    # Try dd-mm-yyyy already formatted
    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        pass
    # fallback: return as-is
    return date_str

def _parse_for_sort(date_str: str):
    """
    Return a datetime for sorting if possible, else return the
    original string to allow stable sorting fallback.
    """
    if not date_str:
        return date_str
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        pass
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except Exception:
        pass
    return date_str

def _format_acres_value(acres_value):
    """
    Accepts numeric or string input. Returns:
      - '2' for 2.0
      - '2.5' for 2.5
      - original string for non-numeric inputs
    """
    try:
        fv = float(acres_value)
        if fv.is_integer():
            return str(int(fv))
        s = format(fv, 'f').rstrip('0').rstrip('.')
        return s
    except Exception:
        return str(acres_value).strip()

def _header_footer(canvas_obj, doc):
    """
    Draw header on every page:
      - Logo (left)
      - Title (center): crop_acres_season_year (uses cleaned acres string)
      - Timestamp (right)
    Footer centered.
    """
    canvas_obj.saveState()
    width, height = A4

    # Top positions
    HEADER_TOP_Y = height - 10 * mm     # top-most y reference
    HEADER_LINE_Y = HEADER_TOP_Y - 6    # main header line (logo/title/timestamp)
    FOOTER_Y = 12 * mm

    # Draw logo left
    logo_path = _get_logo_path()
    if logo_path:
        try:
            img = ImageReader(logo_path)
            max_logo_w = 30 * mm
            max_logo_h = 12 * mm
            iw, ih = img.getSize()
            ratio = min(max_logo_w / iw, max_logo_h / ih, 1.0)
            draw_w = iw * ratio
            draw_h = ih * ratio
            canvas_obj.drawImage(img, 20 * mm, HEADER_LINE_Y - draw_h / 2, width=draw_w, height=draw_h, mask="auto")
        except Exception:
            pass

    # Build title
    title = getattr(doc, "report_title", None)
    if not title and getattr(doc, "data", None):
        d = doc.data
        acres_str = _format_acres_value(getattr(d, "total_acres", ""))
        title = f"{getattr(d, 'crop_name', '')}_{acres_str}_{getattr(d, 'season','')}_{datetime.now().year}"
    if not title:
        title = ""

    # Centered title (main)
    canvas_obj.setFont("Helvetica-Bold", 12)
    canvas_obj.drawCentredString(width / 2.0, HEADER_LINE_Y, title)

    # Timestamp on right
    canvas_obj.setFont("Helvetica", 9)
    ts = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    canvas_obj.drawRightString(width - 20 * mm, HEADER_LINE_Y, f"Generated: {ts}")

    # Footer centered
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawCentredString(width / 2.0, FOOTER_Y, DEFAULT_FOOTER)

    canvas_obj.restoreState()



def _apply_alternate_shading(table_style, rows_count, start_row=1, cols_from=0, cols_to=-1):
    """
    Add background shading to every other data row (i.e., rows 1..end).
    table_style is a list to which we append ('BACKGROUND', (col0,rowN), (colN,rowN), color).
    rows_count: total number of table rows (including header)
    start_row: usually 1 (first data row)
    cols_from/cols_to: column range to shade
    """
    shade = colors.whitesmoke
    for r in range(start_row, rows_count):
        if (r - start_row) % 2 == 1:
            table_style.append(('BACKGROUND', (cols_from, r), (cols_to, r), shade))

def generate_pdf(data, output_path: str):
    """
    Build and write a PDF report for the given FarmerData.
    Returns the path to the generated PDF (same as output_path).
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=40 * mm,
        bottomMargin=20 * mm,
    )

    # Create user-friendly title and set metadata + attach data for header access
    acres_str = _format_acres_value(getattr(data, "total_acres", ""))
    title = f"{data.crop_name}_{acres_str}_{data.season}_{datetime.now().year}"

    # metadata for PDF viewer (prevents "(anonymous)")
    doc.title = title
    doc.author = "GramIQ"
    doc.subject = "Farm Finance Report"
    doc.keywords = "GramIQ, Farm Report, Finance, Agriculture"

    # value used by your header function (and kept separate in case you use doc.report_title elsewhere)
    doc.report_title = title

    # attach the data object so header/footer callback can access fields (farmer_name etc.)
    doc.data = data

    story = []

    story.append(Spacer(1, 4))
    story.append(Paragraph(title, styles['Title']))
    story.append(Paragraph(f"Farmer: {data.farmer_name}", styles['Normal']))
    story.append(Paragraph(f"Location: {data.location}", styles['Normal']))
    story.append(Spacer(1, 8))

    # Finance summary calculations
    total_income = sum(i.amount for i in data.incomes) if data.incomes else 0.0
    total_expense = sum(e.amount for e in data.expenses) if data.expenses else 0.0
    profit = total_income - total_expense
    cost_per_acre = (total_expense / data.total_acres) if data.total_acres else 0.0

    # Format production if present
    if getattr(data, "total_production", None) is not None:
        prod_display = f"{data.total_production:,.2f}"
    else:
        prod_display = ""

    summary_table = [
        ["Total Income", f"{total_income:,.2f}"],
        ["Total Expense", f"{total_expense:,.2f}"],
        ["Total Production", prod_display],
        ["Profit or Loss", f"{profit:,.2f}"],
        ["Cost of cultivation per acre", f"{cost_per_acre:,.2f}"],
    ]
    t = Table(summary_table, colWidths=[120 * mm, 40 * mm])

    # SUMMARY STYLE: first row shaded (whitesmoke), labels left, numbers right, no bold
    summary_style = [
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]

    t.setStyle(TableStyle(summary_style))
    story.append(t)
    story.append(Spacer(1, 12))

    # Generate and add chart image (bigger and with heading)
    chart_path = generate_chart(total_income, total_expense)
    if chart_path:
        story.append(Spacer(1, 40))
        story.append(Paragraph("<b>Income vs Expense Chart</b>", styles['Heading2']))
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 30))
        story.append(Image(str(chart_path), width=320, height=180))
        story.append(Spacer(1, 12))

    story.append(PageBreak())

    # Expense table
    story.append(Paragraph("<b>Expense Breakdown</b>", styles['Heading2']))
    exp_rows = [["Category", "Amount", "Date", "Description"]]
    for e in data.expenses:
        exp_rows.append([str(e.category), f"{float(e.amount):,.2f}", _format_iso_to_ddmm(str(e.date)), str(e.description or "")])
    et = Table(exp_rows, colWidths=[60 * mm, 30 * mm, 35 * mm, 45 * mm])

    et_style = [
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        # Blue header with white bold text
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4A90E2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]
    _apply_alternate_shading(et_style, rows_count=len(exp_rows), start_row=1, cols_from=0, cols_to=-1)
    et.setStyle(TableStyle(et_style))
    story.append(et)
    story.append(Spacer(1, 12))

    # Income table
    story.append(Paragraph("<b>Income Breakdown</b>", styles['Heading2']))
    inc_rows = [["Category", "Amount", "Date", "Description"]]
    for i in data.incomes:
        inc_rows.append([str(i.category), f"{float(i.amount):,.2f}", _format_iso_to_ddmm(str(i.date)), str(i.description or "")])
    it = Table(inc_rows, colWidths=[60 * mm, 30 * mm, 35 * mm, 45 * mm])

    it_style = [
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4A90E2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]
    _apply_alternate_shading(it_style, rows_count=len(inc_rows), start_row=1, cols_from=0, cols_to=-1)
    it.setStyle(TableStyle(it_style))
    story.append(it)
    story.append(Spacer(1, 12))

    # Ledger (merged, sorted by date)
    story.append(Paragraph("<b>Ledger</b>", styles['Heading2']))
    ledger_rows = [["Date", "Particulars", "Type", "Description", "Amount"]]
    merged = []
    for e in data.expenses:
        merged.append((str(e.date), str(e.category), "Expense", str(e.description or ""), float(e.amount)))
    for i in data.incomes:
        merged.append((str(i.date), str(i.category), "Income", str(i.description or ""), float(i.amount)))

    merged_sorted = sorted(merged, key=lambda x: _parse_for_sort(x[0]))
    for row in merged_sorted:
        ledger_rows.append([_format_iso_to_ddmm(row[0]), row[1], row[2], row[3], f"{row[4]:,.2f}"])

    lg = Table(ledger_rows, colWidths=[30 * mm, 55 * mm, 30 * mm, 45 * mm, 25 * mm])

    lg_style = [
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4A90E2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]
    _apply_alternate_shading(lg_style, rows_count=len(ledger_rows), start_row=1, cols_from=0, cols_to=-1)
    lg.setStyle(TableStyle(lg_style))
    story.append(lg)

    # Build PDF with header/footer callback that draws logo/title/footer
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return output_path

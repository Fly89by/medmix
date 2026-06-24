from datetime import datetime
from fpdf import FPDF
from fpdf.enums import TableCellFillMode


def generate_quote_pdf(quote) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("DejaVu", "B", 20)
    pdf.set_text_color(26, 86, 219)
    pdf.cell(0, 12, "MED.MIX", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Al Madinah Ready Mix - Quote", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(50, 50, 50)
    fields = [
        ("Quote #", quote.quote_number),
        ("Date", datetime.now().strftime("%Y-%m-%d %H:%M")),
        ("Customer", quote.customer_name),
    ]
    if quote.customer_phone:
        fields.append(("Phone", quote.customer_phone))
    if quote.city:
        fields.append(("City", quote.city))
    fields.append(("Status", quote.status))

    for label, value in fields:
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(30, 7, label + ":")
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    col_w = [120, 30, 30]
    headers = ["Product", "Qty", "Unit Price"]

    pdf.set_fill_color(26, 86, 219)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 10)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 10, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_fill_color(245, 247, 250)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("DejaVu", "", 10)
    row = [quote.product, f"{quote.quantity:.0f}", f"{quote.unit_price:.2f} SAR"]
    fill = False
    for i, val in enumerate(row):
        pdf.cell(col_w[i], 10, val, border=1, fill=fill, align="C")
    pdf.ln()

    pdf.ln(3)
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(26, 86, 219)
    pdf.cell(0, 10, f"Total: {quote.total_price:,.2f} SAR", new_x="LMARGIN", new_y="NEXT", align="R")

    if quote.notes:
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, "Notes:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 7, quote.notes)

    pdf.set_y(-30)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "MED.MIX - Al Madinah Ready Mix  |  This is a computer-generated quote.", new_x="LMARGIN", new_y="NEXT", align="C")

    return bytes(pdf.output())

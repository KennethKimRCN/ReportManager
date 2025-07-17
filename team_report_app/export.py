from docx import Document
from models import Update
import os

def generate_word():
    doc = Document()
    doc.add_heading('Weekly Team Report', 0)
    updates = Update.query.all()

    for u in updates:
        doc.add_heading(f"{u.name} - {u.project}", level=1)
        doc.add_paragraph(u.update)

    path = 'reports/weekly_report.docx'
    os.makedirs('reports', exist_ok=True)
    doc.save(path)
    return path

def generate_pdf():
    from reportlab.pdfgen import canvas
    updates = Update.query.all()
    path = 'reports/weekly_report.pdf'
    os.makedirs('reports', exist_ok=True)
    c = canvas.Canvas(path)
    y = 800
    for u in updates:
        c.drawString(50, y, f"{u.name} - {u.project}")
        y -= 20
        for line in u.update.splitlines():
            c.drawString(60, y, line)
            y -= 15
        y -= 20
    c.save()
    return path

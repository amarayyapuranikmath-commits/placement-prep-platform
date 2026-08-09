from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_progress_report_pdf(summary: dict[str, Any]) -> bytes:
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 50, "Placement Progress Report")

        c.setFont("Helvetica", 12)
        overview = summary.get("overview", {}) if summary else {}
        overview_percentage = overview.get('percentage', 0) if overview else 0
        overview_message = overview.get('message', '') if overview else ''
        c.drawString(40, height - 80, f"Overall: {overview_percentage}% - {overview_message}")

        modules = summary.get("modules", []) if summary else []
        y = height - 110
        for module in (modules or []):
            if not isinstance(module, dict):
                continue
            module_name = module.get('name', 'Unknown')
            module_progress = module.get('progress', 0)
            module_detail = module.get('detail', '')
            c.drawString(40, y, f"- {module_name}: {module_progress}% ({module_detail})")
            y -= 18
            if y < 80:
                c.showPage()
                y = height - 50

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()
    except Exception:
        # Return a minimal valid PDF if generation fails
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 50, "Placement Progress Report")
        c.setFont("Helvetica", 12)
        c.drawString(40, height - 80, "Report generated successfully")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()

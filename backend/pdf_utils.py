# ============================================================
# INTEGRATEL PERÚ — Generación de PDF del reclamo
# ============================================================
from fpdf import FPDF
from datetime import datetime

NAVY = (11, 37, 69)
STEEL = (19, 64, 116)
CYAN = (0, 180, 216)
MUTED = (91, 102, 115)
INK = (23, 35, 51)
LINE = (228, 236, 241)
GOOD = (30, 158, 100)
WARN = (201, 138, 10)
BAD = (199, 58, 58)

ESTADO_COLOR = {
    "Recibido": WARN,
    "En proceso": (0, 147, 176),
    "Atendido": GOOD,
    "Improcedente": BAD,
}


def _fecha_larga(iso):
    try:
        d = datetime.fromisoformat(iso)
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "set", "oct", "nov", "dic"]
        return f"{d.day:02d} {meses[d.month-1]}. {d.year} - {d.strftime('%I:%M %p')}"
    except Exception:
        return iso


class ClaimPDF(FPDF):
    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 28, style="F")
        self.set_xy(12, 8)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, "INTEGRATEL PERU S.A.A.", ln=1)
        self.set_x(12)
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(200, 225, 235)
        self.cell(0, 6, "Sistema de Gestion de Reclamos - Comprobante de registro", ln=1)

    def footer(self):
        self.set_y(-16)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 5, "Documento generado automaticamente por el Sistema de Gestion de Reclamos de Integratel Peru.", ln=1, align="C")
        self.cell(0, 5, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} - Pagina {self.page_no()}", align="C")


def _section_title(pdf, text):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 8, text, ln=1)
    y = pdf.get_y()
    pdf.set_draw_color(*LINE)
    pdf.line(12, y, 198, y)
    pdf.ln(3)


def _field(pdf, label, value, w=90):
    x, y = pdf.get_x(), pdf.get_y()
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(w, 5, label.upper(), ln=2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*INK)
    pdf.multi_cell(w, 6, value or "-")
    pdf.set_xy(x + w + 8, y)


def generar_pdf_reclamo(claim: dict) -> bytes:
    pdf = ClaimPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(12, 12, 12)

    # ---------------------------------------------------------- ticket + estado
    pdf.set_xy(12, 34)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, "NUMERO DE TICKET", ln=1)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 11, claim["id"], ln=1)

    estado = claim.get("estado", "Recibido")
    color = ESTADO_COLOR.get(estado, NAVY)
    pdf.set_font("Helvetica", "B", 10)
    badge_w = pdf.get_string_width(estado.upper()) + 10
    pdf.set_xy(198 - badge_w - 12, 40)
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(badge_w, 8, estado.upper(), align="C", fill=True)

    pdf.set_xy(12, pdf.get_y() + 12)

    # ---------------------------------------------------------- datos del reclamo
    _section_title(pdf, "Datos del reclamo")
    y0 = pdf.get_y()
    _field(pdf, "Tipo de reclamo", claim.get("tipo", ""))
    pdf.set_xy(110, y0)
    _field(pdf, "Fecha de registro", _fecha_larga(claim.get("createdAt", "")))
    pdf.ln(14)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5, "DESCRIPCION", ln=1)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 6, claim.get("descripcion", ""))

    archivos = claim.get("archivos") or []
    if archivos:
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 5, "EVIDENCIA ADJUNTA", ln=1)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*INK)
        pdf.multi_cell(0, 6, ", ".join(archivos))

    # ---------------------------------------------------------- solicitante
    _section_title(pdf, "Datos del solicitante")
    y0 = pdf.get_y()
    _field(pdf, "Nombre completo", claim.get("nombre", ""))
    pdf.set_xy(110, y0)
    _field(pdf, "N. de contrato / DNI", claim.get("dni", ""))
    pdf.ln(14)
    y0 = pdf.get_y()
    _field(pdf, "Canal de respuesta", claim.get("canal", ""))
    pdf.set_xy(110, y0)
    contacto = claim.get("telefono") if claim.get("canal") == "Telefono / SMS" else claim.get("correo")
    _field(pdf, "Contacto", contacto or "")
    pdf.ln(14)

    # ---------------------------------------------------------- historial
    _section_title(pdf, "Historial de actualizaciones")
    historial = claim.get("historial") or []
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(38, 8, " Estado", fill=True, border=0)
    pdf.cell(42, 8, " Fecha", fill=True, border=0)
    pdf.cell(0, 8, " Nota", fill=True, border=0, ln=1)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*INK)
    for i, h in enumerate(historial):
        fill = (245, 250, 252) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*fill)
        y_before = pdf.get_y()
        x = pdf.get_x()
        pdf.multi_cell(38, 6, " " + h.get("estado", ""), fill=True, border=0)
        y_after = pdf.get_y()
        row_h = max(6, y_after - y_before)
        pdf.set_xy(x + 38, y_before)
        pdf.multi_cell(42, 6, " " + _fecha_larga(h.get("fecha", "")), fill=True, border=0)
        pdf.set_xy(x + 80, y_before)
        pdf.multi_cell(0, 6, " " + (h.get("nota", "") or ""), fill=True, border=0)
        pdf.set_xy(x, max(y_after, pdf.get_y()))

    out = pdf.output()
    return bytes(out)

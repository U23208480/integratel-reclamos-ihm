# ============================================================
# INTEGRATEL PERÚ — Envío de correo con el PDF del reclamo
#
# Si se configuran las variables de entorno SMTP_*, el correo se
# envía de verdad. Si no están configuradas, el envío se "simula":
# el .eml se guarda en backend/sent_emails/ para poder mostrarlo
# igual durante la sustentación, sin necesitar credenciales reales.
# ============================================================
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

SENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sent_emails")

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER)
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "Integratel Peru - Reclamos")

CONFIGURADO = bool(SMTP_HOST and SMTP_USER and SMTP_PASS)


def enviar_pdf_por_correo(destinatario, asunto, cuerpo_texto, cuerpo_html, pdf_bytes, filename):
    """Devuelve (ok: bool, simulado: bool, error: str|None)."""
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>" if SMTP_FROM else "Integratel Peru - Reclamos"
    msg["To"] = destinatario
    msg.set_content(cuerpo_texto)
    msg.add_alternative(cuerpo_html, subtype="html")
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    if not CONFIGURADO:
        try:
            os.makedirs(SENT_DIR, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = filename.rsplit(".", 1)[0]
            path = os.path.join(SENT_DIR, f"{ts}_{safe_name}.eml")
            with open(path, "wb") as f:
                f.write(bytes(msg))
            return True, True, None
        except Exception as e:
            return False, True, str(e)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True, False, None
    except Exception as e:
        return False, False, str(e)


def enviar_correo_simple(destinatario, asunto, cuerpo_texto, cuerpo_html, etiqueta="correo"):
    """Igual que enviar_pdf_por_correo pero sin adjunto. Devuelve (ok, simulado, error)."""
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>" if SMTP_FROM else "Integratel Peru - Reclamos"
    msg["To"] = destinatario
    msg.set_content(cuerpo_texto)
    msg.add_alternative(cuerpo_html, subtype="html")

    if not CONFIGURADO:
        try:
            os.makedirs(SENT_DIR, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(SENT_DIR, f"{ts}_{etiqueta}.eml"), "wb") as f:
                f.write(bytes(msg))
            return True, True, None
        except Exception as e:
            return False, True, str(e)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True, False, None
    except Exception as e:
        return False, False, str(e)


def construir_mensaje(claim):
    nombre = claim.get("nombre", "")
    ticket = claim["id"]
    estado = claim.get("estado", "Recibido")
    tipo = claim.get("tipo", "")
    texto = (
        f"Hola {nombre},\n\n"
        f"Hemos registrado tu reclamo en Integratel Peru con el numero de ticket {ticket}.\n"
        f"Tipo de reclamo: {tipo}\n"
        f"Estado actual: {estado}\n\n"
        f"Adjuntamos el comprobante en PDF con el detalle completo de tu reclamo.\n"
        f"Puedes consultar el estado en cualquier momento ingresando al Sistema de Gestion de Reclamos.\n\n"
        f"Gracias por contactarnos.\n"
        f"Integratel Peru S.A.A."
    )
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;">
      <div style="background:#0B2545;padding:20px 24px;border-radius:12px 12px 0 0;">
        <h1 style="color:#fff;font-size:18px;margin:0;">Integratel Peru</h1>
        <p style="color:#9FBED3;font-size:12.5px;margin:4px 0 0;">Sistema de Gestion de Reclamos</p>
      </div>
      <div style="border:1px solid #E4ECF1;border-top:none;border-radius:0 0 12px 12px;padding:24px;">
        <p style="color:#172333;font-size:14.5px;">Hola <b>{nombre}</b>,</p>
        <p style="color:#172333;font-size:14.5px;">Hemos registrado tu reclamo con el siguiente ticket:</p>
        <div style="background:#F7FAFC;border:1.5px dashed #00B4D8;border-radius:10px;padding:14px 18px;margin:16px 0;">
          <span style="font-size:11px;color:#5B6673;font-weight:bold;">NUMERO DE TICKET</span><br>
          <span style="font-size:22px;color:#0B2545;font-weight:bold;">{ticket}</span>
        </div>
        <p style="color:#172333;font-size:13.5px;"><b>Tipo:</b> {tipo}<br><b>Estado actual:</b> {estado}</p>
        <p style="color:#5B6673;font-size:13px;">Adjuntamos el comprobante en PDF con el detalle completo de tu reclamo.</p>
        <p style="color:#5B6673;font-size:12px;margin-top:24px;">Integratel Peru S.A.A. — Este es un correo automatico, por favor no respondas a este mensaje.</p>
      </div>
    </div>
    """
    return f"Integratel Peru - Reclamo {ticket} registrado", texto, html

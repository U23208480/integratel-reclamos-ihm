# -*- coding: utf-8 -*-
"""
INTEGRATEL PERÚ — Plantillas de los correos del aplicativo
-----------------------------------------------------------------
Los cuatro correos del AP3, construidos igual que en el prototipo de Figma:

  1. Verificación de correo   (al registrarse)
  2. Bienvenida               (cuando la cuenta queda activa)
  3. Recuperación de contraseña
  4. Eliminación de cuenta    (comprobante de la baja)

Reglas de accesibilidad aplicadas a los cuatro:
  · una sola columna de 600 px como máximo (100 % del ancho en el celular)
  · botón principal de 56 px de alto (supera los 44 x 44 px de WCAG 2.5.5)
  · texto real, nunca texto dentro de imágenes
  · modo noche nativo con prefers-color-scheme
  · versión en texto plano equivalente (no un resumen)
  · código alternativo cuando el cliente de correo bloquea los enlaces
"""

MARCA = "Integratel Perú"
BASE_URL = "http://localhost:5000"

# ---------------------------------------------------------------- tokens
LIGHT = dict(bg="#F7FAFC", surface="#FFFFFF", surface2="#F1F6FA", line="#E4ECF1",
             ink="#172333", ink2="#2E3E50", muted="#5B6673", navy="#0B2545",
             accent="#00B4D8", accentInk="#00748C", accentSoft="#E3F6FB",
             ok="#14754A", okSoft="#E7F8EF", warn="#8A5D05", warnSoft="#FFF6E5",
             onAccent="#06202B")
DARK = dict(bg="#081320", surface="#0F2032", surface2="#16293C", line="#23394E",
            ink="#E8F1F8", ink2="#CFE0EE", muted="#9FB3C6", navy="#050F1A",
            accent="#38CFEF", accentInk="#7EE0F7", accentSoft="#12303C",
            ok="#4BD394", okSoft="#0F2E22", warn="#F2B53B", warnSoft="#32270F",
            onAccent="#06202B")


def _css():
    """Hoja de estilo con las dos paletas. El modo noche se activa solo."""
    d = DARK
    return f"""
    :root {{ color-scheme: light dark; }}
    body,table,td,div,p,a {{ -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }}
    table {{ border-collapse:collapse !important; }}
    img {{ border:0; line-height:100%; outline:none; text-decoration:none; }}
    a {{ color:{LIGHT['accentInk']}; }}
    .btn-a:hover {{ opacity:.92; }}
    @media screen and (max-width:620px) {{
      .wrap {{ width:100% !important; }}
      .pad {{ padding-left:24px !important; padding-right:24px !important; }}
      .h1 {{ font-size:24px !important; line-height:32px !important; }}
      .btn-a {{ display:block !important; width:100% !important; box-sizing:border-box; }}
      .cod td {{ font-size:20px !important; width:42px !important; }}
    }}
    @media (prefers-color-scheme: dark) {{
      body, .body {{ background:{d['bg']} !important; }}
      .surface {{ background:{d['surface']} !important; }}
      .surface2 {{ background:{d['surface2']} !important; }}
      .navy {{ background:{d['navy']} !important; }}
      .ink {{ color:{d['ink']} !important; }}
      .ink2 {{ color:{d['ink2']} !important; }}
      .muted {{ color:{d['muted']} !important; }}
      .accentink {{ color:{d['accentInk']} !important; }}
      .accentsoft {{ background:{d['accentSoft']} !important; }}
      .oksoft {{ background:{d['okSoft']} !important; }} .ok {{ color:{d['ok']} !important; }}
      .warnsoft {{ background:{d['warnSoft']} !important; }} .warn {{ color:{d['warn']} !important; }}
      .line {{ border-color:{d['line']} !important; }}
      .btn-a {{ background:{d['accent']} !important; }}
      a {{ color:{d['accentInk']} !important; }}
    }}
    """


def _cabecera(kicker="Portal de Reclamos"):
    L = LIGHT
    return f"""
    <tr><td class="navy pad" style="background:{L['navy']};padding:26px 32px;">
      <table role="presentation" cellpadding="0" cellspacing="0"><tr>
        <td style="width:44px;">
          <table role="presentation" cellpadding="0" cellspacing="0"><tr>
            <td style="width:40px;height:40px;background:{L['accent']};border-radius:11px;
                       text-align:center;font:800 20px/40px Arial,sans-serif;color:{L['onAccent']};">I</td>
          </tr></table>
        </td>
        <td style="padding-left:12px;">
          <div style="font:800 17px/20px Arial,sans-serif;color:#FFFFFF;">Integratel</div>
          <div style="font:600 11px/16px Arial,sans-serif;color:#AFC2D4;">{kicker}</div>
        </td>
      </tr></table>
    </td></tr>"""


def _boton(texto, url):
    L = LIGHT
    return f"""
    <tr><td class="pad" style="padding:4px 32px 10px;">
      <table role="presentation" cellpadding="0" cellspacing="0" width="100%"><tr>
        <td align="center" bgcolor="{L['accent']}" class="btn-a"
            style="background:{L['accent']};border-radius:14px;height:56px;">
          <a href="{url}" class="btn-a"
             style="display:block;height:56px;line-height:56px;text-align:center;
                    font:800 16px Arial,sans-serif;color:{L['onAccent']};text-decoration:none;
                    border-radius:14px;">{texto}</a>
        </td>
      </tr></table>
      <div class="muted" style="font:400 11px/18px Arial,sans-serif;color:{L['muted']};
                                text-align:center;padding-top:8px;">Área táctil de 56 px de alto</div>
    </td></tr>"""


def _pie():
    L = LIGHT
    return f"""
    <tr><td class="surface2 pad" style="background:{L['surface2']};padding:26px 32px;
             border-top:1px solid {L['line']};text-align:center;">
      <div style="font:700 12px/18px Arial,sans-serif;">
        <a href="{BASE_URL}/sistema/index.html" class="accentink"
           style="color:{L['accentInk']};text-decoration:underline;">Ver este correo en el navegador</a>
      </div>
      <div style="padding:12px 0;font:700 11px/16px Arial,sans-serif;">
        <a href="{BASE_URL}/?lang=es" class="accentink" style="color:{L['accentInk']};">Español</a> &nbsp;·&nbsp;
        <a href="{BASE_URL}/?lang=en" class="accentink" style="color:{L['accentInk']};">English</a> &nbsp;·&nbsp;
        <a href="{BASE_URL}/?lang=qu" class="accentink" style="color:{L['accentInk']};">Runasimi</a> &nbsp;·&nbsp;
        <a href="{BASE_URL}/?lang=ay" class="accentink" style="color:{L['accentInk']};">Aymar aru</a>
      </div>
      <div class="muted" style="font:600 11px/17px Arial,sans-serif;color:{L['muted']};">
        Integratel Perú S.A.A. · RUC 20100017491<br>
        Av. República de Panamá 3045, Lima
      </div>
      <div style="padding-top:10px;font:700 11px Arial,sans-serif;">
        <a href="{BASE_URL}/sistema/accesibilidad.html" class="accentink"
           style="color:{L['accentInk']};">Declaración de accesibilidad</a>
      </div>
      <div class="muted" style="padding-top:8px;font:400 10px/15px Arial,sans-serif;color:{L['muted']};">
        Este correo también se envía en texto plano.
      </div>
    </td></tr>"""


def _documento(preheader, cuerpo_filas):
    L = LIGHT
    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>{MARCA}</title>
<style>{_css()}</style>
</head>
<body class="body" style="margin:0;padding:0;background:{L['bg']};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       class="body" style="background:{L['bg']};padding:24px 0;">
<tr><td align="center">
  <table role="presentation" class="wrap surface" width="600" cellpadding="0" cellspacing="0"
         style="width:600px;max-width:600px;background:{L['surface']};border-radius:16px;overflow:hidden;">
    {cuerpo_filas}
  </table>
</td></tr></table>
</body></html>"""


# ============================================================ 1 · verificación
def verificacion(nombre, codigo, enlace):
    L = LIGHT
    celdas = "".join(
        f'<td class="surface line" style="width:46px;height:50px;border:1.4px solid {L["line"]};'
        f'border-radius:10px;text-align:center;font:800 21px Courier New,monospace;color:{L["ink"]};'
        f'background:{L["surface"]};">{d}</td><td style="width:8px;"></td>'
        for d in codigo)
    cuerpo = (
        _cabecera()
        + f"""
    <tr><td class="pad" style="padding:26px 32px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0"><tr>
        <td class="accentsoft" style="background:{L['accentSoft']};border-radius:13px;padding:6px 14px;
            font:800 10.5px Arial,sans-serif;letter-spacing:1.1px;color:{L['accentInk']};">PASO 1 DE 2 · REGISTRO</td>
      </tr></table>
    </td></tr>
    <tr><td class="pad" style="padding:20px 32px 0;">
      <div class="h1 ink" style="font:800 26px/32px Arial,sans-serif;color:{L['ink']};">Confirma tu correo</div>
      <div class="ink2" style="font:400 15px/23px Arial,sans-serif;color:{L['ink2']};padding-top:12px;">
        Hola, {nombre}. Creaste una cuenta en el Portal de Reclamos de Integratel.
        Confirma este correo para activarla.
      </div>
    </td></tr>
    <tr><td style="height:22px;"></td></tr>"""
        + _boton("Confirmar mi correo", enlace)
        + f"""
    <tr><td class="pad" style="padding:14px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="surface2 line" style="background:{L['surface2']};border:1px solid {L['line']};border-radius:14px;">
        <tr><td style="padding:18px;text-align:center;">
          <div class="muted" style="font:400 12px Arial,sans-serif;color:{L['muted']};padding-bottom:12px;">
            ¿El botón no funciona? Usa este código:</div>
          <table role="presentation" cellpadding="0" cellspacing="0" align="center" class="cod"><tr>{celdas}</tr></table>
        </td></tr>
      </table>
      <div class="muted" style="font:400 12px/20px Arial,sans-serif;color:{L['muted']};padding-top:16px;">
        El enlace y el código vencen en 24 horas. Si no creaste esta cuenta, ignora este mensaje.
      </div>
    </td></tr>
    <tr><td style="height:26px;"></td></tr>"""
        + _pie())
    texto = "\n".join([
        "INTEGRATEL PERU - PORTAL DE RECLAMOS", "Confirma tu correo", "",
        f"Hola, {nombre}.",
        "Creaste una cuenta en el Portal de Reclamos de Integratel.",
        "Confirma este correo para activarla.", "",
        "Confirmar mi correo:", enlace, "",
        f"Si el enlace no funciona, usa este codigo: {codigo}",
        "El enlace y el codigo vencen en 24 horas.",
        "Si no creaste esta cuenta, ignora este mensaje.", "",
        "---", "Integratel Peru S.A.A. - RUC 20100017491",
        "Av. Republica de Panama 3045, Lima",
        "Declaracion de accesibilidad | Darse de baja"])
    return "Confirma tu correo - Integratel Perú", texto, _documento(
        "Confirma tu correo para activar tu cuenta del Portal de Reclamos.", cuerpo)


# ============================================================ 2 · bienvenida
def bienvenida(nombre, correo, creada):
    L = LIGHT
    cuerpo = (
        _cabecera()
        + f"""
    <tr><td class="pad" style="padding:30px 32px 0;text-align:center;">
      <table role="presentation" cellpadding="0" cellspacing="0" align="center"><tr>
        <td class="oksoft" style="width:60px;height:60px;background:{L['okSoft']};border-radius:30px;
            text-align:center;font:800 30px/60px Arial,sans-serif;color:{L['ok']};">&#10003;</td>
      </tr></table>
      <div class="h1 ink" style="font:800 26px/34px Arial,sans-serif;color:{L['ink']};padding-top:18px;">
        Tu cuenta está lista</div>
      <div class="muted" style="font:400 14px/22px Arial,sans-serif;color:{L['muted']};padding-top:8px;">
        Ya puedes registrar y seguir tus reclamos.</div>
    </td></tr>
    <tr><td class="pad" style="padding:22px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="surface2 line" style="background:{L['surface2']};border:1px solid {L['line']};border-radius:14px;">
        <tr><td style="padding:16px 20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr><td class="muted" style="font:600 12px/26px Arial,sans-serif;color:{L['muted']};">Usuario</td>
                <td class="ink" align="right" style="font:700 12px/26px Arial,sans-serif;color:{L['ink']};">{correo}</td></tr>
            <tr><td class="muted" style="font:600 12px/26px Arial,sans-serif;color:{L['muted']};">Creada el</td>
                <td class="ink" align="right" style="font:700 12px/26px Arial,sans-serif;color:{L['ink']};">{creada}</td></tr>
          </table>
        </td></tr>
      </table>
    </td></tr>
    <tr><td style="height:20px;"></td></tr>"""
        + _boton("Ir al Portal de Reclamos", f"{BASE_URL}/sistema/mis-reclamos.html")
        + f"""
    <tr><td class="pad" style="padding:12px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="accentsoft" style="background:{L['accentSoft']};border-radius:14px;">
        <tr><td style="padding:18px 20px;">
          <div class="accentink" style="font:800 13.5px Arial,sans-serif;color:{L['accentInk']};">
            Configura tu accesibilidad</div>
          <div class="muted" style="font:400 12px/19px Arial,sans-serif;color:{L['muted']};padding-top:6px;">
            Texto grande, modo noche, lectura por voz e idioma (español, inglés, quechua o aymara).
            <a href="{BASE_URL}/sistema/accesibilidad.html" class="accentink"
               style="color:{L['accentInk']};font-weight:700;">Abrir el centro de accesibilidad</a>
          </div>
        </td></tr>
      </table>
    </td></tr>
    <tr><td style="height:26px;"></td></tr>"""
        + _pie())
    texto = "\n".join([
        "INTEGRATEL PERU - PORTAL DE RECLAMOS", "Tu cuenta esta lista", "",
        f"Hola, {nombre}. Ya puedes registrar y seguir tus reclamos.", "",
        f"Usuario: {correo}", f"Creada el: {creada}", "",
        "Ir al Portal de Reclamos:", f"{BASE_URL}/sistema/mis-reclamos.html", "",
        "Configura tu accesibilidad (texto grande, modo noche, lectura por voz e idioma):",
        f"{BASE_URL}/sistema/accesibilidad.html", "",
        "---", "Integratel Peru S.A.A. - RUC 20100017491"])
    return "Tu cuenta está lista - Integratel Perú", texto, _documento(
        "Tu cuenta del Portal de Reclamos quedó activa.", cuerpo)


# ============================================================ 3 · recuperación
def recuperacion(nombre, enlace, clave_txt):
    L = LIGHT
    cuerpo = (
        _cabecera()
        + f"""
    <tr><td class="pad" style="padding:28px 32px 0;">
      <table role="presentation" cellpadding="0" cellspacing="0"><tr>
        <td class="accentsoft" style="width:46px;height:46px;background:{L['accentSoft']};border-radius:13px;
            text-align:center;font:800 22px/46px Arial,sans-serif;color:{L['accentInk']};">&#9919;</td>
      </tr></table>
      <div class="h1 ink" style="font:800 25px/32px Arial,sans-serif;color:{L['ink']};padding-top:18px;">
        Restablece tu contraseña</div>
      <div class="ink2" style="font:400 14px/22px Arial,sans-serif;color:{L['ink2']};padding-top:10px;">
        Hola, {nombre}. Pediste cambiar la contraseña de tu cuenta del Portal de Reclamos.
      </div>
      <div class="ink2" style="font:400 14px/22px Arial,sans-serif;color:{L['ink2']};padding-top:10px;">
        {clave_txt}
      </div>
    </td></tr>
    <tr><td style="height:20px;"></td></tr>"""
        + _boton("Crear una contraseña nueva", enlace)
        + f"""
    <tr><td class="pad" style="padding:12px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="warnsoft" style="background:{L['warnSoft']};border-radius:12px;">
        <tr><td style="padding:14px 18px;">
          <span class="warn" style="font:800 12.5px Arial,sans-serif;color:{L['warn']};">
            El enlace vence en 60 minutos.</span>
        </td></tr>
      </table>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="surface2 line" style="background:{L['surface2']};border:1px solid {L['line']};
             border-radius:12px;margin-top:12px;">
        <tr><td style="padding:14px 18px;">
          <div class="ink" style="font:800 12px Arial,sans-serif;color:{L['ink']};">¿No fuiste tú?</div>
          <div class="muted" style="font:400 11.5px/18px Arial,sans-serif;color:{L['muted']};padding-top:4px;">
            Ignora este correo: tu contraseña no cambia hasta que uses el enlace.</div>
        </td></tr>
      </table>
    </td></tr>
    <tr><td style="height:26px;"></td></tr>"""
        + _pie())
    texto = "\n".join([
        "INTEGRATEL PERU - PORTAL DE RECLAMOS", "Restablece tu contrasena", "",
        f"Hola, {nombre}.",
        "Pediste cambiar la contrasena de tu cuenta del Portal de Reclamos.",
        clave_txt, "", "Crear una contrasena nueva:", enlace, "",
        "El enlace vence en 60 minutos.",
        "No fuiste tu? Ignora este correo.", "",
        "---", "Integratel Peru S.A.A. - RUC 20100017491"])
    return "Restablece tu contraseña - Integratel Perú", texto, _documento(
        "Instrucciones para restablecer la contraseña de tu cuenta.", cuerpo)


# ============================================================ 4 · eliminación
def eliminacion(nombre, fecha_baja, fecha_limite, enlace_restaurar, reclamos_vigentes):
    L = LIGHT
    lista = ", ".join(reclamos_vigentes) if reclamos_vigentes else "ninguno"
    cuerpo = (
        _cabecera()
        + f"""
    <tr><td class="pad" style="padding:28px 32px 0;">
      <div class="h1 ink" style="font:800 25px/32px Arial,sans-serif;color:{L['ink']};">
        Tu cuenta fue eliminada</div>
      <div class="ink2" style="font:400 14px/22px Arial,sans-serif;color:{L['ink2']};padding-top:12px;">
        Hola, {nombre}. El {fecha_baja} eliminaste tu cuenta del Portal de Reclamos.
        Cerramos tu sesión en todos los equipos.
      </div>
    </td></tr>
    <tr><td class="pad" style="padding:20px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="warnsoft" style="background:{L['warnSoft']};border-radius:14px;">
        <tr><td style="padding:18px 20px;">
          <div class="warn" style="font:800 13.5px Arial,sans-serif;color:{L['warn']};">
            Tienes hasta el {fecha_limite}</div>
          <div class="ink2" style="font:400 12px/19px Arial,sans-serif;color:{L['ink2']};padding-top:6px;">
            Dentro de esos 30 días puedes recuperar tu cuenta y todo tu historial.
            Después de esa fecha la eliminación es definitiva.
          </div>
        </td></tr>
      </table>
    </td></tr>
    <tr><td style="height:20px;"></td></tr>"""
        + _boton("Recuperar mi cuenta", enlace_restaurar)
        + f"""
    <tr><td class="pad" style="padding:12px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             class="surface2 line" style="background:{L['surface2']};border:1px solid {L['line']};border-radius:12px;">
        <tr><td style="padding:16px 20px;">
          <div class="ink" style="font:800 12.5px Arial,sans-serif;color:{L['ink']};">
            Tus reclamos siguen vigentes</div>
          <div class="muted" style="font:400 11.5px/18px Arial,sans-serif;color:{L['muted']};padding-top:5px;">
            Se elimina tu cuenta de acceso. Los reclamos ya registrados se conservan de forma
            anonimizada, porque su trazabilidad responde a la regulación del sector.<br>
            Reclamos en curso: {lista}
          </div>
        </td></tr>
      </table>
      <div class="muted" style="font:400 11.5px/18px Arial,sans-serif;color:{L['muted']};padding-top:14px;">
        Si no pediste esta baja, usa el botón de arriba para recuperar tu cuenta de inmediato.
      </div>
    </td></tr>
    <tr><td style="height:26px;"></td></tr>"""
        + _pie())
    texto = "\n".join([
        "INTEGRATEL PERU - PORTAL DE RECLAMOS", "Tu cuenta fue eliminada", "",
        f"Hola, {nombre}.",
        f"El {fecha_baja} eliminaste tu cuenta del Portal de Reclamos.",
        "Cerramos tu sesion en todos los equipos.", "",
        f"Tienes hasta el {fecha_limite} para recuperarla con todo tu historial.",
        "Despues de esa fecha la eliminacion es definitiva.", "",
        "Recuperar mi cuenta:", enlace_restaurar, "",
        f"Tus reclamos siguen vigentes: {lista}",
        "Se elimina la cuenta de acceso; los reclamos se conservan anonimizados.", "",
        "Si no pediste esta baja, usa el enlace de arriba de inmediato.", "",
        "---", "Integratel Peru S.A.A. - RUC 20100017491"])
    return "Tu cuenta fue eliminada - Integratel Perú", texto, _documento(
        "Confirmación de la baja de tu cuenta y plazo para revertirla.", cuerpo)


PLANTILLAS = {
    "verificacion": verificacion,
    "bienvenida": bienvenida,
    "recuperacion": recuperacion,
    "eliminacion": eliminacion,
}

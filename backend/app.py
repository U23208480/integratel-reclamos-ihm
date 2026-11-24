# ============================================================
# INTEGRATEL PERÚ — Backend del Sistema de Gestión de Reclamos
# Flask + MySQL (base de datos relacional real, servida por MySQL Server
# y administrable desde MySQL Workbench)
# ============================================================
import os
import re
import json
import secrets
import pymysql
import pymysql.cursors
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify, send_from_directory, g, Response

from pdf_utils import generar_pdf_reclamo
from email_utils import enviar_pdf_por_correo, enviar_correo_simple, construir_mensaje, CONFIGURADO as EMAIL_CONFIGURADO
import email_templates as PLANTILLAS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # integratel-web/
PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdfs")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "integratel_app")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "IntegratelReclamos2026!")
MYSQL_DB = os.environ.get("MYSQL_DB", "integratel_reclamos")

DEMO_DNI = "71234567"
ESTADOS = ["Recibido", "En proceso", "Atendido", "Improcedente"]
TIPOS_RECLAMO = [
    "Facturación y cobros",
    "Avería / corte de servicio",
    "Instalación o mantenimiento",
    "Atención al cliente",
    "Velocidad / calidad de conexión",
    "Otro",
]
DIAS_GRACIA = 30            # periodo en el que la baja de cuenta puede revertirse
IDIOMAS = ["es", "en", "qu", "ay"]

# Los 23 ajustes del modulo de accesibilidad (AP3). Son los valores por defecto:
# la interfaz sin tocar nada ya cumple WCAG 2.1 AA, el modulo solo la adapta.
PREFS_DEFECTO = {
    # --- visual (8)
    "fs": 100,                 # 100 | 125 | 150 | 200
    "contraste": "normal",     # normal | alto | invertido
    "tema": "auto",            # dia | noche | auto
    "fuente": "sistema",       # sistema | legible
    "espaciado": "normal",     # normal | amplio | muy-amplio
    "enlaces": False,          # resaltar enlaces con subrayado
    "movimiento": False,       # reducir movimiento
    "guia": False,             # guia de lectura y cursor grande
    # --- auditivo (6)
    "voz": False,              # lectura por voz de la pagina
    "vozVel": 1,               # 0.75 | 1 | 1.25 | 1.5
    "subtitulos": True,
    "transcripcion": True,
    "lsp": False,              # interprete de Lengua de Senas Peruana
    "alertasVisuales": True,
    # --- navegacion y teclado (5)
    "foco": True,              # indicador de foco reforzado
    "saltar": True,            # enlace "saltar al contenido"
    "atajos": True,            # atajos de teclado con Alt
    "sesion": 40,              # 20 | 40 | 0 (sin limite), en minutos
    "confirmar": True,         # confirmar acciones irreversibles
    # --- idioma y lectura facil (4)
    "idioma": "es",
    "lecturaFacil": False,
    "glosario": True,
    "traducir": False,
}

NOTAS_ESTADO = {
    "Recibido": "Reclamo registrado a través del sistema web.",
    "En proceso": "El área responsable tomó el caso y está evaluando la incidencia.",
    "Atendido": "El reclamo fue resuelto y notificado al usuario.",
    "Improcedente": "El reclamo fue evaluado y calificado como improcedente. Se notificó el motivo al usuario.",
}

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


# ---------------------------------------------------------------- DB helpers (MySQL, vía PyMySQL)
class MySQLConn:
    """Envoltorio fino sobre PyMySQL para poder seguir escribiendo
    db.execute("... ? ...", (params,)).fetchone()/.fetchall() igual que con sqlite3."""

    def __init__(self, database=MYSQL_DB):
        self.conn = pymysql.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
            database=database, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query.replace("?", "%s"), params)
        return cur

    def executescript(self, script):
        cur = self.conn.cursor()
        for statement in script.strip().split(";"):
            s = statement.strip()
            if s:
                cur.execute(s)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db():
    if "db" not in g:
        g.db = MySQLConn()
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat()


def init_db():
    # La base de datos y el usuario 'integratel_app' se crean con
    # backend/crear_usuario_mysql.sql (ejecutado una vez desde MySQL Workbench).
    db = MySQLConn()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            dni VARCHAR(12) PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            correo VARCHAR(150) NOT NULL,
            telefono VARCHAR(30),
            password VARCHAR(255) NOT NULL,
            created_at VARCHAR(40) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS reclamos (
            id VARCHAR(20) PRIMARY KEY,
            dni VARCHAR(12) NOT NULL,
            nombre VARCHAR(150) NOT NULL,
            tipo VARCHAR(100) NOT NULL,
            descripcion TEXT NOT NULL,
            canal VARCHAR(50) NOT NULL,
            correo VARCHAR(150),
            telefono VARCHAR(30),
            archivos TEXT,
            estado VARCHAR(30) NOT NULL,
            created_at VARCHAR(40) NOT NULL,
            FOREIGN KEY (dni) REFERENCES usuarios (dni)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            reclamo_id VARCHAR(20) NOT NULL,
            estado VARCHAR(30) NOT NULL,
            fecha VARCHAR(40) NOT NULL,
            nota TEXT,
            FOREIGN KEY (reclamo_id) REFERENCES reclamos (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS notificaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dni VARCHAR(12) NOT NULL,
            tipo VARCHAR(40) NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            detalle TEXT,
            reclamo_id VARCHAR(20),
            leida TINYINT(1) NOT NULL DEFAULT 0,
            created_at VARCHAR(40) NOT NULL,
            INDEX idx_notif_dni (dni)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS bajas_cuenta (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dni VARCHAR(12) NOT NULL,
            motivo VARCHAR(120),
            comentario TEXT,
            solicitada_at VARCHAR(40) NOT NULL,
            efectiva_at VARCHAR(40) NOT NULL,
            restaurada_at VARCHAR(40),
            INDEX idx_baja_dni (dni)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    db.commit()

    # ---------------------------------------------------------------- migracion de 'usuarios'
    # El AP3 agrega accesibilidad, idioma y baja de cuenta. Se agregan solo
    # las columnas que falten, para no perder los datos ya cargados.
    columnas_nuevas = [
        ("preferencias", "TEXT"),
        ("idioma", "VARCHAR(5) NOT NULL DEFAULT 'es'"),
        ("estado_cuenta", "VARCHAR(20) NOT NULL DEFAULT 'activa'"),
        ("correo_verificado", "TINYINT(1) NOT NULL DEFAULT 0"),
        ("codigo_verificacion", "VARCHAR(12)"),
        ("codigo_expira", "VARCHAR(40)"),
        ("codigo_baja", "VARCHAR(12)"),
        ("codigo_baja_expira", "VARCHAR(40)"),
        ("baja_solicitada_at", "VARCHAR(40)"),
        ("baja_efectiva_at", "VARCHAR(40)"),
        ("notificaciones_silenciadas", "TINYINT(1) NOT NULL DEFAULT 0"),
        ("ultimo_acceso", "VARCHAR(40)"),
    ]
    existentes = {r["Field"] for r in db.execute("SHOW COLUMNS FROM usuarios").fetchall()}
    for nombre, tipo in columnas_nuevas:
        if nombre not in existentes:
            db.execute(f"ALTER TABLE usuarios ADD COLUMN {nombre} {tipo}")
    db.commit()

    # las cuentas que ya existian quedan verificadas y con las preferencias por defecto
    db.execute("UPDATE usuarios SET correo_verificado = 1 WHERE correo_verificado = 0 AND created_at < ?", (now_iso(),))
    db.execute("UPDATE usuarios SET preferencias = ? WHERE preferencias IS NULL", (json.dumps(PREFS_DEFECTO),))
    db.commit()

    # ---------------------------------------------------------------- seed
    cur = db.execute("SELECT COUNT(*) AS c FROM usuarios")
    if cur.fetchone()["c"] == 0:
        demo_dni = "71234567"
        db.execute(
            "INSERT INTO usuarios (dni, nombre, correo, telefono, password, created_at) VALUES (?,?,?,?,?,?)",
            (demo_dni, "Juan Pérez García", "juan.perez@ejemplo.com", "+51 987 654 321", "Demo1234", now_iso()),
        )

        demo_claims = [
            dict(tipo="Avería / corte de servicio",
                 descripcion="Corte de señal en el sector de Surquillo desde hace 2 días, afecta el enlace de internet dedicado.",
                 canal="Correo electrónico", archivos=["evidencia_averia.jpg"], estado="En proceso", dias_atras=6),
            dict(tipo="Facturación y cobros",
                 descripcion="Se facturó un cargo adicional no reconocido en el ciclo de julio.",
                 canal="Teléfono / SMS", archivos=[], estado="Atendido", dias_atras=14),
            dict(tipo="Instalación o mantenimiento",
                 descripcion="Solicitud de reprogramación de visita técnica para mantenimiento de fibra óptica.",
                 canal="Correo electrónico", archivos=["orden_servicio.pdf"], estado="Recibido", dias_atras=0),
        ]
        for i, c in enumerate(demo_claims, start=1):
            claim_id = f"REC-{datetime.now().year}-{i:05d}"
            created = now_iso()
            db.execute(
                "INSERT INTO reclamos (id, dni, nombre, tipo, descripcion, canal, correo, telefono, archivos, estado, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (claim_id, demo_dni, "Juan Pérez García", c["tipo"], c["descripcion"], c["canal"],
                 "juan.perez@ejemplo.com", "+51 987 654 321", json.dumps(c["archivos"]), c["estado"], created),
            )
            db.execute(
                "INSERT INTO historial (reclamo_id, estado, fecha, nota) VALUES (?,?,?,?)",
                (claim_id, "Recibido", created, NOTAS_ESTADO["Recibido"]),
            )
            if c["estado"] in ("En proceso", "Atendido", "Improcedente"):
                db.execute(
                    "INSERT INTO historial (reclamo_id, estado, fecha, nota) VALUES (?,?,?,?)",
                    (claim_id, "En proceso", created, NOTAS_ESTADO["En proceso"]),
                )
            if c["estado"] in ("Atendido", "Improcedente"):
                db.execute(
                    "INSERT INTO historial (reclamo_id, estado, fecha, nota) VALUES (?,?,?,?)",
                    (claim_id, c["estado"], created, NOTAS_ESTADO[c["estado"]]),
                )
        db.commit()
    db.close()


# ---------------------------------------------------------------- serializers
def leer_prefs(row):
    """Preferencias del usuario, completadas con los valores por defecto."""
    prefs = dict(PREFS_DEFECTO)
    try:
        guardadas = json.loads(row.get("preferencias") or "{}")
        if isinstance(guardadas, dict):
            prefs.update({k: v for k, v in guardadas.items() if k in PREFS_DEFECTO})
    except Exception:
        pass
    prefs["idioma"] = row.get("idioma") or prefs.get("idioma") or "es"
    return prefs


def user_public(row):
    return {
        "dni": row["dni"], "nombre": row["nombre"], "correo": row["correo"],
        "telefono": row["telefono"],
        "idioma": row.get("idioma") or "es",
        "estadoCuenta": row.get("estado_cuenta") or "activa",
        "correoVerificado": bool(row.get("correo_verificado")),
        "notificacionesSilenciadas": bool(row.get("notificaciones_silenciadas")),
        "bajaSolicitadaAt": row.get("baja_solicitada_at"),
        "bajaEfectivaAt": row.get("baja_efectiva_at"),
        "ultimoAcceso": row.get("ultimo_acceso"),
        "createdAt": row.get("created_at"),
        "preferencias": leer_prefs(row),
    }


def codigo_6():
    return "".join(secrets.choice("0123456789") for _ in range(6))


def mas_horas(horas):
    return (datetime.now(timezone.utc).astimezone() + timedelta(hours=horas)).isoformat()


def vencido(iso):
    if not iso:
        return True
    try:
        return datetime.fromisoformat(iso) < datetime.now(timezone.utc).astimezone()
    except Exception:
        return True


def fecha_larga(iso):
    MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "setiembre", "octubre", "noviembre", "diciembre"]
    try:
        d = datetime.fromisoformat(iso)
    except Exception:
        d = datetime.now()
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def notificar(db, dni, tipo, titulo, detalle="", reclamo_id=None):
    """Deja una notificacion en la bandeja del usuario (alimenta el estado vacio por historial)."""
    fila = db.execute("SELECT notificaciones_silenciadas FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if fila and fila.get("notificaciones_silenciadas"):
        return
    db.execute(
        "INSERT INTO notificaciones (dni, tipo, titulo, detalle, reclamo_id, leida, created_at) VALUES (?,?,?,?,?,0,?)",
        (dni, tipo, titulo, detalle, reclamo_id, now_iso()),
    )


def enviar_plantilla(nombre_plantilla, destinatario, *args, etiqueta=""):
    """Envia uno de los cuatro correos del aplicativo. Nunca lanza excepciones."""
    try:
        asunto, texto, html = PLANTILLAS.PLANTILLAS[nombre_plantilla](*args)
        ok, simulado, error = enviar_correo_simple(
            destinatario, asunto, texto, html, etiqueta=etiqueta or nombre_plantilla)
        return {"enviado": bool(ok), "simulado": bool(simulado), "error": error, "destinatario": destinatario}
    except Exception as e:
        return {"enviado": False, "simulado": False, "error": str(e), "destinatario": destinatario}


def claim_public(row, with_historial=False, db=None):
    d = {
        "id": row["id"], "dni": row["dni"], "nombre": row["nombre"], "tipo": row["tipo"],
        "descripcion": row["descripcion"], "canal": row["canal"], "correo": row["correo"],
        "telefono": row["telefono"], "archivos": json.loads(row["archivos"] or "[]"),
        "estado": row["estado"], "createdAt": row["created_at"],
    }
    if with_historial and db is not None:
        hist = db.execute(
            "SELECT estado, fecha, nota FROM historial WHERE reclamo_id = ? ORDER BY id ASC", (row["id"],)
        ).fetchall()
        d["historial"] = [{"estado": h["estado"], "fecha": h["fecha"], "nota": h["nota"]} for h in hist]
    return d


# ---------------------------------------------------------------- PDF + correo
def claim_with_historial(db, claim_id):
    row = db.execute("SELECT * FROM reclamos WHERE id = ?", (claim_id,)).fetchone()
    if not row:
        return None
    return claim_public(row, with_historial=True, db=db)


def guardar_copia_pdf(claim_id, pdf_bytes):
    try:
        os.makedirs(PDF_DIR, exist_ok=True)
        with open(os.path.join(PDF_DIR, f"{claim_id}.pdf"), "wb") as f:
            f.write(pdf_bytes)
    except Exception:
        pass


def intentar_enviar_correo(claim):
    """Genera el PDF, lo guarda en disco y lo envía por correo (o lo simula). No lanza excepciones."""
    try:
        pdf_bytes = generar_pdf_reclamo(claim)
        guardar_copia_pdf(claim["id"], pdf_bytes)
        destinatario = claim.get("correo")
        if not destinatario:
            return {"enviado": False, "simulado": False, "error": "El reclamo no tiene un correo de contacto registrado."}
        asunto, texto, html = construir_mensaje(claim)
        ok, simulado, error = enviar_pdf_por_correo(destinatario, asunto, texto, html, pdf_bytes, f"{claim['id']}.pdf")
        return {"enviado": ok, "simulado": simulado, "error": error, "destinatario": destinatario}
    except Exception as e:
        return {"enviado": False, "simulado": False, "error": str(e)}


# ---------------------------------------------------------------- validation
def valid_dni(dni):
    return bool(re.fullmatch(r"\d{6,12}", dni or ""))


def valid_email(email):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email or ""))


# ---------------------------------------------------------------- simulacion de estados
# Permite demostrar en vivo los estados del catalogo del AP3 sin tener que
# desconectar la red ni apagar la base de datos:  ?simular=error-sistema
def _simular(valor):
    v = (valor or "").strip().lower()
    if not v:
        return None
    if v == "lento":
        import time
        time.sleep(3)
        return None
    if v == "vacio":
        return jsonify(ok=True, reclamos=[], notificaciones=[], simulado="vacio")
    if v in ("error-conexion", "conexion"):
        return jsonify(ok=False, codigo="error_conexion",
                       error="No se pudo contactar con el servicio. Revisa tu conexión a internet."), 503
    if v in ("error-sistema", "sistema"):
        incidente = "INC-" + datetime.now().strftime("%H%M")
        return jsonify(ok=False, codigo="error_sistema", incidente=incidente,
                       error="El servicio de consulta no respondió. El fallo es nuestro: tu reclamo "
                             "sigue registrado y su plazo continúa corriendo."), 500
    if v in ("no-disponible", "archivado"):
        return jsonify(ok=False, codigo="no_disponible",
                       error="Este reclamo pasó al archivo histórico y ya no está disponible en línea."), 410
    if v in ("sin-permisos", "permisos"):
        return jsonify(ok=False, codigo="sin_permisos",
                       error="Tu sesión venció por inactividad. Vuelve a iniciar sesión para continuar."), 403
    return None


# ============================================================
# API — usuarios
# ============================================================
@app.post("/api/registro")
def registro():
    data = request.get_json(force=True) or {}
    nombre = (data.get("nombre") or "").strip()
    dni = (data.get("dni") or "").strip()
    correo = (data.get("correo") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    password = data.get("password") or ""

    if not nombre or len(nombre) < 3:
        return jsonify(ok=False, error="Ingresa tu nombre completo."), 400
    if not valid_dni(dni):
        return jsonify(ok=False, error="El N° de contrato o DNI debe tener entre 6 y 12 dígitos."), 400
    if not valid_email(correo):
        return jsonify(ok=False, error="Ingresa un correo electrónico válido."), 400
    if len(password) < 6:
        return jsonify(ok=False, error="La contraseña debe tener al menos 6 caracteres."), 400

    db = get_db()
    if db.execute("SELECT 1 FROM usuarios WHERE dni = ?", (dni,)).fetchone():
        return jsonify(ok=False, error="Ya existe una cuenta registrada con ese N° de contrato o DNI."), 409

    idioma = (data.get("idioma") or "es").strip()
    if idioma not in IDIOMAS:
        idioma = "es"

    codigo = codigo_6()
    db.execute(
        """INSERT INTO usuarios (dni, nombre, correo, telefono, password, created_at,
                                 preferencias, idioma, estado_cuenta, correo_verificado,
                                 codigo_verificacion, codigo_expira)
           VALUES (?,?,?,?,?,?,?,?,'activa',0,?,?)""",
        (dni, nombre, correo, telefono, password, now_iso(),
         json.dumps(dict(PREFS_DEFECTO, idioma=idioma)), idioma, codigo, mas_horas(24)),
    )

    # Correo 1 — verificacion de la direccion (paso 1 de 2 del registro)
    enlace = f"{PLANTILLAS.BASE_URL}/api/verificar?dni={dni}&codigo={codigo}"
    correo_verificacion = enviar_plantilla("verificacion", correo, nombre, codigo, enlace,
                                           etiqueta="verificacion_" + dni)
    notificar(db, dni, "cuenta", "Confirma tu correo electrónico",
              "Te enviamos un enlace a " + correo + ". El enlace vence en 24 horas.")
    db.commit()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    return jsonify(ok=True, user=user_public(user), correoVerificacion=correo_verificacion)


@app.get("/api/verificar")
def verificar_correo():
    """Confirma la direccion de correo y dispara el correo 2 (bienvenida)."""
    dni = (request.args.get("dni") or "").strip()
    codigo = (request.args.get("codigo") or "").strip()
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    destino = "/sistema/index.html"
    if not user:
        return _redirigir(destino + "?verificacion=noexiste")
    if user.get("correo_verificado"):
        return _redirigir(destino + "?verificacion=ya")
    if not codigo or codigo != (user.get("codigo_verificacion") or "") or vencido(user.get("codigo_expira")):
        return _redirigir(destino + "?verificacion=invalida")

    db.execute("UPDATE usuarios SET correo_verificado = 1, codigo_verificacion = NULL, codigo_expira = NULL WHERE dni = ?", (dni,))
    # Correo 2 — bienvenida
    enviar_plantilla("bienvenida", user["correo"], user["nombre"], user["correo"],
                     fecha_larga(user["created_at"]), etiqueta="bienvenida_" + dni)
    notificar(db, dni, "cuenta", "Tu cuenta quedó activa",
              "Ya puedes registrar y seguir tus reclamos.")
    db.commit()
    return _redirigir(destino + "?verificacion=ok")


@app.post("/api/reenviar-verificacion")
def reenviar_verificacion():
    data = request.get_json(force=True) or {}
    dni = (data.get("dni") or "").strip()
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    if user.get("correo_verificado"):
        return jsonify(ok=True, yaVerificado=True)
    codigo = codigo_6()
    db.execute("UPDATE usuarios SET codigo_verificacion = ?, codigo_expira = ? WHERE dni = ?",
               (codigo, mas_horas(24), dni))
    db.commit()
    enlace = f"{PLANTILLAS.BASE_URL}/api/verificar?dni={dni}&codigo={codigo}"
    info = enviar_plantilla("verificacion", user["correo"], user["nombre"], codigo, enlace,
                            etiqueta="verificacion_" + dni)
    return jsonify(ok=True, correo=info)


def _redirigir(ruta):
    return Response("", status=302, headers={"Location": ruta})


@app.post("/api/login")
def login():
    data = request.get_json(force=True) or {}
    dni = (data.get("dni") or "").strip()
    password = data.get("password") or ""
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="No existe una cuenta registrada con ese N° de contrato o DNI."), 404
    if user["password"] != password:
        return jsonify(ok=False, error="La contraseña ingresada es incorrecta."), 401

    estado = user.get("estado_cuenta") or "activa"
    if estado == "eliminada":
        # Estado 9 del catalogo (sin permisos), con la salida que corresponde:
        # la cuenta esta en periodo de gracia y puede recuperarse.
        return jsonify(ok=False, codigo="cuenta_eliminada",
                       error="Esta cuenta fue eliminada el " + fecha_larga(user.get("baja_solicitada_at") or now_iso()) +
                             ". Puedes recuperarla hasta el " + fecha_larga(user.get("baja_efectiva_at") or now_iso()) + ".",
                       bajaEfectivaAt=user.get("baja_efectiva_at"), dni=user["dni"]), 403
    if estado == "desactivada":
        return jsonify(ok=False, codigo="cuenta_desactivada",
                       error="Tu cuenta está desactivada temporalmente. Puedes reactivarla ahora mismo.",
                       dni=user["dni"]), 403

    db.execute("UPDATE usuarios SET ultimo_acceso = ? WHERE dni = ?", (now_iso(), user["dni"]))
    db.commit()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    return jsonify(ok=True, user=user_public(user))


@app.post("/api/recuperar")
def recuperar():
    """Recuperación de contraseña. Siempre responde igual para no revelar si la cuenta existe."""
    data = request.get_json(force=True) or {}
    ident = (data.get("identificador") or "").strip()
    if not ident:
        return jsonify(ok=False, error="Ingresa tu correo o N° de contrato/DNI."), 400

    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ? OR LOWER(correo) = LOWER(?)", (ident, ident)).fetchone()
    if user and user.get("correo"):
        if user["dni"] == DEMO_DNI:
            clave_txt = "Esta es la cuenta de demostración: su contraseña no se modifica (Demo1234)."
        else:
            temporal = "Tmp" + secrets.token_hex(4)
            db.execute("UPDATE usuarios SET password = ? WHERE dni = ?", (temporal, user["dni"]))
            db.commit()
            clave_txt = f"Tu contraseña temporal es: {temporal}. Ingresa con ella y cámbiala desde Mi perfil."
        enlace = f"{PLANTILLAS.BASE_URL}/sistema/index.html?dni={user['dni']}"
        enviar_plantilla("recuperacion", user["correo"], user["nombre"], enlace, clave_txt,
                         etiqueta="recuperar_" + user["dni"])
        notificar(db, user["dni"], "seguridad", "Se pidió restablecer tu contraseña",
                  "Si no fuiste tú, cambia tu contraseña desde Mi perfil.")
        db.commit()
    return jsonify(ok=True, mensaje="Si el dato coincide con una cuenta activa, recibirás las instrucciones en el correo registrado.")


@app.get("/api/perfil/<dni>")
def get_perfil(dni):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    return jsonify(ok=True, user=user_public(user))


@app.patch("/api/perfil/<dni>")
def update_perfil(dni):
    data = request.get_json(force=True) or {}
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404

    nombre = (data.get("nombre") or user["nombre"]).strip()
    correo = (data.get("correo") or user["correo"]).strip()
    telefono = data.get("telefono", user["telefono"])
    if correo and not valid_email(correo):
        return jsonify(ok=False, error="Ingresa un correo electrónico válido."), 400

    db.execute("UPDATE usuarios SET nombre=?, correo=?, telefono=? WHERE dni=?", (nombre, correo, telefono, dni))
    db.commit()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    return jsonify(ok=True, user=user_public(user))


@app.post("/api/perfil/<dni>/password")
def change_password(dni):
    data = request.get_json(force=True) or {}
    actual = data.get("actual") or ""
    nueva = data.get("nueva") or ""
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    if user["password"] != actual:
        return jsonify(ok=False, error="La contraseña actual no es correcta."), 401
    if len(nueva) < 6:
        return jsonify(ok=False, error="La nueva contraseña debe tener al menos 6 caracteres."), 400
    db.execute("UPDATE usuarios SET password=? WHERE dni=?", (nueva, dni))
    db.commit()
    return jsonify(ok=True)


# ============================================================
# API — reclamos
# ============================================================
@app.get("/api/reclamos")
def list_reclamos():
    dni = request.args.get("dni", "").strip()
    if not dni:
        return jsonify(ok=False, error="Falta el parámetro dni."), 400
    simulado = _simular(request.args.get("simular"))
    if simulado:
        return simulado
    db = get_db()
    rows = db.execute(
        "SELECT * FROM reclamos WHERE dni = ? ORDER BY created_at DESC", (dni,)
    ).fetchall()
    return jsonify(ok=True, reclamos=[claim_public(r) for r in rows])


@app.get("/api/reclamos/<claim_id>")
def get_reclamo(claim_id):
    simulado = _simular(request.args.get("simular"))
    if simulado:
        return simulado
    db = get_db()
    row = db.execute("SELECT * FROM reclamos WHERE id = ?", (claim_id,)).fetchone()
    if not row:
        return jsonify(ok=False, codigo="no_encontrado",
                       error="No encontramos ningún reclamo con ese código."), 404
    return jsonify(ok=True, reclamo=claim_public(row, with_historial=True, db=db))


@app.get("/api/seguimiento")
def seguimiento():
    """Consulta publica por codigo + documento. Alimenta el estado 2 (vacio por busqueda)."""
    codigo = (request.args.get("codigo") or "").strip().upper()
    doc = (request.args.get("documento") or "").strip()
    simulado = _simular(request.args.get("simular"))
    if simulado:
        return simulado
    if not codigo:
        return jsonify(ok=False, codigo="falta_codigo", error="Ingresa el código de seguimiento."), 400
    if not re.fullmatch(r"REC-\d{4}-\d{5}", codigo):
        return jsonify(ok=False, codigo="formato", resultados=0,
                       error="El código debe tener el formato REC-AAAA-NNNNN. "
                             "Lo encuentras en el correo de registro o en el comprobante."), 400
    db = get_db()
    row = db.execute("SELECT * FROM reclamos WHERE id = ?", (codigo,)).fetchone()
    if not row or (doc and row["dni"] != doc):
        return jsonify(ok=True, resultados=0, reclamo=None,
                       mensaje="No encontramos ningún reclamo con ese código."), 200
    return jsonify(ok=True, resultados=1, reclamo=claim_public(row, with_historial=True, db=db))


@app.post("/api/reclamos")
def create_reclamo():
    data = request.get_json(force=True) or {}
    dni = (data.get("dni") or "").strip()
    nombre = (data.get("nombre") or "").strip()
    tipo = data.get("tipo") or ""
    descripcion = (data.get("descripcion") or "").strip()
    canal = data.get("canal") or "Correo electrónico"
    correo = (data.get("correo") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    archivos = data.get("archivos") or []

    db = get_db()
    if not db.execute("SELECT 1 FROM usuarios WHERE dni = ?", (dni,)).fetchone():
        return jsonify(ok=False, error="Debes iniciar sesión con una cuenta verificada."), 401
    if tipo not in TIPOS_RECLAMO:
        return jsonify(ok=False, error="Selecciona un tipo de reclamo válido."), 400
    if len(descripcion) < 15:
        return jsonify(ok=False, error="Describe tu reclamo con al menos 15 caracteres."), 400
    if canal == "Correo electrónico" and not valid_email(correo):
        return jsonify(ok=False, error="Ingresa un correo electrónico válido."), 400
    if canal == "Teléfono / SMS" and len(telefono) < 6:
        return jsonify(ok=False, error="Ingresa un número de teléfono válido."), 400

    count = db.execute("SELECT COUNT(*) AS c FROM reclamos").fetchone()["c"]
    claim_id = f"REC-{datetime.now().year}-{count + 1:05d}"
    created = now_iso()

    db.execute(
        "INSERT INTO reclamos (id, dni, nombre, tipo, descripcion, canal, correo, telefono, archivos, estado, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (claim_id, dni, nombre, tipo, descripcion, canal, correo, telefono, json.dumps(archivos), "Recibido", created),
    )
    db.execute(
        "INSERT INTO historial (reclamo_id, estado, fecha, nota) VALUES (?,?,?,?)",
        (claim_id, "Recibido", created, NOTAS_ESTADO["Recibido"]),
    )
    notificar(db, dni, "reclamo", f"Registramos tu reclamo {claim_id}",
              "Te avisaremos por correo en cada cambio de estado.", claim_id)
    db.commit()
    reclamo = claim_with_historial(db, claim_id)

    correo_info = intentar_enviar_correo(reclamo)

    return jsonify(ok=True, reclamo=reclamo, correo=correo_info)


@app.patch("/api/reclamos/<claim_id>/estado")
def update_estado(claim_id):
    data = request.get_json(force=True) or {}
    nuevo_estado = data.get("estado")
    if nuevo_estado not in ESTADOS:
        return jsonify(ok=False, error="Estado inválido."), 400

    db = get_db()
    row = db.execute("SELECT * FROM reclamos WHERE id = ?", (claim_id,)).fetchone()
    if not row:
        return jsonify(ok=False, error="Reclamo no encontrado."), 404

    db.execute("UPDATE reclamos SET estado = ? WHERE id = ?", (nuevo_estado, claim_id))
    db.execute(
        "INSERT INTO historial (reclamo_id, estado, fecha, nota) VALUES (?,?,?,?)",
        (claim_id, nuevo_estado, now_iso(), NOTAS_ESTADO.get(nuevo_estado, "")),
    )
    notificar(db, row["dni"], "reclamo", f"Tu reclamo {claim_id} pasó a «{nuevo_estado}»",
              NOTAS_ESTADO.get(nuevo_estado, ""), claim_id)
    db.commit()
    row = db.execute("SELECT * FROM reclamos WHERE id = ?", (claim_id,)).fetchone()
    return jsonify(ok=True, reclamo=claim_public(row, with_historial=True, db=db))


@app.get("/api/meta")
def meta():
    return jsonify(ok=True, tipos=TIPOS_RECLAMO, estados=ESTADOS,
                   emailConfigurado=EMAIL_CONFIGURADO, idiomas=IDIOMAS,
                   preferenciasDefecto=PREFS_DEFECTO, diasGracia=DIAS_GRACIA,
                   motivosBaja=MOTIVOS_BAJA)


@app.get("/api/reclamos/<claim_id>/pdf")
def descargar_pdf(claim_id):
    db = get_db()
    reclamo = claim_with_historial(db, claim_id)
    if not reclamo:
        return jsonify(ok=False, error="Reclamo no encontrado."), 404
    pdf_bytes = generar_pdf_reclamo(reclamo)
    guardar_copia_pdf(claim_id, pdf_bytes)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{claim_id}.pdf"'},
    )


@app.post("/api/reclamos/<claim_id>/enviar-correo")
def reenviar_correo(claim_id):
    db = get_db()
    reclamo = claim_with_historial(db, claim_id)
    if not reclamo:
        return jsonify(ok=False, error="Reclamo no encontrado."), 404

    data = request.get_json(silent=True) or {}
    correo_override = (data.get("correo") or "").strip()
    if correo_override:
        if not valid_email(correo_override):
            return jsonify(ok=False, error="Ingresa un correo electrónico válido."), 400
        reclamo["correo"] = correo_override

    correo_info = intentar_enviar_correo(reclamo)
    if correo_info.get("error") and not correo_info.get("enviado"):
        return jsonify(ok=False, error=correo_info["error"], correo=correo_info), 502
    return jsonify(ok=True, correo=correo_info)


# ============================================================
# API — modulo de accesibilidad (23 ajustes) e idioma
# ============================================================
@app.get("/api/accesibilidad/<dni>")
def get_accesibilidad(dni):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    return jsonify(ok=True, preferencias=leer_prefs(user), defecto=PREFS_DEFECTO)


@app.put("/api/accesibilidad/<dni>")
def set_accesibilidad(dni):
    """Guarda las preferencias en la cuenta: valen en la PC, el celular y los correos."""
    data = request.get_json(force=True) or {}
    cambios = data.get("preferencias") if isinstance(data.get("preferencias"), dict) else data
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404

    prefs = leer_prefs(user)
    for k, v in (cambios or {}).items():
        if k in PREFS_DEFECTO:
            prefs[k] = v
    if prefs.get("idioma") not in IDIOMAS:
        prefs["idioma"] = "es"
    if prefs.get("fs") not in (100, 125, 150, 200):
        prefs["fs"] = 100

    db.execute("UPDATE usuarios SET preferencias = ?, idioma = ? WHERE dni = ?",
               (json.dumps(prefs), prefs["idioma"], dni))
    db.commit()
    return jsonify(ok=True, preferencias=prefs)


@app.post("/api/accesibilidad/<dni>/restablecer")
def reset_accesibilidad(dni):
    db = get_db()
    if not db.execute("SELECT 1 FROM usuarios WHERE dni = ?", (dni,)).fetchone():
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    db.execute("UPDATE usuarios SET preferencias = ?, idioma = 'es' WHERE dni = ?",
               (json.dumps(PREFS_DEFECTO), dni))
    db.commit()
    return jsonify(ok=True, preferencias=dict(PREFS_DEFECTO))


# ============================================================
# API — notificaciones (alimentan el estado 3: vacio por historial)
# ============================================================
@app.get("/api/notificaciones")
def list_notificaciones():
    dni = (request.args.get("dni") or "").strip()
    if not dni:
        return jsonify(ok=False, error="Falta el parámetro dni."), 400
    simulado = _simular(request.args.get("simular"))
    if simulado:
        return simulado
    db = get_db()
    rows = db.execute(
        "SELECT * FROM notificaciones WHERE dni = ? ORDER BY id DESC LIMIT 60", (dni,)).fetchall()
    return jsonify(ok=True, notificaciones=[{
        "id": r["id"], "tipo": r["tipo"], "titulo": r["titulo"], "detalle": r["detalle"],
        "reclamoId": r["reclamo_id"], "leida": bool(r["leida"]), "createdAt": r["created_at"],
    } for r in rows])


@app.post("/api/notificaciones/leer")
def leer_notificaciones():
    data = request.get_json(force=True) or {}
    dni = (data.get("dni") or "").strip()
    db = get_db()
    db.execute("UPDATE notificaciones SET leida = 1 WHERE dni = ?", (dni,))
    db.commit()
    return jsonify(ok=True)


# ============================================================
# API — baja de cuenta (las seis etapas del AP3)
# ============================================================
MOTIVOS_BAJA = [
    "Ya resolví mi reclamo y no necesito la cuenta",
    "Creé la cuenta por error o tengo otra",
    "No quiero que guarden mis datos personales",
    "El portal me resultó difícil de usar",
    "Prefiero no decirlo",
]


@app.get("/api/cuenta/<dni>/resumen")
def resumen_cuenta(dni):
    """Etapa 2: que se elimina y que se conserva, con datos reales de la cuenta."""
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    total = db.execute("SELECT COUNT(*) AS c FROM reclamos WHERE dni = ?", (dni,)).fetchone()["c"]
    abiertos = db.execute(
        "SELECT id FROM reclamos WHERE dni = ? AND estado IN ('Recibido','En proceso')", (dni,)).fetchall()
    return jsonify(ok=True, motivos=MOTIVOS_BAJA, user=user_public(user),
                   reclamos=total, reclamosAbiertos=[r["id"] for r in abiertos],
                   diasGracia=DIAS_GRACIA,
                   seElimina=["Tu usuario y contraseña del portal",
                              "Tu correo y teléfono de contacto",
                              "Tus preferencias de accesibilidad",
                              "Tus notificaciones y mensajes",
                              "Las sesiones abiertas en otros equipos"],
                   seConserva=["Los reclamos que ya registraste",
                               "Las respuestas formales enviadas",
                               "Las hojas del Libro de Reclamaciones",
                               "Los comprobantes de atención",
                               "De forma anonimizada, por el plazo legal"])


@app.post("/api/cuenta/<dni>/silenciar")
def silenciar_cuenta(dni):
    """Etapa 3, alternativa 1: dejar de recibir avisos sin perder la cuenta."""
    data = request.get_json(silent=True) or {}
    activar = bool(data.get("silenciar", True))
    db = get_db()
    if not db.execute("SELECT 1 FROM usuarios WHERE dni = ?", (dni,)).fetchone():
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    db.execute("UPDATE usuarios SET notificaciones_silenciadas = ? WHERE dni = ?", (1 if activar else 0, dni))
    db.commit()
    return jsonify(ok=True, silenciadas=activar)


@app.post("/api/cuenta/<dni>/desactivar")
def desactivar_cuenta(dni):
    """Etapa 3, alternativa 2: desactivacion temporal, reversible con solo entrar."""
    db = get_db()
    if not db.execute("SELECT 1 FROM usuarios WHERE dni = ?", (dni,)).fetchone():
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    db.execute("UPDATE usuarios SET estado_cuenta = 'desactivada' WHERE dni = ?", (dni,))
    db.commit()
    return jsonify(ok=True, estadoCuenta="desactivada")


@app.post("/api/cuenta/<dni>/reactivar")
def reactivar_cuenta(dni):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    db.execute("UPDATE usuarios SET estado_cuenta = 'activa' WHERE dni = ?", (dni,))
    db.commit()
    return jsonify(ok=True, estadoCuenta="activa")


@app.get("/api/cuenta/<dni>/exportar")
def exportar_datos(dni):
    """Etapa 3, alternativa 3: llevarse una copia de los datos antes de borrar."""
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    reclamos = db.execute("SELECT * FROM reclamos WHERE dni = ? ORDER BY created_at", (dni,)).fetchall()
    export = {
        "generado": now_iso(),
        "cuenta": user_public(user),
        "reclamos": [claim_public(r, with_historial=True, db=db) for r in reclamos],
        "notificaciones": [dict(r) for r in db.execute(
            "SELECT tipo, titulo, detalle, created_at FROM notificaciones WHERE dni = ?", (dni,)).fetchall()],
    }
    cuerpo = json.dumps(export, ensure_ascii=False, indent=2)
    return Response(cuerpo, mimetype="application/json",
                    headers={"Content-Disposition": f'attachment; filename="mis-datos-{dni}.json"'})


@app.post("/api/cuenta/<dni>/baja/solicitar")
def baja_solicitar(dni):
    """Etapa 4a: envia el codigo de verificacion al correo registrado."""
    data = request.get_json(force=True) or {}
    motivo = (data.get("motivo") or "").strip()
    comentario = (data.get("comentario") or "").strip()[:300]
    confirmo = data.get("confirmaciones") or {}

    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    if not (confirmo.get("acceso") and confirmo.get("definitiva")):
        return jsonify(ok=False, error="Debes marcar las dos confirmaciones antes de continuar."), 400
    if (data.get("palabra") or "").strip().upper() != "ELIMINAR":
        return jsonify(ok=False, error="Escribe la palabra ELIMINAR para confirmar.",
                       campo="palabra"), 400

    codigo = codigo_6()
    db.execute("UPDATE usuarios SET codigo_baja = ?, codigo_baja_expira = ? WHERE dni = ?",
               (codigo, mas_horas(1), dni))
    db.commit()
    asunto = "Código para eliminar tu cuenta - Integratel Perú"
    texto = (f"Hola {user['nombre']},\n\nTu código para eliminar la cuenta es: {codigo}\n"
             "Vence en 10 minutos. Si no pediste esto, ignora el mensaje y cambia tu contraseña.")
    html = (f"<p>Hola <b>{user['nombre']}</b>,</p>"
            f"<p>Tu código para eliminar la cuenta es: <b style='font-size:22px;letter-spacing:4px'>{codigo}</b></p>"
            "<p>Vence en 10 minutos. Si no pediste esto, ignora el mensaje y cambia tu contraseña.</p>")
    ok, simulado, error = enviar_correo_simple(user["correo"], asunto, texto, html,
                                               etiqueta="codigo_baja_" + dni)
    return jsonify(ok=True, motivo=motivo, comentario=comentario,
                   correo={"enviado": bool(ok), "simulado": bool(simulado), "error": error,
                           "destinatario": user["correo"]})


@app.post("/api/cuenta/<dni>/baja/confirmar")
def baja_confirmar(dni):
    """Etapas 4b, 5 y 6: verifica el codigo, inicia el periodo de gracia y envia el comprobante."""
    data = request.get_json(force=True) or {}
    codigo = (data.get("codigo") or "").strip()
    motivo = (data.get("motivo") or "").strip()
    comentario = (data.get("comentario") or "").strip()[:300]

    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    if not codigo or len(codigo) != 6:
        return jsonify(ok=False, error="El código debe tener 6 dígitos.", campo="codigo"), 400
    if codigo != (user.get("codigo_baja") or ""):
        return jsonify(ok=False, error="El código no coincide con el que enviamos a tu correo.",
                       campo="codigo"), 400
    if vencido(user.get("codigo_baja_expira")):
        return jsonify(ok=False, error="El código venció. Pide uno nuevo.", campo="codigo"), 400

    ahora = datetime.now(timezone.utc).astimezone()
    efectiva = (ahora + timedelta(days=DIAS_GRACIA)).isoformat()
    db.execute(
        """UPDATE usuarios SET estado_cuenta = 'eliminada', baja_solicitada_at = ?,
           baja_efectiva_at = ?, codigo_baja = NULL, codigo_baja_expira = NULL WHERE dni = ?""",
        (ahora.isoformat(), efectiva, dni))
    db.execute(
        "INSERT INTO bajas_cuenta (dni, motivo, comentario, solicitada_at, efectiva_at) VALUES (?,?,?,?,?)",
        (dni, motivo, comentario, ahora.isoformat(), efectiva))
    db.commit()

    abiertos = [r["id"] for r in db.execute(
        "SELECT id FROM reclamos WHERE dni = ? AND estado IN ('Recibido','En proceso')", (dni,)).fetchall()]
    enlace = f"{PLANTILLAS.BASE_URL}/sistema/cuenta-eliminada.html?dni={dni}&restaurar=1"
    correo = enviar_plantilla("eliminacion", user["correo"], user["nombre"],
                              fecha_larga(ahora.isoformat()), fecha_larga(efectiva),
                              enlace, abiertos, etiqueta="eliminacion_" + dni)
    return jsonify(ok=True, bajaSolicitadaAt=ahora.isoformat(), bajaEfectivaAt=efectiva,
                   diasGracia=DIAS_GRACIA, reclamosVigentes=abiertos, correo=correo)


@app.post("/api/cuenta/<dni>/baja/restaurar")
def baja_restaurar(dni):
    """Deshace la baja dentro del periodo de gracia."""
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    if (user.get("estado_cuenta") or "activa") != "eliminada":
        return jsonify(ok=True, estadoCuenta=user.get("estado_cuenta") or "activa", yaActiva=True)
    if vencido(user.get("baja_efectiva_at")):
        return jsonify(ok=False, error="El plazo de 30 días ya venció: la eliminación es definitiva."), 410

    db.execute("""UPDATE usuarios SET estado_cuenta = 'activa', baja_solicitada_at = NULL,
                  baja_efectiva_at = NULL WHERE dni = ?""", (dni,))
    db.execute("UPDATE bajas_cuenta SET restaurada_at = ? WHERE dni = ? AND restaurada_at IS NULL",
               (now_iso(), dni))
    notificar(db, dni, "cuenta", "Recuperaste tu cuenta",
              "Tu historial completo sigue disponible.")
    db.commit()
    return jsonify(ok=True, estadoCuenta="activa")


@app.get("/api/cuenta/<dni>/estado")
def estado_cuenta(dni):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE dni = ?", (dni,)).fetchone()
    if not user:
        return jsonify(ok=False, error="Usuario no encontrado."), 404
    return jsonify(ok=True, user=user_public(user))


# ============================================================
# Archivos estáticos (sitio institucional + sistema)
# ============================================================
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


if __name__ == "__main__":
    init_db()
    print(f"Base de datos MySQL: {MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
    print("Servidor disponible en: http://localhost:5000")
    # use_reloader=False: el reinicio automatico se cuelga al ejecutar con F5 (depurador) y deja el puerto 5000 ocupado sin responder
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False, threaded=True)

# -*- coding: utf-8 -*-
"""Recorre todos los flujos nuevos del AP3 contra la API."""
import _test_harness as H
import json, re, os
c = H.cliente
fallos = []

def chk(nombre, cond, extra=""):
    print(("  OK  " if cond else "  FALLA ") + nombre + (("  -> " + str(extra)[:140]) if (not cond and extra) else ""))
    if not cond: fallos.append(nombre)

def j(r):
    try: return r.get_json() or {}
    except Exception: return {}

print("\n=== 1. REGISTRO + VERIFICACIÓN + BIENVENIDA ===")
r = c.post("/api/registro", json={"nombre":"Alberto Ramírez","dni":"70123456",
    "correo":"alberto@correo.com","telefono":"987654321","password":"Clave1234","idioma":"es"})
d = j(r); chk("registro crea la cuenta", r.status_code==200 and d.get("ok"), d)
chk("cuenta nace sin verificar", d.get("user",{}).get("correoVerificado") is False, d.get("user"))
chk("correo 1 de verificación generado", d.get("correoVerificacion",{}).get("simulado") or d.get("correoVerificacion",{}).get("enviado"), d.get("correoVerificacion"))

# recuperar el código de la BD para simular el clic en el enlace
db = H.SQLiteConn(); cod = db.execute("SELECT codigo_verificacion FROM usuarios WHERE dni='70123456'").fetchone()["codigo_verificacion"]; db.close()
chk("código de 6 dígitos", bool(re.fullmatch(r"\d{6}", cod or "")), cod)
r = c.get(f"/api/verificar?dni=70123456&codigo={cod}")
chk("verificar redirige con ok", r.status_code==302 and "verificacion=ok" in r.headers.get("Location",""), r.headers.get("Location"))
r = c.get("/api/cuenta/70123456/estado"); d=j(r)
chk("cuenta queda verificada", d.get("user",{}).get("correoVerificado") is True)
chk("correo 2 (bienvenida) enviado", any("bienvenida" in f for f in os.listdir("sent_emails")) if os.path.isdir("sent_emails") else False)

print("\n=== 2. MÓDULO DE ACCESIBILIDAD (23 ajustes) ===")
r = c.get("/api/accesibilidad/70123456"); d=j(r)
chk("lee las 23 preferencias", len(d.get("preferencias",{}))==23, len(d.get("preferencias",{})))
r = c.put("/api/accesibilidad/70123456", json={"preferencias":{"fs":150,"contraste":"alto","tema":"noche","idioma":"qu","voz":True,"movimiento":True}})
d=j(r); p=d.get("preferencias",{})
chk("guarda fs=150", p.get("fs")==150, p.get("fs"))
chk("guarda tema=noche", p.get("tema")=="noche")
chk("guarda idioma=qu", p.get("idioma")=="qu")
r = c.get("/api/cuenta/70123456/estado"); d=j(r)
chk("el idioma viaja en la cuenta", d.get("user",{}).get("idioma")=="qu", d.get("user",{}).get("idioma"))
r = c.put("/api/accesibilidad/70123456", json={"preferencias":{"fs":999,"idioma":"xx"}}); p=j(r).get("preferencias",{})
chk("rechaza valores inválidos", p.get("fs")==100 and p.get("idioma")=="es", p)
r = c.post("/api/accesibilidad/70123456/restablecer"); p=j(r).get("preferencias",{})
chk("restablece a los valores por defecto", p.get("fs")==100 and p.get("tema")=="auto")

print("\n=== 3. RECLAMO + NOTIFICACIONES ===")
r = c.post("/api/reclamos", json={"dni":"70123456","nombre":"Alberto Ramírez",
    "tipo":"Facturación y cobros","descripcion":"Cobro duplicado del mes de setiembre en mi recibo.",
    "canal":"Correo electrónico","correo":"alberto@correo.com"})
d=j(r); rid=d.get("reclamo",{}).get("id"); chk("crea el reclamo", bool(rid), d.get("error"))
r = c.get("/api/notificaciones?dni=70123456"); n=j(r).get("notificaciones",[])
chk("genera notificación del reclamo", any(x["tipo"]=="reclamo" for x in n), [x["titulo"] for x in n])
r = c.patch(f"/api/reclamos/{rid}/estado", json={"estado":"En proceso"})
chk("cambia el estado", j(r).get("ok"))
n = j(c.get("/api/notificaciones?dni=70123456")).get("notificaciones",[])
chk("notifica el cambio de estado", any("En proceso" in x["titulo"] for x in n))
chk("marcar leídas", j(c.post("/api/notificaciones/leer", json={"dni":"70123456"})).get("ok"))

print("\n=== 4. SEGUIMIENTO PÚBLICO (estado 2) ===")
r = c.get(f"/api/seguimiento?codigo={rid}"); d=j(r)
chk("encuentra por código", d.get("resultados")==1, d)
r = c.get("/api/seguimiento?codigo=REC-2026-09999"); d=j(r)
chk("devuelve 0 resultados, no error", d.get("ok") and d.get("resultados")==0, d)
r = c.get("/api/seguimiento?codigo=ABC123"); d=j(r)
chk("valida el formato con mensaje útil", r.status_code==400 and "REC-AAAA" in (d.get("error") or ""), d.get("error"))

print("\n=== 5. SIMULACIÓN DE ESTADOS ===")
for sim, esperado, codigo in [("vacio",200,None),("error-conexion",503,"error_conexion"),
                              ("error-sistema",500,"error_sistema"),("sin-permisos",403,"sin_permisos")]:
    r = c.get(f"/api/reclamos?dni=70123456&simular={sim}"); d=j(r)
    chk(f"simular={sim}", r.status_code==esperado and (codigo is None or d.get("codigo")==codigo), (r.status_code, d.get("codigo")))
r = c.get(f"/api/reclamos/{rid}?simular=no-disponible")
chk("simular=no-disponible", r.status_code==410 and j(r).get("codigo")=="no_disponible")
r = c.get("/api/reclamos/REC-2026-00999")
chk("404 con mensaje del usuario", r.status_code==404 and j(r).get("codigo")=="no_encontrado")

print("\n=== 6. ALTERNATIVAS A LA BAJA (etapa 3) ===")
r = c.get("/api/cuenta/70123456/resumen"); d=j(r)
chk("resumen trae motivos y listas", len(d.get("motivos",[]))==5 and len(d.get("seElimina",[]))==5 and len(d.get("seConserva",[]))==5)
chk("resumen cuenta los reclamos", d.get("reclamos")>=1, d.get("reclamos"))
chk("silenciar avisos", j(c.post("/api/cuenta/70123456/silenciar", json={"silenciar":True})).get("silenciadas") is True)
chk("desactivar temporalmente", j(c.post("/api/cuenta/70123456/desactivar")).get("estadoCuenta")=="desactivada")
r = c.post("/api/login", json={"dni":"70123456","password":"Clave1234"}); d=j(r)
chk("login bloquea cuenta desactivada", r.status_code==403 and d.get("codigo")=="cuenta_desactivada", d)
chk("reactivar", j(c.post("/api/cuenta/70123456/reactivar")).get("estadoCuenta")=="activa")
chk("login vuelve a funcionar", j(c.post("/api/login", json={"dni":"70123456","password":"Clave1234"})).get("ok"))
r = c.get("/api/cuenta/70123456/exportar")
chk("exporta los datos en JSON", r.status_code==200 and b"reclamos" in r.data, r.status_code)
c.post("/api/cuenta/70123456/silenciar", json={"silenciar":False})

print("\n=== 7. BAJA DE CUENTA (etapas 4, 5 y 6) ===")
r = c.post("/api/cuenta/70123456/baja/solicitar", json={"motivo":"Prefiero no decirlo","confirmaciones":{"acceso":True},"palabra":"ELIMINAR"})
chk("exige las dos confirmaciones", r.status_code==400, j(r).get("error"))
r = c.post("/api/cuenta/70123456/baja/solicitar", json={"motivo":"x","confirmaciones":{"acceso":True,"definitiva":True},"palabra":"BORRAR"})
chk("exige la palabra ELIMINAR", r.status_code==400 and j(r).get("campo")=="palabra", j(r).get("error"))
r = c.post("/api/cuenta/70123456/baja/solicitar", json={"motivo":"Prefiero no decirlo","confirmaciones":{"acceso":True,"definitiva":True},"palabra":"eliminar"})
d=j(r); chk("envía el código al correo", d.get("ok") and d.get("correo",{}).get("simulado"), d)
db = H.SQLiteConn(); cb = db.execute("SELECT codigo_baja FROM usuarios WHERE dni='70123456'").fetchone()["codigo_baja"]; db.close()
r = c.post("/api/cuenta/70123456/baja/confirmar", json={"codigo":"000000"})
chk("rechaza código incorrecto", r.status_code==400 and j(r).get("campo")=="codigo")
r = c.post("/api/cuenta/70123456/baja/confirmar", json={"codigo":cb,"motivo":"Prefiero no decirlo"})
d=j(r); chk("confirma la baja", d.get("ok") and d.get("diasGracia")==30, d)
chk("deja los reclamos vigentes", isinstance(d.get("reclamosVigentes"),list) and len(d["reclamosVigentes"])>=1, d.get("reclamosVigentes"))
chk("correo 4 (eliminación) enviado", d.get("correo",{}).get("simulado") or d.get("correo",{}).get("enviado"), d.get("correo"))
r = c.post("/api/login", json={"dni":"70123456","password":"Clave1234"}); d=j(r)
chk("login bloquea cuenta eliminada", r.status_code==403 and d.get("codigo")=="cuenta_eliminada", d)
chk("el mensaje indica la fecha límite", "recuperarla hasta el" in (d.get("error") or ""), d.get("error"))
r = c.post("/api/cuenta/70123456/baja/restaurar"); chk("restaura dentro del plazo", j(r).get("estadoCuenta")=="activa", j(r))
chk("login funciona tras restaurar", j(c.post("/api/login", json={"dni":"70123456","password":"Clave1234"})).get("ok"))
chk("el reclamo sobrevivió a la baja", len(j(c.get("/api/reclamos?dni=70123456")).get("reclamos",[]))>=1)

print("\n=== 8. RECUPERACIÓN DE CONTRASEÑA (correo 3) ===")
r = c.post("/api/recuperar", json={"identificador":"alberto@correo.com"})
chk("responde siempre igual", j(r).get("ok"))
chk("correo 3 generado", any("recuperar" in f for f in os.listdir("sent_emails")))
r = c.post("/api/recuperar", json={"identificador":"noexiste@x.com"})
chk("no revela si la cuenta existe", j(r).get("ok"))

print("\n=== 9. PDF ===")
r = c.get(f"/api/reclamos/{rid}/pdf")
chk("genera el PDF", r.status_code==200 and r.data[:4]==b"%PDF", r.status_code)

print("\n" + "="*52)
print("FALLAS: %d" % len(fallos))
for f in fallos: print("   -", f)
print("="*52)

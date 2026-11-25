# Arquitectura

El sistema tiene dos productos conectados: el **sitio institucional** (Inicio, Nosotros, Servicios, Contacto) y el **Sistema de Gestión de Reclamos** (14 pantallas en `sistema/`).

```
Navegador (HTML + CSS + JS)  --JSON/REST-->  Flask (backend/app.py)  -->  MySQL
  reclamos.js  a11y.js  i18n.js              pdf_utils.py (fpdf2)
  asistente.js (voz + agente)                email_utils.py (SMTP)
```

- **Frontend:** HTML, CSS y JavaScript sin frameworks, con un Design System de tokens y tres temas (claro, oscuro y alto contraste).
- **Backend:** Flask expone 30 rutas REST. Toda la información vive en MySQL; el navegador solo recuerda quién inició sesión.
- **Servicios:** comprobante PDF con fpdf2, correos HTML responsivos por SMTP (modo simulado si no hay credenciales) y Web Speech API para voz.
- **Tablas:** `usuarios`, `reclamos`, `historial`, `notificaciones` y `bajas_cuenta`.

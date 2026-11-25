# API REST del sistema

Todas las rutas responden JSON con la forma `{ "ok": true, ... }` o `{ "ok": false, "error": "..." }`.

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/registro` |  |
| GET | `/api/verificar` | Confirma la direccion de correo y dispara el correo 2 (bienvenida). |
| POST | `/api/reenviar-verificacion` |  |
| POST | `/api/login` |  |
| POST | `/api/recuperar` | Recuperación de contraseña. Siempre responde igual para no revelar si la cuenta existe. |
| GET | `/api/perfil/<dni>` |  |
| PATCH | `/api/perfil/<dni>` |  |
| POST | `/api/perfil/<dni>/password` |  |
| GET | `/api/reclamos` |  |
| GET | `/api/reclamos/<claim_id>` |  |
| GET | `/api/seguimiento` | Consulta publica por codigo + documento. Alimenta el estado 2 (vacio por busqueda). |
| POST | `/api/reclamos` |  |
| PATCH | `/api/reclamos/<claim_id>/estado` |  |
| GET | `/api/meta` |  |
| GET | `/api/reclamos/<claim_id>/pdf` |  |
| POST | `/api/reclamos/<claim_id>/enviar-correo` |  |
| GET | `/api/accesibilidad/<dni>` |  |
| PUT | `/api/accesibilidad/<dni>` | Guarda las preferencias en la cuenta: valen en la PC, el celular y los correos. |
| POST | `/api/accesibilidad/<dni>/restablecer` |  |
| GET | `/api/notificaciones` |  |
| POST | `/api/notificaciones/leer` |  |
| GET | `/api/cuenta/<dni>/resumen` | Etapa 2: que se elimina y que se conserva, con datos reales de la cuenta. |
| POST | `/api/cuenta/<dni>/silenciar` | Etapa 3, alternativa 1: dejar de recibir avisos sin perder la cuenta. |
| POST | `/api/cuenta/<dni>/desactivar` | Etapa 3, alternativa 2: desactivacion temporal, reversible con solo entrar. |
| POST | `/api/cuenta/<dni>/reactivar` |  |
| GET | `/api/cuenta/<dni>/exportar` | Etapa 3, alternativa 3: llevarse una copia de los datos antes de borrar. |
| POST | `/api/cuenta/<dni>/baja/solicitar` | Etapa 4a: envia el codigo de verificacion al correo registrado. |
| POST | `/api/cuenta/<dni>/baja/confirmar` | Etapas 4b, 5 y 6: verifica el codigo, inicia el periodo de gracia y envia el comprobante. |
| POST | `/api/cuenta/<dni>/baja/restaurar` | Deshace la baja dentro del periodo de gracia. |
| GET | `/api/cuenta/<dni>/estado` |  |

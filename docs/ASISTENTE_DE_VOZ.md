# Asistente de voz con agente

Se abre con el botón del micrófono o con `Alt + Q` en cualquier pantalla del sistema con sesión iniciada.

## Flujo
Entrada (voz o texto), normalización y detección de intención (NLU), decisión del agente, herramientas (API REST) y respuesta en texto y voz.

## Intenciones
| Intención | Ejemplo | Acción |
|---|---|---|
| Registrar | «Registra un reclamo: me cobraron el recibo doble» | Clasifica el tipo, pide confirmación y llama a `POST /api/reclamos` |
| Estado | «Estado de mi último reclamo» o «Estado de REC-2026-00015» | Lee el estado y el último movimiento |
| Resumen | «¿Cuántos reclamos tengo?» | Cuenta los reclamos por estado |
| Navegar | «Abre notificaciones» | Abre la pantalla |
| Ayuda o salir | «Ayuda» o «Cerrar sesión» | Lista comandos o cierra la sesión |

## Límites
La comprensión es por reglas y palabras clave (sin modelo de lenguaje externo). El reconocimiento de voz lo hace el navegador (Chrome o Edge) y requiere permiso de micrófono; también se puede escribir.

# Integratel Perú — Prototipo Web (Página Institucional + Sistema de Gestión de Reclamos)

Prototipo funcional: frontend en HTML/CSS/JavaScript puro (sin frameworks) + backend en **Flask** con una **base de datos MySQL real**, desarrollado para el curso **Herramientas de Prototipado (UTP)**.

## Cómo ejecutarlo en Antigravity (o cualquier editor)

Este proyecto ya no funciona abriendo el `.html` directo ni con Live Server: el Sistema de Gestión de Reclamos necesita el servidor Flask corriendo para leer/escribir en la base de datos.

1. Abre esta carpeta (`integratel-web`) como proyecto en Antigravity.
2. Instala las dependencias del backend (una sola vez):
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Inicia el servidor:
   ```bash
   python backend/app.py
   ```
   La primera vez que corre, crea automáticamente la base `integratel_reclamos` en MySQL con sus cinco tablas y una cuenta + reclamos de ejemplo. Si ya existía de una versión anterior, agrega solo las columnas que falten, sin borrar nada.
4. Abre `http://localhost:5000` en el navegador. Flask sirve ahí mismo tanto el sitio institucional como el sistema de reclamos (mismo origen, sin configuración adicional).
5. Navega el sitio institucional desde `index.html`, y entra al sistema de reclamos desde el botón **"Libro de Reclamaciones"**.

Para detener el servidor, `Ctrl + C` en la terminal donde corre.

## Requisitos

- Python 3.10 o superior y MySQL 8 (para ejecutar el sistema completo).
- Navegador Chrome o Edge para la entrada por voz del asistente.
- Node.js 18 o superior solo para las pruebas del asistente (`npm test`).

## Estructura del proyecto

```
integratel-web/
├── index.html          Página de inicio institucional
├── nosotros.html        Historia, misión/visión, equipo
├── servicios.html        Catálogo de servicios
├── contacto.html         Formulario de contacto + FAQ
├── ui-kit.html           Catálogo de componentes del design system
├── sistema/               Sistema de Gestión de Reclamos (app)
│   ├── index.html          Identificación (DNI / N° contrato)
│   ├── registro.html        Alta de cuenta + verificación por correo
│   ├── recuperar.html        Recuperar contraseña
│   ├── nuevo-reclamo.html     Formulario de registro de reclamo
│   ├── confirmacion.html       Pantalla de éxito con N° de ticket
│   ├── mis-reclamos.html        Dashboard con KPIs, filtros y búsqueda
│   ├── detalle.html              Seguimiento con línea de tiempo (stepper)
│   ├── seguimiento.html           Consulta pública por código, sin iniciar sesión
│   ├── notificaciones.html         Bandeja de avisos de cambio de estado
│   ├── accesibilidad.html           Centro de accesibilidad: los 23 ajustes
│   ├── estados.html                  Catálogo vivo de los 10 estados de pantalla
│   ├── eliminar-cuenta.html           Baja de cuenta en tres pasos
│   ├── cuenta-eliminada.html           Periodo de gracia de 30 días
│   └── perfil.html                      Datos de contacto, mis datos y zona de riesgo
├── assets/
│   ├── css/style.css        Design system: tokens, tres temas, componentes
│   ├── js/main.js             Nav, animaciones, formulario de contacto
│   ├── js/reclamos.js          Cliente de la API (fetch) — habla con el backend
│   ├── js/app-shell.js          Sidebar móvil + sesión compartida
│   ├── js/a11y.js                Motor de accesibilidad (panel, atajos, voz, foco)
│   ├── js/asistente.js            Asistente de voz con agente de IA (Proyecto Final)
│   ├── js/i18n.js                 Interfaz en español, inglés, quechua y aymara
│   └── js/estados.js               Los 10 estados de pantalla, como componentes
└── backend/
    ├── app.py                 Servidor Flask: API REST + base de datos
    ├── email_templates.py       Los 4 correos responsivos (HTML + texto plano)
    ├── pdf_utils.py              Genera el comprobante en PDF de cada reclamo
    ├── email_utils.py             Envía (o simula) el correo con el PDF adjunto
    ├── migracion_ap3.sql           La migración del AP3, para revisarla en Workbench
    ├── crear_usuario_mysql.sql      Crea la base y el usuario de la aplicación
    ├── requirements.txt              Dependencias Python (Flask + PyMySQL + fpdf2)
    ├── pdfs/                          Copia en PDF de cada reclamo (se genera sola)
    └── sent_emails/                    Copias .eml de los correos en modo simulado
```

## Cómo funciona el Sistema de Reclamos (con base de datos real)

Todo lo que antes vivía en el `localStorage` del navegador ahora se guarda en **MySQL** (base `integratel_reclamos`), gestionada por el servidor Flask (`backend/app.py`) a través de PyMySQL. El navegador ya no guarda los reclamos ni las cuentas — solo recuerda, mientras la pestaña está abierta, **quién inició sesión** (para no pedir la contraseña en cada clic); todo lo demás se consulta al servidor.

**Tablas de la base de datos:**
- `usuarios` — datos de la cuenta, más las doce columnas que agregó el AP3: `preferencias` (los 23 ajustes de accesibilidad en JSON), `idioma`, `estado_cuenta`, `correo_verificado`, los códigos de verificación y de baja con sus vencimientos, las fechas del periodo de gracia, `notificaciones_silenciadas` y `ultimo_acceso`
- `reclamos` (id/ticket, dni, tipo, descripción, canal, correo, telefono, archivos, estado, created_at)
- `historial` (reclamo_id, estado, fecha, nota) — una fila por cada cambio de estado
- `notificaciones` (dni, tipo, titulo, detalle, reclamo_id, leida, created_at) — alimenta la bandeja de avisos
- `bajas_cuenta` (dni, motivo, comentario, solicitada_at, efectiva_at, restaurada_at) — una fila por cada baja, se conserva aunque la cuenta se restaure

La migración completa está en `backend/migracion_ap3.sql`, comentada línea por línea, por si quieres revisarla en MySQL Workbench. No hace falta ejecutarla: `app.py` la aplica sola al arrancar y solo agrega lo que falte.

**Endpoints de la API** (`http://localhost:5000/api/...`):
| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/api/registro` | Crea una cuenta nueva |
| POST | `/api/login` | Verifica DNI + contraseña contra la base de datos |
| GET / PATCH | `/api/perfil/<dni>` | Consulta o actualiza nombre/correo/teléfono |
| POST | `/api/perfil/<dni>/password` | Cambia la contraseña |
| GET | `/api/reclamos?dni=...` | Lista los reclamos de un usuario |
| POST | `/api/reclamos` | Registra un reclamo nuevo (genera el ticket) |
| GET | `/api/reclamos/<id>` | Detalle de un reclamo + su historial completo |
| PATCH | `/api/reclamos/<id>/estado` | Cambia el estado: `En proceso`, `Atendido` o `Improcedente` |
| GET | `/api/reclamos/<id>/pdf` | Genera y descarga el comprobante en PDF (siempre con los datos más recientes) |
| POST | `/api/reclamos/<id>/enviar-correo` | (Re)envía el PDF al correo del solicitante, o a uno alternativo en el body |
| POST | `/api/recuperar` | Recuperación de contraseña: envía (o simula) un correo con instrucciones; responde igual exista o no la cuenta |
| GET | `/api/verificar?dni=&codigo=` | Confirma el correo desde el enlace del correo 1 y dispara el de bienvenida |
| POST | `/api/reenviar-verificacion` | Vuelve a enviar el enlace de confirmación |
| GET / PUT | `/api/accesibilidad/<dni>` | Lee o guarda los 23 ajustes de accesibilidad |
| POST | `/api/accesibilidad/<dni>/restablecer` | Vuelve a los valores por defecto |
| GET | `/api/notificaciones?dni=...` | Bandeja de avisos de la persona |
| POST | `/api/notificaciones/leer` | Marca todos los avisos como leídos |
| GET | `/api/seguimiento?codigo=&documento=` | Consulta pública por código, sin iniciar sesión |
| GET | `/api/cuenta/<dni>/resumen` | Datos para la pantalla de baja: motivos, qué se elimina, qué se conserva |
| GET | `/api/cuenta/<dni>/estado` | Estado de la cuenta y fecha límite del periodo de gracia |
| GET | `/api/cuenta/<dni>/exportar` | Descarga todos los datos de la persona en un `.json` |
| POST | `/api/cuenta/<dni>/silenciar` | Alternativa 1: dejar de recibir correos |
| POST | `/api/cuenta/<dni>/desactivar` · `/reactivar` | Alternativa 2: desactivar la cuenta y volver a activarla |
| POST | `/api/cuenta/<dni>/baja/solicitar` | Paso 3 de la baja: envía el código de 6 dígitos |
| POST | `/api/cuenta/<dni>/baja/confirmar` | Verifica el código y arranca el periodo de gracia de 30 días |
| POST | `/api/cuenta/<dni>/baja/restaurar` | Recupera la cuenta dentro del plazo |
| GET | `/api/meta` | Constantes del sistema: estados, idiomas, motivos de baja, ajustes por defecto |

Cualquier endpoint de lectura acepta `?simular=` para provocar los estados 4, 5, 6, 8 y 9 sin tocar la base de datos.

**Flujo funcional:**
- **Registro y acceso con cuenta verificada**: para reclamar hay que registrarse (nombre, DNI, correo, teléfono, contraseña) o iniciar sesión — el servidor valida contra la base de datos, así que un DNI inventado es rechazado. Cuenta demo: `71234567` / `Demo1234` (con 3 reclamos de ejemplo ya cargados en la base de datos).
- **Nuevo reclamo**: nombre y DNI se toman de la cuenta verificada (no se pueden escribir a mano). Se exige correo o teléfono según el canal de respuesta elegido. Al enviarlo, el servidor genera el ticket (`REC-2026-000XX`), lo guarda en `reclamos` + una primera fila en `historial`, **genera automáticamente el PDF** (se guarda en `backend/pdfs/<ticket>.pdf`) y **lo envía por correo** al solicitante. La pantalla de confirmación muestra el resultado de ese envío y permite reintentarlo o descargar el PDF manualmente.
- **Mis reclamos**: consulta en vivo a `GET /api/reclamos?dni=...`; KPIs, filtros (incluye **Improcedente**) y buscador sobre esos datos.
- **Detalle y actualizaciones de estado**: la línea de tiempo se arma leyendo `historial` desde la base de datos. Un panel de "actualización" (pensado para simular al área responsable en la sustentación) permite marcar el reclamo como **En proceso**, **Atendido** o **Improcedente** — cada cambio queda registrado permanentemente en `historial` con fecha y nota, y es visible para cualquiera que abra ese mismo reclamo (incluso desde otra sesión o dispositivo, porque ya no es local a un navegador). Desde ahí también se puede **descargar el PDF actualizado** o **reenviarlo por correo** en cualquier momento.
- **Perfil**: lee y actualiza el registro real en `usuarios`; el cambio de contraseña valida la actual contra la base de datos antes de aceptarla.

### Comprobante en PDF y envío por correo

Cada reclamo puede descargarse como PDF (botón "Descargar PDF" en la confirmación y en el detalle) con el ticket, los datos del solicitante, la descripción y el historial completo de estados — se genera al vuelo con los datos actuales de la base de datos, y además se guarda una copia en `backend/pdfs/<ticket>.pdf`.

Por defecto, **no hay ningún servidor de correo configurado**, así que el envío se simula: el mensaje completo (con el PDF adjunto) se guarda como archivo `.eml` en `backend/sent_emails/`, y la interfaz lo deja claro ("envío en modo demo"). Puedes abrir esos `.eml` con Outlook, Thunderbird o el propio explorador de Windows para mostrarle al docente que el correo "se generó" con el adjunto correcto.

**Para que el envío sea 100% real** (por ejemplo con una cuenta de Gmail), define estas variables de entorno antes de iniciar el servidor:

```bash
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=465
set SMTP_USER=tu_correo@gmail.com
set SMTP_PASS=tu_contraseña_de_aplicacion
set SMTP_FROM=tu_correo@gmail.com
python backend/app.py
```

(En Gmail necesitas generar una "contraseña de aplicación" en la configuración de seguridad de tu cuenta — no funciona con tu contraseña normal). Con esas variables definidas, `emailConfigurado` pasa a `true` y los correos salen de verdad; sin ellas, el sistema sigue funcionando igual mostrando el modo simulado, sin errores.

## Accesibilidad (AP3)

Todo el portal cumple **WCAG 2.1 nivel AA** sin activar nada, y el módulo de accesibilidad lo adapta a quien lo usa. Los ajustes se guardan en la cuenta (columna `preferencias` de `usuarios`), así que siguen a la persona en cualquier equipo donde inicie sesión; mientras tanto, una copia en `localStorage` hace que la página se pinte bien desde el primer instante, sin parpadeo.

### Dónde se usa

- **Botón flotante** abajo a la derecha, en todas las pantallas: abre un panel con once ajustes rápidos.
- **Barra superior**: idioma, accesibilidad y día/noche, siempre a la vista.
- **`sistema/accesibilidad.html`**: el centro completo, con los 23 ajustes repartidos en cuatro grupos (visual, auditivo, navegación y teclado, idioma y lectura fácil), vista previa en vivo y el resumen de conformidad.
- **Atajos de teclado**: `Alt + A` abre el panel, `Alt + D` cambia día/noche, `Alt + V` lee la página en voz alta, `Alt + N` detiene la voz, `Alt + S` salta al contenido y `Alt + L` abre el cuadro de Lengua de Señas Peruana.

### Los 23 ajustes

| Grupo | Ajustes |
|---|---|
| Visual (8) | Tamaño del texto (100–200 %), nivel de contraste (normal · alto · invertido), tema (día · noche · automático), tipografía de alta legibilidad, espaciado del texto, resaltar enlaces, reducir movimiento, guía de lectura y cursor grande |
| Auditivo (6) | Lectura por voz, velocidad de la voz, subtítulos, transcripción, intérprete de Lengua de Señas Peruana, alertas visuales |
| Navegación y teclado (5) | Foco visible reforzado, enlace «saltar al contenido», atajos de teclado, tiempo de sesión (20 · 40 min · sin límite), confirmar acciones irreversibles |
| Idioma y lectura fácil (4) | Idioma de la interfaz, modo lectura fácil, glosario de términos, traducción asistida |

### Tres temas, uno solo activo

Los colores son variables CSS (`--ink`, `--surface`, `--cyan-text`…) que se redefinen por tema, no una inversión automática: **día**, **noche** y **alto contraste** (negro, blanco y amarillo). El modo automático sigue a `prefers-color-scheme` del sistema operativo. Cada par de colores que se usa en la interfaz pasa 4.5:1 en los tres temas; eso se verifica recorriendo las 19 páginas con un navegador real y midiendo el contraste calculado de cada texto contra su fondo.

Los cuatro pares que venían del AP2 y no llegaban a AA se corrigieron manteniendo el tono de marca:

| Elemento | Antes | Después | Contraste |
|---|---|---|---|
| Acento cian sobre blanco | `#0093B0` | `#00748C` | 3.25:1 → 4.86:1 |
| Estado «Atendido» | `#1E9E64` | `#14754A` | 3.11:1 → 5.19:1 |
| Estado «Recibido» | `#C98A0A` | `#8A5D05` | 2.75:1 → 5.36:1 |
| Estado «Improcedente» | `#C73A3A` | `#BC3232` | 4.42:1 → 4.97:1 |
| Texto del botón principal | `#FFFFFF` sobre cian | `#06202B` sobre cian | 2.46:1 → 6.82:1 |

### Idiomas

La interfaz está en **español, inglés, quechua (runasimi) y aymara**. El cambio es inmediato, sin recargar, y actualiza el atributo `lang` del documento para que el lector de pantalla cambie de pronunciación. El idioma elegido se guarda en la cuenta y es el que se usa en los correos.

## Los diez estados de pantalla

Cada pantalla que depende de datos tiene definidos sus diez estados, y todos cumplen las mismas cuatro condiciones: señal visual, mensaje en el lenguaje de la persona, al menos una acción de salida y la navegación principal siempre visible. Viven en `assets/js/estados.js` como componentes reutilizables.

| # | Estado | Dónde se ve |
|---|---|---|
| 1 | Vacío inicial | Mis reclamos, cuando la cuenta todavía no tiene ninguno |
| 2 | Vacío por búsqueda | Seguimiento y el buscador de Mis reclamos |
| 3 | Vacío por historial | Notificaciones |
| 4 | Carga | Toda petición: esqueleto con la forma real del contenido, no un spinner |
| 5 | Error de conexión | Sin red: el texto escrito **no se pierde**, queda guardado como borrador |
| 6 | Error del sistema | Falla del servidor, con código de incidente para soporte |
| 7 | Error de validación | Resumen al inicio del formulario, que recibe el foco, y mensaje en texto junto a cada campo |
| 8 | Contenido no disponible | Reclamo archivado o código inexistente |
| 9 | Sin permisos / sesión vencida | Al vencer el tiempo de inactividad que la persona eligió |
| 10 | Éxito | Reclamo registrado, ajustes guardados, baja confirmada |

`sistema/estados.html` los muestra los diez uno por uno, con el código que los dibuja y los criterios WCAG que atiende cada uno. Los que dependen del servidor se pueden provocar de verdad añadiendo `?simular=` a la dirección, sin tocar la base de datos:

```
/sistema/mis-reclamos.html?simular=lento            esqueleto de carga (2,5 s)
/sistema/mis-reclamos.html?simular=vacio            vacío inicial
/sistema/mis-reclamos.html?simular=error-conexion   error de conexión
/sistema/mis-reclamos.html?simular=error-sistema    error del sistema
/sistema/mis-reclamos.html?simular=no-disponible    contenido no disponible
/sistema/mis-reclamos.html?simular=sin-permisos     sesión vencida
```

## Los cuatro correos

Están en `backend/email_templates.py`. Son responsivos de verdad: una sola columna de 600 px, botón de 56 px de alto (se puede tocar con el dedo), versión en texto plano para los clientes que no muestran HTML, y modo oscuro con `prefers-color-scheme` para quien lee el correo de noche.

| # | Correo | Cuándo sale |
|---|---|---|
| 1 | Verificación de la dirección | Al crear la cuenta. El enlace vence en 24 horas |
| 2 | Bienvenida | Cuando la persona confirma el correo |
| 3 | Recuperación de contraseña | Desde «¿Olvidaste tu contraseña?» |
| 4 | Código para eliminar la cuenta | En el paso 3 de la baja. Son 6 dígitos y vencen en 10 minutos |

A esos se suma el comprobante del reclamo con el PDF adjunto. Sin SMTP configurado, todos se guardan como `.eml` en `backend/sent_emails/` y la interfaz lo dice («envío en modo demo»).

## Baja de cuenta

La baja está pensada para que nadie la haga por error y para que nadie se quede atrapado:

1. **Antes de borrar**, tres alternativas que sí se pueden deshacer: silenciar los avisos, desactivar la cuenta por un tiempo o descargar una copia de los datos.
2. **Qué se elimina y qué se conserva**, lado a lado. Los reclamos ya registrados se conservan de forma anonimizada, porque Integratel debe guardarlos según las normas de Osiptel y del Libro de Reclamaciones de Indecopi; lo que se borra es la cuenta de acceso y los datos de contacto.
3. **Dos confirmaciones** y escribir la palabra `ELIMINAR`.
4. **Código de 6 dígitos** enviado al correo, que vence en 10 minutos.
5. **30 días de gracia**: la cuenta queda eliminada pero se puede recuperar entera. Si la persona intenta iniciar sesión en ese plazo, el error le ofrece el botón para recuperarla.
6. **Eliminación definitiva** al terminar el plazo.

En todo el flujo, el botón de borrar nunca es el foco inicial, la confirmación no depende del color y el recorrido completo se puede hacer con el teclado.

## Cómo comprobarlo

```bash
python backend/_pruebas.py
```

Recorre la API entera (registro y verificación, los 23 ajustes, reclamos, notificaciones, seguimiento público, las cinco simulaciones de estado, las tres alternativas a la baja, las seis etapas de la eliminación con su periodo de gracia, la recuperación de contraseña y el PDF) y termina con el número de fallas. Corre contra una base SQLite temporal, así que no toca la base real ni necesita MySQL levantado.

## Paleta e identidad visual

Se usa la misma paleta navy + cian ya utilizada en el informe Word y la presentación PPT del proyecto (`#0B2545`, `#134074`, `#00B4D8`), para mantener consistencia de marca en todos los entregables. El logotipo es un wordmark propio ("IT" en un cuadrado con gradiente) — no se reproduce el logo real de Integratel/Movistar, ya que es una marca registrada de terceros.

## Sobre la "seguridad" del prototipo

Las contraseñas se guardan en texto plano en la base de datos (columna `password` de `usuarios`), no cifradas como en un sistema en producción (que usaría, por ejemplo, `bcrypt`). Para un proyecto real habría que aplicar hash a las contraseñas y usar tokens de sesión (JWT/cookies firmadas) en vez de solo recordar el DNI en el navegador. Aquí el foco es demostrar el flujo de una cuenta verificada conectada a una base de datos real, no una implementación de seguridad de producción — vale la pena mencionarlo así en la sustentación si preguntan.

## Notas para la sustentación

- Todo el código es legible y está organizado por bloques; se puede explicar directamente desde el editor (`backend/app.py` para la base de datos y la API, `assets/js/reclamos.js` para cómo el frontend la consume).
- El servidor Flask **debe estar corriendo** (`python backend/app.py`) antes de grabar el video o mostrar el sistema — sin él, el sitio institucional se ve igual pero el sistema de reclamos no podrá cargar ni guardar datos.
- Para reiniciar la base desde cero (borrar todo y volver a sembrar la cuenta demo), cierra el servidor y ejecuta `DROP DATABASE integratel_reclamos;` en MySQL Workbench, luego `backend/crear_usuario_mysql.sql`; la próxima vez que ejecutes `python backend/app.py` se vuelve a crear con sus datos de ejemplo.
- Puedes abrir la base en **MySQL Workbench** para mostrarle al docente las tablas y filas reales durante la sustentación. Las consultas útiles están comentadas al final de `backend/migracion_ap3.sql`.
- Para demostrar el envío de correo sin configurar SMTP, registra un reclamo en vivo y abre `backend/sent_emails/` justo después: ahí aparece el `.eml` con el PDF adjunto que "se habría enviado". Si prefieres mostrar un envío real, configura las variables `SMTP_*` (ver sección anterior) antes de la grabación.


## Asistente de voz con agente de IA (Proyecto Final IHM)

Con la sesión iniciada aparece un botón de micrófono (o `Alt + Q`) en todas las pantallas del sistema. El usuario habla (Web Speech API, Chrome o Edge) o escribe; `assets/js/asistente.js` interpreta el pedido (NLU ligero por reglas), decide y ejecuta acciones con la API REST del sistema: registrar un reclamo (siempre pide confirmación), consultar el estado, resumir la cuenta, abrir pantallas y cerrar sesión. Responde con texto y con voz. Para publicarlo en el despliegue basta subir `assets/js/asistente.js` y `assets/js/app-shell.js`.


## Ejecutar el proyecto desde GitHub

Repositorio: https://github.com/U23208480/integratel-reclamos-ihm

### Opción A. En tu computadora (con MySQL)

Requisitos: Git, Python 3.10 o superior y MySQL 8 en ejecución.

```bash
git clone https://github.com/U23208480/integratel-reclamos-ihm.git
cd integratel-reclamos-ihm
python -m venv .venv
.venv\Scripts\activate            # en Linux o Mac: source .venv/bin/activate
pip install -r backend/requirements.txt
```

Crea el usuario de la base en MySQL ejecutando `backend/crear_usuario_mysql.sql` (por ejemplo, desde MySQL Workbench) o, si usas otro usuario, define las variables `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` y `MYSQL_DB`. Luego inicia el servidor:

```bash
python backend/app.py
```

Abre http://localhost:5000. La primera vez se crean las tablas y una cuenta de demostración: DNI `71234567`, contraseña `Demo1234`. Para probar el asistente de voz, inicia sesión y pulsa el botón del micrófono (o `Alt + Q`) usando Chrome o Edge.

### Opción B. Publicado en PythonAnywhere (la URL del proyecto)

1. En una consola de PythonAnywhere: `git clone https://github.com/U23208480/integratel-reclamos-ihm.git` (si la carpeta ya existe: `git pull`).
2. En la pestaña Web, apunta el código fuente y el archivo WSGI a esa carpeta, y configura las variables `MYSQL_*` con la base de datos de tu cuenta.
3. Pulsa **Reload**. Cada cambio nuevo en GitHub se aplica con `git pull` y **Reload**.

### Pruebas automáticas

```bash
cd backend
python _pruebas.py
```

Muestra 52 verificaciones de la API y termina con `FALLAS: 0`.

Para probar la comprensión del asistente (desde la raíz del proyecto): `npm test`.

> Nota: GitHub Pages solo sirve páginas estáticas, por lo que sirve para ver el sitio institucional pero no el sistema de reclamos, que necesita el servidor Flask y la base de datos.

## Documentación

- [Arquitectura](docs/ARQUITECTURA.md)
- [API REST](docs/API.md)
- [Asistente de voz](docs/ASISTENTE_DE_VOZ.md)
- [Accesibilidad e inclusión](docs/ACCESIBILIDAD.md)
- [Cambios](CHANGELOG.md)
- [Nota académica](docs/NOTA_ACADEMICA.md)

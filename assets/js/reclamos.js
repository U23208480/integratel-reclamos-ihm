// ============================================================
// INTEGRATEL PERÚ — Sistema de Gestión de Reclamos
// Cliente de API — habla con el backend Flask + SQLite (base de datos real)
// Todas las funciones de datos son asíncronas (devuelven Promesas).
// ============================================================

const LS_SESSION = 'integratel_sesion_v1';

const TIPOS_RECLAMO = [
  'Facturación y cobros',
  'Avería / corte de servicio',
  'Instalación o mantenimiento',
  'Atención al cliente',
  'Velocidad / calidad de conexión',
  'Otro'
];

const ESTADOS = ['Recibido', 'En proceso', 'Atendido', 'Improcedente'];

// ---------------------------------------------------------------- utils
function fechaCorta(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' });
}
function fechaHora(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' }) +
    ' · ' + d.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' });
}

// ---------------------------------------------------------------- API client
async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(path, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    let data;
    try { data = await res.json(); }
    catch (e) { data = { ok: false, error: 'El servidor no devolvió una respuesta válida.' }; }
    if (!data.error && !res.ok) data.error = 'Ocurrió un error inesperado (código ' + res.status + ').';
    return data;
  } catch (e) {
    return { ok: false, error: 'No se pudo conectar con el servidor. ¿Está corriendo "python backend/app.py"?' };
  }
}

// ============================================================
// USUARIOS (cuenta verificada — validada en el servidor / base de datos)
// ============================================================
async function registrarUsuario({ nombre, dni, correo, telefono, password }) {
  return apiFetch('/api/registro', { method: 'POST', body: JSON.stringify({ nombre, dni, correo, telefono, password }) });
}
async function autenticarUsuario(dni, password) {
  return apiFetch('/api/login', { method: 'POST', body: JSON.stringify({ dni, password }) });
}
async function recuperarContrasena(identificador) {
  return apiFetch('/api/recuperar', { method: 'POST', body: JSON.stringify({ identificador }) });
}
async function getPerfil(dni) {
  return apiFetch(`/api/perfil/${encodeURIComponent(dni)}`);
}
async function actualizarPerfil(dni, cambios) {
  return apiFetch(`/api/perfil/${encodeURIComponent(dni)}`, { method: 'PATCH', body: JSON.stringify(cambios) });
}
async function cambiarPassword(dni, actual, nueva) {
  return apiFetch(`/api/perfil/${encodeURIComponent(dni)}/password`, { method: 'POST', body: JSON.stringify({ actual, nueva }) });
}

// ============================================================
// RECLAMOS (persistidos en SQLite en el servidor)
// ============================================================
async function getClaimsForCurrentUser() {
  const dni = getSession();
  if (!dni) return [];
  const r = await apiFetch(`/api/reclamos?dni=${encodeURIComponent(dni)}`);
  return r.ok ? r.reclamos : [];
}
async function getClaimById(id) {
  const r = await apiFetch(`/api/reclamos/${encodeURIComponent(id)}`);
  return r.ok ? r.reclamo : null;
}
/** Devuelve {ok, reclamo} o {ok:false, error} */
async function addClaim({ dni, nombre, tipo, descripcion, canal, correo, telefono, archivos }) {
  return apiFetch('/api/reclamos', {
    method: 'POST',
    body: JSON.stringify({ dni, nombre, tipo, descripcion, canal, correo, telefono, archivos: archivos || [] }),
  });
}
/** Cambia el estado a uno específico: 'Recibido' | 'En proceso' | 'Atendido' | 'Improcedente' */
async function cambiarEstado(id, estado) {
  return apiFetch(`/api/reclamos/${encodeURIComponent(id)}/estado`, { method: 'PATCH', body: JSON.stringify({ estado }) });
}

/** URL para descargar el PDF del reclamo (generado en el servidor a partir de la base de datos). */
function getPdfUrl(id) {
  return `/api/reclamos/${encodeURIComponent(id)}/pdf`;
}

/** Descarga el PDF del reclamo directamente en el navegador. */
function descargarPdf(id) {
  const a = document.createElement('a');
  a.href = getPdfUrl(id);
  a.download = `${id}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

/** Reenvía (o envía por primera vez) el PDF del reclamo al correo del solicitante, o a uno alternativo. */
async function reenviarCorreo(id, correoAlternativo) {
  return apiFetch(`/api/reclamos/${encodeURIComponent(id)}/enviar-correo`, {
    method: 'POST',
    body: JSON.stringify(correoAlternativo ? { correo: correoAlternativo } : {}),
  });
}

// ---------------------------------------------------------------- session (ligera, en el navegador)
// La autenticación real ocurre en el servidor (/api/login); esto solo recuerda
// quién es el usuario activo en ESTE navegador para no pedir credenciales en cada página.
function setSession(dni, nombre) {
  localStorage.setItem(LS_SESSION, JSON.stringify({ dni, nombre, since: new Date().toISOString() }));
}
function getSession() {
  try { const s = JSON.parse(localStorage.getItem(LS_SESSION)); return s ? s.dni : null; }
  catch (e) { return null; }
}
function getSessionNombre() {
  try { const s = JSON.parse(localStorage.getItem(LS_SESSION)); return s ? s.nombre : ''; }
  catch (e) { return ''; }
}
async function getSessionUser() {
  const dni = getSession();
  if (!dni) return null;
  const r = await getPerfil(dni);
  return r.ok ? r.user : null;
}
function clearSession() { localStorage.removeItem(LS_SESSION); }

function requireSession() {
  if (!getSession()) {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}


// ============================================================
// AP3 — accesibilidad, notificaciones, seguimiento y baja de cuenta
// ============================================================
async function getAccesibilidad(dni) {
  return apiFetch(`/api/accesibilidad/${encodeURIComponent(dni)}`);
}
async function guardarAccesibilidad(dni, preferencias) {
  return apiFetch(`/api/accesibilidad/${encodeURIComponent(dni)}`,
    { method: 'PUT', body: JSON.stringify({ preferencias }) });
}
async function restablecerAccesibilidad(dni) {
  return apiFetch(`/api/accesibilidad/${encodeURIComponent(dni)}/restablecer`, { method: 'POST' });
}

/** Notificaciones del usuario (alimentan el estado 3: vacío por historial). */
async function getNotificaciones(dni, simular) {
  const q = simular ? `&simular=${encodeURIComponent(simular)}` : '';
  return apiFetch(`/api/notificaciones?dni=${encodeURIComponent(dni)}${q}`);
}
async function marcarNotificacionesLeidas(dni) {
  return apiFetch('/api/notificaciones/leer', { method: 'POST', body: JSON.stringify({ dni }) });
}

/** Consulta pública por código (estado 2: vacío por búsqueda). */
async function buscarPorCodigo(codigo, documento, simular) {
  const p = new URLSearchParams({ codigo: codigo || '' });
  if (documento) p.set('documento', documento);
  if (simular) p.set('simular', simular);
  return apiFetch('/api/seguimiento?' + p.toString());
}

/** Lista de reclamos con posibilidad de simular un estado (para la sustentación). */
async function getClaimsSimulado(simular) {
  const dni = getSession();
  if (!dni) return { ok: false, error: 'No hay sesión activa.' };
  const q = simular ? `&simular=${encodeURIComponent(simular)}` : '';
  return apiFetch(`/api/reclamos?dni=${encodeURIComponent(dni)}${q}`);
}
async function getClaimSimulado(id, simular) {
  const q = simular ? `?simular=${encodeURIComponent(simular)}` : '';
  return apiFetch(`/api/reclamos/${encodeURIComponent(id)}${q}`);
}

// ---- baja de cuenta (las seis etapas del AP3)
async function resumenCuenta(dni) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/resumen`);
}
async function silenciarAvisos(dni, silenciar) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/silenciar`,
    { method: 'POST', body: JSON.stringify({ silenciar }) });
}
async function desactivarCuenta(dni) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/desactivar`, { method: 'POST' });
}
async function reactivarCuenta(dni) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/reactivar`, { method: 'POST' });
}
function descargarMisDatos(dni) {
  const a = document.createElement('a');
  a.href = `/api/cuenta/${encodeURIComponent(dni)}/exportar`;
  a.download = `mis-datos-${dni}.json`;
  document.body.appendChild(a); a.click(); a.remove();
}
async function solicitarBaja(dni, payload) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/baja/solicitar`,
    { method: 'POST', body: JSON.stringify(payload) });
}
async function confirmarBaja(dni, payload) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/baja/confirmar`,
    { method: 'POST', body: JSON.stringify(payload) });
}
async function restaurarCuenta(dni) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/baja/restaurar`, { method: 'POST' });
}
async function estadoCuenta(dni) {
  return apiFetch(`/api/cuenta/${encodeURIComponent(dni)}/estado`);
}
async function reenviarVerificacion(dni) {
  return apiFetch('/api/reenviar-verificacion', { method: 'POST', body: JSON.stringify({ dni }) });
}
async function getMeta() { return apiFetch('/api/meta'); }

window.Reclamos = {
  TIPOS_RECLAMO, ESTADOS,
  getClaimsForCurrentUser, getClaimById, addClaim, cambiarEstado,
  getPdfUrl, descargarPdf, reenviarCorreo,
  setSession, getSession, getSessionNombre, getSessionUser, clearSession, requireSession,
  registrarUsuario, autenticarUsuario, recuperarContrasena, getPerfil, actualizarPerfil, cambiarPassword,
  fechaCorta, fechaHora,
  // AP3
  getAccesibilidad, guardarAccesibilidad, restablecerAccesibilidad,
  getNotificaciones, marcarNotificacionesLeidas,
  buscarPorCodigo, getClaimsSimulado, getClaimSimulado,
  resumenCuenta, silenciarAvisos, desactivarCuenta, reactivarCuenta, descargarMisDatos,
  solicitarBaja, confirmarBaja, restaurarCuenta, estadoCuenta, reenviarVerificacion, getMeta,
};

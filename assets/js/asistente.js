// ============================================================
// INTEGRATEL PERÚ — asistente.js
// Asistente de voz con agente de IA para el Sistema de Reclamos (Proyecto Final IHM)
//  - Entrada por voz: reconocimiento de voz del navegador (Web Speech API, es-PE) o texto
//  - Comprensión: NLU ligero (normalización, intenciones y clasificación del tipo de reclamo)
//  - Agente: decide la acción y la ejecuta con herramientas = la API REST del sistema
//  - Salida: texto + síntesis de voz. Acciones con efecto (registrar) piden confirmación.
// ============================================================
(function () {
  'use strict';

  // ---------------------------------------------------------- NLU (funciones puras)
  const norm = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[¿?¡!.,;]/g, ' ').replace(/\s+/g, ' ').trim();

  const TIPOS = {
    'Facturación y cobros': ['cobr', 'factur', 'recibo', 'monto', 'pago', 'pague', 'tarifa', 'doble', 'duplic', 'cargo', 'mayor al', 'deuda', 'importe'],
    'Avería / corte de servicio': ['averi', 'corte', 'cortaron', 'sin servicio', 'sin senal', 'sin internet', 'no funciona', 'no hay internet', 'no tengo senal', 'se cayo', 'caido', 'apag', 'dejo de funcionar'],
    'Instalación o mantenimiento': ['instala', 'tecnico', 'mantenimiento', 'visita', 'cita', 'cableado', 'router', 'modem', 'equipo'],
    'Atención al cliente': ['atencion', 'asesor', 'maltrat', 'mala atencion', 'llamada', 'nadie contesta', 'call center', 'agencia', 'trato', 'respuesta'],
    'Velocidad / calidad de conexión': ['lent', 'velocidad', 'megas', 'intermiten', 'se corta', 'senal debil', 'ping', 'latencia', 'inestable', 'calidad'],
  };

  /** Clasifica la descripción en uno de los tipos de reclamo (puntaje por palabras clave). */
  function clasificarTipo(texto) {
    const t = norm(texto);
    let mejor = 'Otro', max = 0, total = 0;
    for (const [tipo, claves] of Object.entries(TIPOS)) {
      const p = claves.reduce((a, c) => a + (t.includes(c) ? 1 : 0), 0);
      total += p;
      if (p > max) { max = p; mejor = tipo; }
    }
    return { tipo: mejor, confianza: total ? max / total : 0 };
  }

  const PAGINAS = [
    [['notificacion', 'aviso'], 'notificaciones.html', 'Notificaciones'],
    [['perfil', 'mi cuenta', 'mis datos'], 'perfil.html', 'Mi perfil'],
    [['accesibilidad'], 'accesibilidad.html', 'Centro de accesibilidad'],
    [['seguimiento', 'rastrear', 'consultar codigo'], 'seguimiento.html', 'Seguimiento'],
    [['nuevo reclamo', 'formulario'], 'nuevo-reclamo.html', 'Nuevo reclamo'],
    [['mis reclamos', 'lista de reclamos', 'historial'], 'mis-reclamos.html', 'Mis reclamos'],
  ];

  function extraerCodigo(t) {
    const m = t.match(/rec\D{0,3}(\d{4})\D{0,3}(\d{5})/);
    return m ? `REC-${m[1]}-${m[2]}` : null;
  }

  function extraerDescripcion(original) {
    // lo que viene después de ":" o de un conector ("que", "porque", "sobre", "por")
    let s = String(original || '').trim();
    const colon = s.indexOf(':');
    if (colon > -1) return s.slice(colon + 1).trim();
    const m = s.match(/\b(?:que|porque|sobre|por|diciendo|sucede que)\b\s+(.{12,})$/i);
    return m ? m[1].trim() : '';
  }

  /** Devuelve la intención: {intent, ...datos} */
  function interpretar(original) {
    const t = norm(original);
    if (!t) return { intent: 'vacio' };
    if (/^(si|sii|claro|confirmo|dale|ok|okay|de acuerdo|correcto|adelante)\b/.test(t)) return { intent: 'si' };
    if (/^(no|cancela|cancelar|mejor no|olvidalo|detente)\b/.test(t)) return { intent: 'no' };
    if (/\b(ayuda|que puedes hacer|comandos|como funcionas)\b/.test(t)) return { intent: 'ayuda' };
    if (/\b(cerrar sesion|salir|desconectar)\b/.test(t)) return { intent: 'salir' };
    const codigo = extraerCodigo(t);
    if (/\b(estado|como va|en que va|situacion|avance)\b/.test(t) || (codigo && /\b(reclamo|ticket|codigo)\b/.test(t))) {
      return { intent: 'estado', codigo };
    }
    if (/\b(cuantos|resumen|mis reclamos|lista|listar|que reclamos)\b/.test(t) && !/\b(ir a|abre|abrir|llevame)\b/.test(t)) {
      return { intent: 'resumen' };
    }
    if (/\b(registr|crear|crea|nuevo|nueva|presentar|poner|hacer|levantar|quiero reclamar|quiero poner)\w*/.test(t) && /\b(reclamo|queja)\b/.test(t)) {
      return { intent: 'registrar', descripcion: extraerDescripcion(original) };
    }
    if (/\b(ir a|abre|abrir|llevame|muestrame|ve a|vamos a)\b/.test(t) || PAGINAS.some(([k]) => k.some((x) => t === x))) {
      for (const [claves, href, nombre] of PAGINAS) if (claves.some((c) => t.includes(c))) return { intent: 'ir', href, nombre };
    }
    return { intent: 'desconocido' };
  }

  if (typeof module !== 'undefined') { module.exports = { norm, clasificarTipo, interpretar, extraerCodigo }; return; }
  window.AsistenteNLU = { clasificarTipo, interpretar };

  // ---------------------------------------------------------- Agente + interfaz
  if (window.__asistente || !window.Reclamos) return;
  window.__asistente = true;
  const R = window.Reclamos;
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const hayVoz = 'speechSynthesis' in window;
  let hablar = hayVoz;           // responder en voz alta
  let pendiente = null;          // acción a confirmar
  let escuchando = false, rec = null;

  const css = document.createElement('style');
  css.textContent = `
  #as-fab{position:fixed;right:18px;bottom:92px;z-index:9998;width:56px;height:56px;border-radius:50%;border:2px solid var(--cyan,#00B4D8);background:var(--navy,#0B2545);color:var(--cyan,#00B4D8);display:grid;place-items:center;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.35)}
  #as-fab:focus-visible,#as-panel button:focus-visible,#as-panel input:focus-visible{outline:3px solid var(--cyan,#00B4D8);outline-offset:2px}
  #as-panel{position:fixed;right:18px;bottom:160px;z-index:9999;width:min(380px,calc(100vw - 36px));max-height:min(540px,calc(100vh - 170px));display:none;flex-direction:column;border-radius:18px;background:var(--surface,#fff);color:var(--ink,#0B2545);border:1px solid rgba(120,150,190,.35);box-shadow:0 18px 50px rgba(0,0,0,.4);overflow:hidden;font-family:inherit}
  #as-panel.open{display:flex}
  #as-head{display:flex;align-items:center;gap:10px;padding:12px 14px;background:var(--navy,#0B2545);color:#fff}
  #as-head b{flex:1;font-size:15px}
  #as-head button{background:transparent;border:0;color:#fff;cursor:pointer;font-size:13px;padding:6px;border-radius:8px}
  #as-log{flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:8px;min-height:180px}
  .as-m{max-width:88%;padding:9px 12px;border-radius:14px;font-size:14px;line-height:1.4;white-space:pre-wrap}
  .as-m.bot{background:var(--cyan-light,#E6F8FC);color:var(--ink,#0B2545);align-self:flex-start;border-bottom-left-radius:4px}
  .as-m.yo{background:var(--cyan,#00B4D8);color:#04202b;align-self:flex-end;border-bottom-right-radius:4px}
  #as-chips{display:flex;flex-wrap:wrap;gap:6px;padding:0 12px 8px}
  #as-chips button{font-size:12px;padding:5px 9px;border-radius:999px;border:1px solid var(--cyan,#00B4D8);background:transparent;color:var(--cyan-text,#00748C);cursor:pointer}
  #as-form{display:flex;gap:6px;padding:10px;border-top:1px solid rgba(120,150,190,.3)}
  #as-in{flex:1;padding:10px 12px;border-radius:12px;border:1px solid rgba(120,150,190,.5);background:transparent;color:inherit;font-size:14px;min-width:0}
  #as-form button{width:42px;border-radius:12px;border:0;background:var(--cyan,#00B4D8);color:#04202b;cursor:pointer;font-weight:700}
  #as-mic.on{background:#E5484D;color:#fff;animation:asp 1s infinite}
  @keyframes asp{50%{box-shadow:0 0 0 8px rgba(229,72,77,.25)}}
  @media (prefers-reduced-motion:reduce){#as-mic.on{animation:none}}
  @media (max-width:820px){#as-fab{bottom:150px}#as-panel{bottom:216px}}`;
  document.head.appendChild(css);

  const ic = (d) => `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
  const MIC = '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>';

  const fab = document.createElement('button');
  fab.id = 'as-fab'; fab.type = 'button'; fab.setAttribute('aria-label', 'Abrir el asistente de voz (Alt + Q)'); fab.title = 'Asistente de voz (Alt + Q)';
  fab.innerHTML = ic(MIC);
  const panel = document.createElement('div');
  panel.id = 'as-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Asistente de voz de Integratel');
  panel.innerHTML = `
    <div id="as-head"><b>Asistente Integratel</b><button type="button" id="as-voz" aria-pressed="${hablar}" title="Activar o desactivar la respuesta en voz">Voz: ${hablar ? 'sí' : 'no'}</button><button type="button" id="as-x" aria-label="Cerrar el asistente">✕</button></div>
    <div id="as-log" role="log" aria-live="polite"></div>
    <div id="as-chips"></div>
    <form id="as-form" autocomplete="off">
      <input id="as-in" type="text" placeholder="Escribe o habla: «estado de mi reclamo»" aria-label="Escribe tu pedido">
      ${SR ? `<button type="button" id="as-mic" aria-label="Hablar">${ic(MIC)}</button>` : ''}
      <button type="submit" aria-label="Enviar">➤</button>
    </form>`;
  document.body.appendChild(fab); document.body.appendChild(panel);
  const log = panel.querySelector('#as-log'), input = panel.querySelector('#as-in'), chips = panel.querySelector('#as-chips');

  function decir(texto, quien) {
    const d = document.createElement('div'); d.className = 'as-m ' + (quien || 'bot'); d.textContent = texto; log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    if (quien !== 'yo' && hablar && hayVoz) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(texto); u.lang = 'es-PE'; u.rate = 1; window.speechSynthesis.speak(u);
    }
  }
  function sugerencias(lista) {
    chips.innerHTML = '';
    lista.forEach((s) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = s; b.onclick = () => procesar(s); chips.appendChild(b); });
  }
  const SUG = ['¿Cuántos reclamos tengo?', 'Estado de mi último reclamo', 'Registrar un reclamo', 'Abrir notificaciones', 'Ayuda'];

  // ---------------------------------------------------------- herramientas (API REST)
  const tools = {
    async listar() { return R.getClaimsForCurrentUser(); },
    async estado(codigo) {
      if (codigo) return R.getClaimById(codigo);
      const l = await R.getClaimsForCurrentUser(); return l[0] ? R.getClaimById(l[0].id) : null;
    },
    async registrar(descripcion, clasif) {
      const u = await R.getSessionUser(); if (!u) return { ok: false, error: 'No pude leer tu perfil.' };
      const correoOk = /^\S+@\S+\.\S+$/.test(u.correo || '');
      return R.addClaim({ dni: u.dni, nombre: u.nombre, tipo: clasif.tipo, descripcion,
        canal: correoOk ? 'Correo electrónico' : 'Teléfono / SMS', correo: u.correo || '', telefono: u.telefono || '', archivos: [] });
    },
  };

  const AYUDA = 'Puedo hacer esto por ti:\n• «Registrar un reclamo: me cobraron el recibo doble»\n• «Estado de mi último reclamo» o «Estado de REC-2026-00015»\n• «¿Cuántos reclamos tengo?»\n• «Abrir notificaciones / perfil / accesibilidad / seguimiento»\n• «Cerrar sesión»';

  async function procesar(texto) {
    texto = String(texto || '').trim(); if (!texto) return;
    decir(texto, 'yo'); input.value = '';
    const it = interpretar(texto);
    try {
      if (pendiente && pendiente.tipo === 'descripcion' && !['si', 'no', 'ayuda'].includes(it.intent) && texto.length >= 12) {
        return proponerRegistro(texto);
      }
      switch (it.intent) {
        case 'ayuda': decir(AYUDA); break;
        case 'si': case 'no':
          if (pendiente && pendiente.tipo === 'registro') {
            if (it.intent === 'no') { pendiente = null; decir('Listo, no registré nada. ¿Algo más?'); break; }
            const p = pendiente; pendiente = null; decir('Registrando tu reclamo…');
            const r = await tools.registrar(p.descripcion, p.clasif);
            if (r && r.ok) { decir(`Listo. Registré tu reclamo ${r.reclamo.id} como «${p.clasif.tipo}». Te llevo a la confirmación.`); setTimeout(() => { location.href = `confirmacion.html?id=${encodeURIComponent(r.reclamo.id)}`; }, 2500); }
            else decir('No pude registrarlo: ' + ((r && r.error) || 'error desconocido'));
          } else decir('No tengo nada pendiente por confirmar.');
          break;
        case 'registrar':
          if (it.descripcion && it.descripcion.length >= 15) await proponerRegistro(it.descripcion);
          else { pendiente = { tipo: 'descripcion' }; decir('Claro. Cuéntame qué pasó, con al menos una frase completa. Por ejemplo: «Me cobraron el recibo de internet dos veces».'); }
          break;
        case 'estado': {
          const r = await tools.estado(it.codigo);
          if (!r) decir(it.codigo ? `No encontré el reclamo ${it.codigo}.` : 'Aún no tienes reclamos registrados.');
          else {
            const h = (r.historial || []); const ult = h[h.length - 1];
            decir(`El reclamo ${r.id} («${r.tipo}») está «${r.estado}».` + (ult && ult.nota ? ` Último movimiento: ${ult.nota}` : ''));
          }
          break;
        }
        case 'resumen': {
          const l = await tools.listar();
          if (!l.length) { decir('Todavía no tienes reclamos registrados.'); break; }
          const c = {}; l.forEach((x) => { c[x.estado] = (c[x.estado] || 0) + 1; });
          decir(`Tienes ${l.length} reclamo${l.length > 1 ? 's' : ''}: ` + Object.entries(c).map(([e, n]) => `${n} ${e.toLowerCase()}`).join(', ') + '.');
          break;
        }
        case 'ir': decir(`Abriendo ${it.nombre}…`); setTimeout(() => { location.href = it.href; }, 900); break;
        case 'salir': decir('Cerrando tu sesión.'); R.clearSession(); setTimeout(() => { location.href = 'index.html'; }, 900); break;
        default:
          // si parece la descripción de un problema, el agente ofrece registrarla como reclamo
          if (texto.length >= 20 && clasificarTipo(texto).confianza > 0) { decir('Parece que quieres reportar un problema.'); await proponerRegistro(texto); }
          else decir('No te entendí del todo. Di «ayuda» para ver lo que puedo hacer.');
      }
    } catch (e) { decir('Tuve un problema al conectar con el sistema. Inténtalo de nuevo.'); }
  }

  async function proponerRegistro(descripcion) {
    const clasif = clasificarTipo(descripcion);
    pendiente = { tipo: 'registro', descripcion, clasif };
    decir(`Entendí esto:\n«${descripcion}»\nLo clasifiqué como «${clasif.tipo}». ¿Confirmo el registro? Di «sí» o «no».`);
    sugerencias(['Sí', 'No']);
  }

  // ---------------------------------------------------------- eventos
  function abrir(v) {
    panel.classList.toggle('open', v);
    fab.setAttribute('aria-expanded', String(v));
    if (v) { if (!log.children.length) { decir('Hola, soy el asistente de Integratel. Puedes hablarme o escribirme. Di «ayuda» para ver lo que sé hacer.'); sugerencias(SUG); } input.focus(); }
    else { if (rec && escuchando) rec.stop(); if (hayVoz) window.speechSynthesis.cancel(); }
  }
  fab.addEventListener('click', () => abrir(!panel.classList.contains('open')));
  panel.querySelector('#as-x').addEventListener('click', () => { abrir(false); fab.focus(); });
  panel.querySelector('#as-voz').addEventListener('click', (e) => { hablar = !hablar; e.target.textContent = 'Voz: ' + (hablar ? 'sí' : 'no'); e.target.setAttribute('aria-pressed', hablar); if (!hablar && hayVoz) window.speechSynthesis.cancel(); });
  panel.querySelector('#as-form').addEventListener('submit', (e) => { e.preventDefault(); procesar(input.value); });
  document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key.toLowerCase() === 'q') { e.preventDefault(); abrir(!panel.classList.contains('open')); }
    if (e.key === 'Escape' && panel.classList.contains('open')) { abrir(false); fab.focus(); }
  });

  const mic = panel.querySelector('#as-mic');
  if (mic && SR) {
    rec = new SR(); rec.lang = 'es-PE'; rec.interimResults = false; rec.maxAlternatives = 1;
    rec.onresult = (ev) => { const t = ev.results[0][0].transcript; procesar(t); };
    rec.onend = () => { escuchando = false; mic.classList.remove('on'); mic.setAttribute('aria-label', 'Hablar'); };
    rec.onerror = (ev) => { decir(ev.error === 'not-allowed' ? 'Necesito permiso para usar el micrófono. Mientras tanto puedes escribirme.' : 'No pude escucharte. Inténtalo de nuevo o escribe tu pedido.'); };
    mic.addEventListener('click', () => {
      if (escuchando) { rec.stop(); return; }
      if (hayVoz) window.speechSynthesis.cancel();
      try { rec.start(); escuchando = true; mic.classList.add('on'); mic.setAttribute('aria-label', 'Detener'); } catch (e) { /* ya activo */ }
    });
  }
})();

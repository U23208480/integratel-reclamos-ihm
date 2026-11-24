// ============================================================
// INTEGRATEL PERÚ — a11y.js
// Módulo de accesibilidad del AP3: 23 ajustes, tres temas visuales
// y cuatro idiomas. Se auto-inyecta en cualquier página que lo cargue:
// enlace "saltar al contenido", botón flotante, panel rápido, guía de
// lectura, reproductor de voz, ventana de LSP y aviso de sesión.
//
// Las preferencias se guardan en la cuenta (API /api/accesibilidad/<dni>)
// y además en localStorage, para que la página pinte bien desde el primer
// frame aunque el servidor tarde.
// ============================================================
(function () {
  'use strict';

  const LS = 'integratel_a11y_v1';
  const LS_SESION = 'integratel_sesion_v1';

  const DEFECTO = {
    fs: 100, contraste: 'normal', tema: 'auto', fuente: 'sistema', espaciado: 'normal',
    enlaces: false, movimiento: false, guia: false,
    voz: false, vozVel: 1, subtitulos: true, transcripcion: true, lsp: false, alertasVisuales: true,
    foco: true, saltar: true, atajos: true, sesion: 40, confirmar: true,
    idioma: 'es', lecturaFacil: false, glosario: true, traducir: false,
  };

  let prefs = Object.assign({}, DEFECTO);
  let guardarTimer = null;

  // ---------------------------------------------------------------- iconos
  const IC = {
    a11y: '<circle cx="12" cy="4.5" r="2.1"/><path d="M4.8 8.8 12 10.4l7.2-1.6M12 10.4v4.2M12 14.6 8.8 21M12 14.6 15.2 21"/>',
    texto: '<path d="M2.6 18.6 7.4 5.8l4.8 12.8M4.2 14.4h6.4M14.6 18.6 18 9.8l3.4 8.8M15.8 15.8h4.4"/>',
    contraste: '<circle cx="12" cy="12" r="9"/><path d="M12 3.4a8.6 8.6 0 0 1 0 17.2z" fill="currentColor"/>',
    luna: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    sol: '<circle cx="12" cy="12" r="4.4"/><path d="M12 2.2v2.4M12 19.4v2.4M2.2 12h2.4M19.4 12h2.4M5.1 5.1l1.7 1.7M17.2 17.2l1.7 1.7M18.9 5.1l-1.7 1.7M6.8 17.2l-1.7 1.7"/>',
    voz: '<path d="M11 5.2 6.2 9.2H3v5.6h3.2L11 18.8z"/><path d="M14.8 9a4.2 4.2 0 0 1 0 6M17.6 6a8 8 0 0 1 0 12"/>',
    subtitulos: '<rect x="2" y="5.5" width="20" height="13" rx="2"/><path d="M7 10.5h3M7 14h5M14 10.5h3M14 14h3"/>',
    mano: '<path d="M9 11.5V5.6a1.6 1.6 0 0 1 3.2 0v5.9M12.2 11.5V4.6a1.6 1.6 0 0 1 3.2 0v6.9M15.4 11.5V7a1.6 1.6 0 0 1 3.2 0v6.3a7 7 0 0 1-7 7h-.8a7 7 0 0 1-7-7v-2.1a1.6 1.6 0 0 1 3.2 0v1.3"/>',
    movimiento: '<path d="M3.5 8.5h9M3.5 12.5h12M3.5 16.5h7M20.5 5.5 14 20"/>',
    enlace: '<path d="M10.2 13.8a4.6 4.6 0 0 0 6.5 0l2.1-2.1a4.6 4.6 0 0 0-6.5-6.5l-1 1M13.8 10.2a4.6 4.6 0 0 0-6.5 0l-2.1 2.1a4.6 4.6 0 0 0 6.5 6.5l1-1"/>',
    teclado: '<rect x="2" y="6.5" width="20" height="11" rx="1.5"/><path d="M5.6 10h.01M9 10h.01M12.4 10h.01M15.8 10h.01M19 10h.01M7.5 14h9"/>',
    cursor: '<path d="M5.5 3.2 19 11.4l-6.2 1.4L9.6 19.6z"/>',
    globo: '<circle cx="12" cy="12" r="9"/><path d="M3.2 12h17.6M12 3a13.5 13.5 0 0 1 0 18M12 3a13.5 13.5 0 0 0 0 18"/>',
    cerrar: '<path d="M6.2 6.2 17.8 17.8M17.8 6.2 6.2 17.8"/>',
    play: '<path d="M8.4 5.2 19 12 8.4 18.8z" fill="currentColor"/>',
    pausa: '<path d="M9 5.6v12.8M15 5.6v12.8"/>',
    saltar: '<path d="M4.6 12h14.8M13.4 6l6 6-6 6"/>',
    deshacer: '<path d="M4 9h9.5a5.5 5.5 0 1 1 0 11H8M7.6 5.2 3.8 9l3.8 3.8"/>',
    reloj: '<circle cx="12" cy="12" r="9"/><path d="M12 7.2v5.4l3.6 2.1"/>',
  };
  const svg = (d, w) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w || 1.9}" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;

  // ---------------------------------------------------------------- persistencia
  function sesionDni() {
    try { const s = JSON.parse(localStorage.getItem(LS_SESION)); return s ? s.dni : null; }
    catch (e) { return null; }
  }
  function leerLocal() {
    try {
      const g = JSON.parse(localStorage.getItem(LS) || '{}');
      Object.keys(DEFECTO).forEach((k) => { if (k in g) prefs[k] = g[k]; });
    } catch (e) { /* almacenamiento bloqueado: se usan los valores por defecto */ }
  }
  function escribirLocal() {
    try { localStorage.setItem(LS, JSON.stringify(prefs)); } catch (e) {}
  }
  function guardarServidor() {
    const dni = sesionDni();
    if (!dni) return;
    clearTimeout(guardarTimer);
    guardarTimer = setTimeout(() => {
      fetch('/api/accesibilidad/' + encodeURIComponent(dni), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferencias: prefs }),
      }).catch(() => { /* sin conexión: queda guardado en el navegador */ });
    }, 500);
  }
  async function cargarServidor() {
    const dni = sesionDni();
    if (!dni) return;
    try {
      const r = await fetch('/api/accesibilidad/' + encodeURIComponent(dni));
      const d = await r.json();
      if (d && d.ok && d.preferencias) {
        prefs = Object.assign({}, DEFECTO, d.preferencias);
        escribirLocal(); aplicar(); pintarPanel();
      }
    } catch (e) { /* el servidor no respondió: seguimos con lo local */ }
  }

  // ---------------------------------------------------------------- aplicar
  function temaEfectivo() {
    if (prefs.tema === 'noche') return 'noche';
    if (prefs.tema === 'dia') return 'dia';
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'noche' : 'dia';
  }

  function aplicar() {
    const h = document.documentElement;
    h.setAttribute('data-tema', temaEfectivo());
    h.setAttribute('data-contraste', prefs.contraste);
    h.setAttribute('data-fs', String(prefs.fs));
    h.setAttribute('data-fuente', prefs.fuente);
    h.setAttribute('data-espaciado', prefs.espaciado);
    h.setAttribute('data-enlaces', prefs.enlaces ? 'on' : 'off');
    h.setAttribute('data-movimiento', prefs.movimiento ? 'off' : 'on');
    h.setAttribute('data-foco', prefs.foco ? 'on' : 'off');
    h.setAttribute('data-saltar', prefs.saltar ? 'on' : 'off');
    h.setAttribute('data-guia', prefs.guia ? 'on' : 'off');
    h.setAttribute('data-lsp', prefs.lsp ? 'on' : 'off');
    h.setAttribute('data-lectura-facil', prefs.lecturaFacil ? 'on' : 'off');
    h.setAttribute('data-glosario', prefs.glosario ? 'on' : 'off');
    h.setAttribute('data-alertas-visuales', prefs.alertasVisuales ? 'on' : 'off');
    if (window.I18N) window.I18N.aplicar(prefs.idioma);
    actualizarBotonesTopbar();
    if (!prefs.voz) detenerVoz();
    document.dispatchEvent(new CustomEvent('a11y:cambio', { detail: { prefs } }));
  }

  function set(clave, valor) {
    prefs[clave] = valor;
    escribirLocal(); aplicar(); guardarServidor();

    // El panel se vuelve a dibujar, así que el foco se devuelve al mismo control:
    // quien navega con teclado no pierde su sitio al cambiar un ajuste (WCAG 3.2.2).
    const a = document.activeElement;
    let sello = null;
    if (a && a.closest && a.closest('#a11y-panel')) {
      if (a.hasAttribute('data-sw')) sello = '[data-sw="' + a.getAttribute('data-sw') + '"]';
      else if (a.hasAttribute('data-seg')) sello = '[data-seg="' + a.getAttribute('data-seg') +
                                                   '"][data-val="' + a.getAttribute('data-val') + '"]';
      else if (a.id) sello = '#' + a.id;
    }
    pintarPanel();
    if (sello) {
      const n = document.querySelector('#a11y-panel ' + sello);
      if (n) n.focus();
    }
  }

  // ---------------------------------------------------------------- interfaz inyectada
  function crear(tag, attrs, html) {
    const el = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => el.setAttribute(k, v));
    if (html != null) el.innerHTML = html;
    return el;
  }

  function montarBase() {
    // enlace "saltar al contenido" — primer elemento enfocable (WCAG 2.4.1)
    if (!document.querySelector('.skip-link')) {
      const destino = document.querySelector('main, .app-content, #contenido') || document.body;
      if (!destino.id) destino.id = 'contenido';
      const a = crear('a', { href: '#' + destino.id, class: 'skip-link' }, 'Saltar al contenido principal');
      document.body.insertBefore(a, document.body.firstChild);
      destino.setAttribute('tabindex', '-1');
    }
    // guía de lectura
    if (!document.getElementById('reading-guide')) {
      document.body.appendChild(crear('div', { id: 'reading-guide', 'aria-hidden': 'true' }));
    }
    // ventana del intérprete de Lengua de Señas Peruana
    if (!document.querySelector('.lsp-box')) {
      document.body.appendChild(crear('div', { class: 'lsp-box', 'aria-hidden': 'true' },
        svg(IC.mano, 2) + '<span>Intérprete LSP</span>'));
    }
    // reproductor de lectura por voz
    if (!document.querySelector('.tts-bar')) {
      document.body.appendChild(crear('div', { class: 'tts-bar', role: 'region', 'aria-label': 'Lectura por voz' },
        '<button class="play" id="tts-play" aria-label="Pausar o reanudar la lectura">' + svg(IC.pausa, 2.2) + '</button>' +
        '<div class="info"><b id="tts-txt">Lectura por voz activa</b><span id="tts-sub">Voz del sistema en español</span></div>' +
        '<div class="ctrl">' +
        '<button id="tts-restart" title="Volver a empezar" aria-label="Volver a empezar">' + svg(IC.deshacer) + '</button>' +
        '<button id="tts-stop" title="Cerrar el reproductor" aria-label="Cerrar el reproductor">' + svg(IC.cerrar, 2.2) + '</button>' +
        '</div>'));
    }
    // aviso de sesión por vencer (WCAG 2.2.1)
    if (!document.querySelector('.sesion-aviso')) {
      document.body.appendChild(crear('div', { class: 'sesion-aviso', role: 'alertdialog', 'aria-live': 'assertive' },
        svg(IC.reloj, 2) + '<span id="sesion-txt">Tu sesión vence en 2 minutos.</span>' +
        '<button class="btn btn-primary btn-sm" id="sesion-extender">Seguir conectado</button>'));
    }
    // botón flotante + panel
    if (!document.querySelector('.a11y-fab')) {
      const fab = crear('button', {
        class: 'a11y-fab', id: 'a11y-fab', type: 'button',
        'aria-expanded': 'false', 'aria-controls': 'a11y-panel',
        'aria-label': 'Abrir el panel de accesibilidad (Alt + A)',
      }, '<span class="lbl">Accesibilidad</span><span class="dot">' + svg(IC.a11y, 2.1) + '</span>');
      document.body.appendChild(fab);
      document.body.appendChild(crear('div', { class: 'a11y-scrim', id: 'a11y-scrim' }));
      document.body.appendChild(crear('aside', {
        class: 'a11y-panel', id: 'a11y-panel', role: 'dialog', 'aria-modal': 'true',
        'aria-label': 'Panel de accesibilidad',
      }, ''));
    }
    document.body.appendChild(crear('div', { id: 'a11y-live', class: 'sr-only', 'aria-live': 'polite' }));
  }

  // ---------------------------------------------------------------- panel rápido (11 ajustes)
  const FILAS = [
    { g: 'Visual' },
    { k: 'fs', tipo: 'slider', ic: IC.texto, t: 'Tamaño de texto', d: 'Agranda todo el texto de la página' },
    { k: 'contraste', tipo: 'seg', ic: IC.contraste, t: 'Contraste', d: 'Refuerza el contraste de texto y bordes',
      ops: [['normal', 'Normal'], ['alto', 'Alto'], ['invertido', 'Invertido']] },
    { k: 'tema', tipo: 'seg', ic: IC.luna, t: 'Tema de la interfaz', d: 'Día, noche o según tu sistema',
      ops: [['dia', 'Día'], ['noche', 'Noche'], ['auto', 'Automático']] },
    { k: 'fuente', tipo: 'sw', ic: IC.texto, t: 'Tipografía legible', d: 'Mayor interlineado y letra sin serifas',
      on: 'legible', off: 'sistema' },
    { k: 'movimiento', tipo: 'sw', ic: IC.movimiento, t: 'Reducir movimiento', d: 'Quita animaciones y desplazamiento automático' },
    { g: 'Auditivo' },
    { k: 'voz', tipo: 'sw', ic: IC.voz, t: 'Lectura por voz', d: 'Escucha la página con un clic' },
    { k: 'subtitulos', tipo: 'sw', ic: IC.subtitulos, t: 'Subtítulos y transcripción', d: 'En todos los videos del portal' },
    { k: 'lsp', tipo: 'sw', ic: IC.mano, t: 'Lengua de Señas Peruana', d: 'Intérprete en video sobre el contenido' },
    { g: 'Navegación' },
    { k: 'foco', tipo: 'sw', ic: IC.teclado, t: 'Foco visible y atajos', d: 'Recorre el portal solo con el teclado' },
    { k: 'guia', tipo: 'sw', ic: IC.cursor, t: 'Cursor y guía de lectura', d: 'Cursor grande y regla que sigue la línea' },
    { g: 'Idioma' },
    { k: 'idioma', tipo: 'seg', ic: IC.globo, t: 'Idioma de la interfaz', d: 'Cambia el idioma de toda la página',
      ops: [['es', 'Español'], ['en', 'English'], ['qu', 'Runasimi'], ['ay', 'Aymara']] },
  ];

  const ETIQ_FS = { 100: '100 %', 125: '125 %', 150: '150 %', 200: '200 %' };
  const VALORES_FS = [100, 125, 150, 200];

  function pintarPanel() {
    const panel = document.getElementById('a11y-panel');
    if (!panel) return;
    const activos = FILAS.filter((f) => f.k).length;

    let html = '<div class="a11y-head">' +
      '<span class="ic">' + svg(IC.a11y, 2.1) + '</span>' +
      '<div><h2>Accesibilidad</h2><p>' + activos + ' ajustes rápidos · se guardan en tu cuenta</p></div>' +
      '<button class="a11y-close" id="a11y-cerrar" aria-label="Cerrar el panel">' + svg(IC.cerrar, 2.2) + '</button>' +
      '</div><div class="a11y-body">';

    FILAS.forEach((f) => {
      if (f.g) { html += '<div class="a11y-group">' + f.g + '</div>'; return; }
      const valor = prefs[f.k];
      if (f.tipo === 'sw') {
        const encendido = f.on ? valor === f.on : !!valor;
        html += '<div class="a11y-row' + (encendido ? ' on' : '') + '">' +
          '<span class="ic">' + svg(f.ic) + '</span>' +
          '<span class="txt"><b>' + f.t + '</b><span>' + f.d + '</span></span>' +
          '<button class="sw" role="switch" aria-checked="' + encendido + '" data-sw="' + f.k + '"' +
          (f.on ? ' data-on="' + f.on + '" data-off="' + f.off + '"' : '') +
          ' aria-label="' + f.t + '"></button></div>';
      } else if (f.tipo === 'seg') {
        html += '<div class="a11y-row col"><div class="head"><span class="ic">' + svg(f.ic) + '</span>' +
          '<span class="txt"><b>' + f.t + '</b><span>' + f.d + '</span></span></div>' +
          '<div class="ctrl"><div class="seg" role="group" aria-label="' + f.t + '">' +
          f.ops.map(([v, l]) => '<button type="button" data-seg="' + f.k + '" data-val="' + v + '" aria-pressed="' +
            (valor === v) + '">' + l + '</button>').join('') +
          '</div></div></div>';
      } else if (f.tipo === 'slider') {
        const idx = Math.max(0, VALORES_FS.indexOf(Number(valor)));
        html += '<div class="a11y-row col"><div class="head"><span class="ic">' + svg(f.ic) + '</span>' +
          '<span class="txt"><b>' + f.t + '</b><span>' + f.d + '</span></span></div>' +
          '<div class="ctrl"><div class="fs-slider">' +
          '<input type="range" id="a11y-fs" min="0" max="3" step="1" value="' + idx + '" ' +
          'aria-label="Tamaño de texto" aria-valuetext="' + ETIQ_FS[valor] + '">' +
          '<span class="val" id="a11y-fs-val">' + ETIQ_FS[valor] + '</span></div></div></div>';
      }
    });

    html += '</div><div class="a11y-foot">' +
      '<a href="' + rutaSistema('accesibilidad.html') + '" class="btn btn-primary btn-sm" style="flex:1;">Ver los 23 ajustes</a>' +
      '<button class="btn btn-ghost btn-sm" id="a11y-reset">' + svg(IC.deshacer, 2) + ' Restablecer</button>' +
      '</div>';
    panel.innerHTML = html;
    conectarPanel();
  }

  function rutaSistema(archivo) {
    return location.pathname.indexOf('/sistema/') >= 0 ? archivo : 'sistema/' + archivo;
  }

  function conectarPanel() {
    const panel = document.getElementById('a11y-panel');
    panel.querySelectorAll('[data-sw]').forEach((b) => {
      b.addEventListener('click', () => {
        const k = b.getAttribute('data-sw');
        if (b.hasAttribute('data-on')) {
          set(k, prefs[k] === b.getAttribute('data-on') ? b.getAttribute('data-off') : b.getAttribute('data-on'));
        } else {
          set(k, !prefs[k]);
        }
        anunciar(b.getAttribute('aria-label') + ': ' + (b.getAttribute('aria-checked') === 'true' ? 'desactivado' : 'activado'));
      });
    });
    panel.querySelectorAll('[data-seg]').forEach((b) => {
      b.addEventListener('click', () => set(b.getAttribute('data-seg'), b.getAttribute('data-val')));
    });
    const r = document.getElementById('a11y-fs');
    if (r) {
      r.addEventListener('input', () => {
        const v = VALORES_FS[Number(r.value)];
        document.getElementById('a11y-fs-val').textContent = ETIQ_FS[v];
        set('fs', v);
      });
    }
    const cerrar = document.getElementById('a11y-cerrar');
    if (cerrar) cerrar.addEventListener('click', () => abrirPanel(false));
    const reset = document.getElementById('a11y-reset');
    if (reset) {
      reset.addEventListener('click', async () => {
        prefs = Object.assign({}, DEFECTO);
        escribirLocal(); aplicar(); pintarPanel();
        const dni = sesionDni();
        if (dni) { try { await fetch('/api/accesibilidad/' + dni + '/restablecer', { method: 'POST' }); } catch (e) {} }
        anunciar('Ajustes restablecidos');
      });
    }
  }

  let ultimoFoco = null;
  function abrirPanel(abrir) {
    const panel = document.getElementById('a11y-panel');
    const scrim = document.getElementById('a11y-scrim');
    const fab = document.getElementById('a11y-fab');
    if (!panel) return;
    if (abrir) {
      ultimoFoco = document.activeElement;
      panel.classList.add('open'); scrim.classList.add('open');
      document.body.classList.add('a11y-abierto');
      fab.setAttribute('aria-expanded', 'true');
      const f = panel.querySelector('button, input, a');
      if (f) f.focus();
    } else {
      panel.classList.remove('open'); scrim.classList.remove('open');
      document.body.classList.remove('a11y-abierto');
      fab.setAttribute('aria-expanded', 'false');
      if (ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
    }
  }

  // el foco no sale del panel mientras está abierto (WCAG 2.4.3)
  document.addEventListener('keydown', (e) => {
    const panel = document.getElementById('a11y-panel');
    if (!panel || !panel.classList.contains('open')) return;
    if (e.key === 'Escape') { abrirPanel(false); return; }
    if (e.key !== 'Tab') return;
    const f = panel.querySelectorAll('button, input, a, [tabindex]:not([tabindex="-1"])');
    if (!f.length) return;
    const primero = f[0], ultimo = f[f.length - 1];
    if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
    else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
  });

  // ---------------------------------------------------------------- barra superior
  function montarTopbar() {
    const host = document.querySelector('.topbar') || document.querySelector('.nav-cta');
    if (!host || host.querySelector('.topbar-a11y')) return;
    const cont = crear('div', { class: 'topbar-a11y' },
      '<button class="tb-btn" id="tb-idioma" aria-haspopup="true" aria-expanded="false" title="Cambiar idioma">' +
        svg(IC.globo, 1.8) + '<span id="tb-idioma-txt">ES</span></button>' +
      '<button class="tb-btn" id="tb-a11y" title="Panel de accesibilidad (Alt + A)" aria-label="Panel de accesibilidad">' +
        svg(IC.a11y, 2) + '</button>' +
      '<button class="tb-btn" id="tb-tema" title="Modo día y modo noche (Alt + D)" aria-label="Cambiar entre modo día y modo noche">' +
        svg(IC.luna, 1.8) + '</button>');
    host.appendChild(cont);

    const menu = crear('div', { class: 'tb-menu', id: 'tb-menu-idioma', role: 'menu' },
      Object.entries(window.I18N ? window.I18N.IDIOMAS : {}).map(([k, v]) =>
        '<button role="menuitem" data-lang="' + k + '" aria-current="' + (prefs.idioma === k) + '">' +
        v.nombre + '<span class="tag-lang">' + v.tag + '</span></button>').join(''));
    document.body.appendChild(menu);

    document.getElementById('tb-a11y').addEventListener('click', () => abrirPanel(true));
    document.getElementById('tb-tema').addEventListener('click', () => {
      set('tema', temaEfectivo() === 'noche' ? 'dia' : 'noche');
      anunciar('Modo ' + (temaEfectivo() === 'noche' ? 'noche' : 'día') + ' activado');
    });
    const bi = document.getElementById('tb-idioma');
    bi.addEventListener('click', (e) => {
      e.stopPropagation();
      const abierto = menu.classList.toggle('open');
      bi.setAttribute('aria-expanded', String(abierto));
    });
    menu.querySelectorAll('[data-lang]').forEach((b) => {
      b.addEventListener('click', () => {
        set('idioma', b.getAttribute('data-lang'));
        menu.classList.remove('open'); bi.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('click', (e) => {
      if (!menu.contains(e.target) && e.target !== bi) {
        menu.classList.remove('open'); bi.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function actualizarBotonesTopbar() {
    const t = document.getElementById('tb-idioma-txt');
    if (t) t.textContent = (prefs.idioma || 'es').toUpperCase();
    const bt = document.getElementById('tb-tema');
    if (bt) bt.innerHTML = svg(temaEfectivo() === 'noche' ? IC.sol : IC.luna, 1.8);
    const ba = document.getElementById('tb-a11y');
    if (ba) ba.classList.toggle('on', prefs.fs !== 100 || prefs.contraste !== 'normal' || prefs.voz || prefs.guia);
    const menu = document.getElementById('tb-menu-idioma');
    if (menu) menu.querySelectorAll('[data-lang]').forEach((b) =>
      b.setAttribute('aria-current', String(b.getAttribute('data-lang') === prefs.idioma)));
  }

  // ---------------------------------------------------------------- atajos de teclado
  document.addEventListener('keydown', (e) => {
    if (!prefs.atajos || !e.altKey || e.ctrlKey || e.metaKey) return;
    const k = (e.key || '').toLowerCase();
    const ir = (p) => { e.preventDefault(); location.href = rutaSistema(p); };
    if (k === 'a') { e.preventDefault(); abrirPanel(!document.getElementById('a11y-panel').classList.contains('open')); }
    else if (k === 'd') { e.preventDefault(); set('tema', temaEfectivo() === 'noche' ? 'dia' : 'noche'); }
    else if (k === 'v') { e.preventDefault(); set('voz', !prefs.voz); if (prefs.voz) leerPagina(); }
    else if (k === 'n') ir('nuevo-reclamo.html');
    else if (k === 's') ir('seguimiento.html');
    else if (k === 'l') { e.preventDefault(); const b = document.getElementById('tb-idioma'); if (b) b.click(); }
  });

  // ---------------------------------------------------------------- lectura por voz
  let vozActiva = false;
  function textoDeLaPagina() {
    const raiz = document.querySelector('main, .app-content, #contenido') || document.body;
    const partes = [];
    raiz.querySelectorAll('h1,h2,h3,p,li,label,.claim-title,.state-block b,td').forEach((el) => {
      if (el.closest('.a11y-panel, .tts-bar, .skip-link, script, style')) return;
      const t = (el.innerText || '').trim();
      if (t && t.length > 1) partes.push(t);
    });
    return partes.join('. ');
  }
  function leerPagina() {
    if (!('speechSynthesis' in window)) {
      toast('Tu navegador no tiene síntesis de voz', 'Prueba con Chrome o Edge.');
      return;
    }
    detenerVoz();
    const u = new SpeechSynthesisUtterance(textoDeLaPagina().slice(0, 7000));
    const mapa = { es: 'es-PE', en: 'en-US', qu: 'es-PE', ay: 'es-PE' };
    u.lang = mapa[prefs.idioma] || 'es-PE';
    u.rate = Number(prefs.vozVel) || 1;
    u.onend = () => { vozActiva = false; pintarVoz(); };
    window.speechSynthesis.speak(u);
    vozActiva = true;
    document.querySelector('.tts-bar').classList.add('open');
    document.getElementById('tts-txt').textContent = 'Leyendo: ' + (document.title.split('|')[0] || '').trim();
    document.getElementById('tts-sub').textContent = 'Voz del sistema · ' + u.lang + ' · ' + u.rate + '×';
    pintarVoz();
  }
  function detenerVoz() {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    vozActiva = false;
    const bar = document.querySelector('.tts-bar');
    if (bar && !prefs.voz) bar.classList.remove('open');
    pintarVoz();
  }
  function pintarVoz() {
    const b = document.getElementById('tts-play');
    if (b) b.innerHTML = svg(vozActiva ? IC.pausa : IC.play, 2.2);
  }

  // ---------------------------------------------------------------- guía de lectura
  document.addEventListener('mousemove', (e) => {
    if (!prefs.guia) return;
    const g = document.getElementById('reading-guide');
    if (g) g.style.top = (e.clientY - 23) + 'px';
  });

  // ---------------------------------------------------------------- sesión (WCAG 2.2.1)
  let tSesion = null, tAviso = null;
  function reiniciarSesion() {
    clearTimeout(tSesion); clearTimeout(tAviso);
    const aviso = document.querySelector('.sesion-aviso');
    if (aviso) aviso.classList.remove('open');
    const min = Number(prefs.sesion) || 0;
    if (!min || !sesionDni()) return;
    tAviso = setTimeout(() => {
      if (aviso) {
        aviso.classList.add('open');
        document.getElementById('sesion-txt').textContent =
          'Tu sesión vence en 2 minutos por inactividad. Lo que escribiste se conserva.';
      }
    }, Math.max(1, min - 2) * 60000);
    tSesion = setTimeout(() => {
      if (aviso) document.getElementById('sesion-txt').textContent = 'Tu sesión venció. Vuelve a iniciarla.';
    }, min * 60000);
  }
  ['click', 'keydown', 'scroll'].forEach((ev) =>
    document.addEventListener(ev, () => { if (tSesion) reiniciarSesion(); }, { passive: true }));

  // ---------------------------------------------------------------- utilidades públicas
  function anunciar(msg) {
    const l = document.getElementById('a11y-live');
    if (l) { l.textContent = ''; setTimeout(() => { l.textContent = msg; }, 60); }
  }
  function toast(titulo, msg) {
    if (window.showToast) window.showToast(titulo, msg);
    anunciar(titulo + '. ' + msg);
  }

  // ---------------------------------------------------------------- arranque
  leerLocal();
  aplicar();   // antes de pintar, para evitar el parpadeo de tema

  document.addEventListener('DOMContentLoaded', () => {
    montarBase();
    pintarPanel();
    montarTopbar();
    aplicar();
    reiniciarSesion();

    document.getElementById('a11y-fab').addEventListener('click', () => abrirPanel(true));
    document.getElementById('a11y-scrim').addEventListener('click', () => abrirPanel(false));
    const play = document.getElementById('tts-play');
    if (play) play.addEventListener('click', () => {
      if (!('speechSynthesis' in window)) return;
      if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
        window.speechSynthesis.pause(); vozActiva = false;
      } else if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume(); vozActiva = true;
      } else { leerPagina(); }
      pintarVoz();
    });
    const rs = document.getElementById('tts-restart');
    if (rs) rs.addEventListener('click', leerPagina);
    const st = document.getElementById('tts-stop');
    if (st) st.addEventListener('click', () => set('voz', false));
    const ext = document.getElementById('sesion-extender');
    if (ext) ext.addEventListener('click', reiniciarSesion);

    document.addEventListener('a11y:cambio', (e) => {
      if (e.detail.prefs.voz && !vozActiva && !window.speechSynthesis?.speaking) leerPagina();
    });

    cargarServidor();
  });

  if (window.matchMedia) {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(
      () => { if (prefs.tema === 'auto') aplicar(); });
  }

  window.A11Y = {
    DEFECTO,
    get prefs() { return Object.assign({}, prefs); },
    set, aplicar, abrirPanel, anunciar, leerPagina, detenerVoz,
    recargar: cargarServidor,
  };
})();

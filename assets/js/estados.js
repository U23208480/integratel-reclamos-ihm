// ============================================================
// INTEGRATEL PERÚ — estados.js
// Los diez estados del catálogo del AP3, como componentes reutilizables.
//
// Cada estado cumple las cuatro partes obligatorias:
//   señal visual · mensaje en lenguaje del usuario · acción de salida ·
//   permanencia de la navegación principal.
//
// Los mensajes de error van siempre en texto (nunca solo color ni ícono),
// junto al elemento que los provoca, y reciben el foco (WCAG 3.3.1).
// ============================================================
(function () {
  'use strict';

  const I = {
    vacio: '<path d="M4 8h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><path d="M7 12h7M7 15.5h4"/>',
    lupa: '<circle cx="10.6" cy="10.6" r="6.6"/><path d="M15.4 15.4 20.6 20.6M8.2 8.2l4.8 4.8M13 8.2l-4.8 4.8"/>',
    campana: '<path d="M6 16.4v-5a6 6 0 0 1 12 0v5l2 3H4z"/><path d="M10 19.4a2 2 0 0 0 4 0"/>',
    nube: '<path d="M6 17h11a4 4 0 0 0 .6-7.95 6 6 0 0 0-11.4-1.4A3.8 3.8 0 0 0 6 17z"/><path d="M3.5 20.5 20.5 3.5"/>',
    servidor: '<rect x="3" y="4.5" width="18" height="6" rx="1.6"/><rect x="3" y="13.5" width="18" height="6" rx="1.6"/><path d="M6.5 7.5h.01M6.5 16.5h.01"/><path d="M17 13.5V10"/>',
    archivo: '<path d="M14 3.4H7.4a2 2 0 0 0-2 2v13.2a2 2 0 0 0 2 2h9.2a2 2 0 0 0 2-2V8z"/><path d="M13.8 3.4V8h4.8M8.5 19.5 18 10"/>',
    escudo: '<path d="M12 3 20 6v6.2c0 5-3.6 8.2-8 9.2-4.4-1-8-4.2-8-9.2V6l8-3z"/><rect x="9" y="11" width="6" height="5" rx="1"/><path d="M10.4 11V9.6a1.6 1.6 0 0 1 3.2 0V11"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="M8.2 12.4 11 15.2l5-5.4"/>',
    alerta: '<path d="M12 3.6 2.4 20.4h19.2z"/><path d="M12 9.6v4.8M12 17.4v.01"/>',
  };
  const svg = (d, w) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' +
    (w || 1.8) + '" stroke-linecap="round" stroke-linejoin="round">' + d + '</svg>';

  // ---------------------------------------------------------------- catálogo
  // tono: '' (cian) | warn | bad | good
  const CATALOGO = {
    'vacio-inicial': {
      n: 1, etiqueta: 'Vacío inicial', ilu: I.vacio, tono: '',
      titulo: 'Todavía no tienes reclamos registrados',
      mensaje: 'Cuando registres uno, aquí vas a ver su código, su estado y la fecha en que te vamos a responder. El registro toma unos tres minutos.',
    },
    'vacio-busqueda': {
      n: 2, etiqueta: 'Vacío por búsqueda', ilu: I.lupa, tono: '',
      titulo: 'No encontramos ningún reclamo con ese código',
      mensaje: 'Revisa que el código tenga el formato REC-AAAA-NNNNN. Lo encuentras en el correo de registro o en el comprobante que descargaste.',
    },
    'vacio-historial': {
      n: 3, etiqueta: 'Vacío por historial', ilu: I.campana, tono: '',
      titulo: 'Tu bandeja de avisos está al día',
      mensaje: 'Acá te vamos a avisar cada vez que tu reclamo cambie de estado o cuando un asesor te pida información. También te llega a tu correo.',
    },
    'error_conexion': {
      n: 5, etiqueta: 'Error de conexión', ilu: I.nube, tono: 'warn',
      titulo: 'Se perdió la conexión con el servidor',
      mensaje: 'El problema está en la red, no en lo que hiciste. Nada se perdió ni se duplicó: puedes reintentar cuando vuelva la conexión.',
    },
    'error_sistema': {
      n: 6, etiqueta: 'Error del sistema', ilu: I.servidor, tono: 'bad',
      titulo: 'No pudimos cargar esta información',
      mensaje: 'El fallo es nuestro, no tuyo: el servicio no respondió. Tu reclamo sigue registrado y su plazo de atención continúa corriendo.',
    },
    'no_disponible': {
      n: 8, etiqueta: 'Contenido no disponible', ilu: I.archivo, tono: 'warn',
      titulo: 'Este reclamo ya no está disponible en línea',
      mensaje: 'Pasó al archivo histórico. Puedes pedir una copia certificada y te llega a tu correo en 48 horas.',
    },
    'no_encontrado': {
      n: 8, etiqueta: 'Contenido no disponible', ilu: I.archivo, tono: 'warn',
      titulo: 'No encontramos ese reclamo',
      mensaje: 'Revisa el código o consulta la lista de tus reclamos.',
    },
    'sin_permisos': {
      n: 9, etiqueta: 'Sin permisos', ilu: I.escudo, tono: 'warn',
      titulo: 'Tu sesión venció por inactividad',
      mensaje: 'Por seguridad cerramos la sesión tras un tiempo sin actividad. Lo que estabas revisando quedó guardado.',
    },
    'exito': {
      n: 10, etiqueta: 'Éxito', ilu: I.check, tono: 'good',
      titulo: 'Listo', mensaje: 'La operación se completó correctamente.',
    },
  };

  function botones(acciones) {
    if (!acciones || !acciones.length) return '';
    return '<div class="state-actions">' + acciones.map((a, i) => {
      const clase = 'btn ' + (i === 0 ? 'btn-primary' : 'btn-ghost');
      return a.href
        ? '<a href="' + a.href + '" class="' + clase + '">' + a.texto + '</a>'
        : '<button type="button" class="' + clase + '" data-accion="' + i + '">' + a.texto + '</button>';
    }).join('') + '</div>';
  }

  /** Dibuja uno de los estados del catálogo dentro de 'host'. */
  function pintar(host, clave, opciones) {
    const el = typeof host === 'string' ? document.querySelector(host) : host;
    if (!el) return;
    const o = opciones || {};
    const base = CATALOGO[clave] || CATALOGO['error_sistema'];
    const tono = o.tono !== undefined ? o.tono : base.tono;
    const titulo = o.titulo || base.titulo;
    const mensaje = o.mensaje || base.mensaje;

    el.innerHTML =
      '<section class="state-block" role="region" aria-labelledby="st-t" data-estado="' + clave + '">' +
      '<span class="state-tag ' + tono + '">' + (base.etiqueta || '') + '</span>' +
      '<div class="state-ilu ' + tono + '" aria-hidden="true">' + svg(base.ilu, 1.8) + '</div>' +
      '<h3 id="st-t">' + titulo + '</h3>' +
      '<p>' + mensaje + '</p>' +
      (o.detalle ? '<p class="state-meta">' + o.detalle + '</p>' : '') +
      botones(o.acciones) +
      '</section>';

    (o.acciones || []).forEach((a, i) => {
      if (a.onClick) {
        const b = el.querySelector('[data-accion="' + i + '"]');
        if (b) b.addEventListener('click', a.onClick);
      }
    });
    // los estados de error se anuncian al lector de pantalla sin robar el foco
    if (tono === 'bad' || tono === 'warn') {
      el.firstElementChild.setAttribute('aria-live', 'polite');
      if (window.A11Y) window.A11Y.anunciar(titulo + '. ' + mensaje);
    }
    return el.firstElementChild;
  }

  /** Estado 4 · carga: esqueleto con la forma real del contenido, no un spinner. */
  function cargando(host, filas, texto) {
    const el = typeof host === 'string' ? document.querySelector(host) : host;
    if (!el) return;
    const n = filas || 4;
    let html = '<div class="sk-wrap" role="status" aria-live="polite" aria-busy="true">' +
      '<div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">' +
      '<div class="progress" style="flex:1;"><i style="width:35%"></i></div>' +
      '<span style="font-size:calc(12.5px * var(--fs,1));color:var(--muted);font-weight:700;">' +
      (texto || 'Cargando tus reclamos…') + '</span></div>';
    for (let i = 0; i < n; i++) {
      html += '<div class="sk-row"><div class="sk a"></div><div class="b">' +
        '<i class="sk" style="width:' + (46 - i * 4) + '%"></i>' +
        '<i class="sk" style="width:' + (70 - i * 6) + '%;height:11px;"></i></div>' +
        '<div class="sk c"></div></div>';
    }
    html += '</div>';
    el.innerHTML = html;
    // el progreso avanza para que la espera no parezca congelada
    let p = 35;
    const barra = el.querySelector('.progress i');
    const t = setInterval(() => {
      p = Math.min(92, p + 7);
      if (barra) barra.style.width = p + '%'; else clearInterval(t);
    }, 320);
    return () => clearInterval(t);
  }

  /**
   * Decide qué estado corresponde a una respuesta de la API.
   * Devuelve true si pintó un estado (es decir, si no hay datos que mostrar).
   */
  function desdeRespuesta(host, data, opciones) {
    const o = opciones || {};
    if (!data) {
      pintar(host, 'error_conexion', { acciones: o.accionesConexion || o.acciones });
      return true;
    }
    if (data.ok === false) {
      const codigo = data.codigo ||
        ((data.error || '').indexOf('No se pudo conectar') >= 0 ? 'error_conexion' : 'error_sistema');
      pintar(host, codigo, {
        mensaje: data.error || undefined,
        detalle: data.incidente ? ('Código del incidente: ' + data.incidente + ' · ' +
          new Date().toLocaleString('es-PE')) : undefined,
        acciones: o.acciones,
      });
      return true;
    }
    return false;
  }

  // ---------------------------------------------------------------- estado 7: validación
  /**
   * Valida un formulario y pinta el resumen + los errores por campo.
   * reglas: [{ id, etiqueta, test(valor), mensaje }]
   * Devuelve true si todo está correcto.
   */
  function validar(form, reglas) {
    const el = typeof form === 'string' ? document.querySelector(form) : form;
    if (!el) return true;
    const errores = [];

    reglas.forEach((r) => {
      const campo = el.querySelector('#' + r.id);
      if (!campo) return;
      const cont = campo.closest('.field') || campo.parentElement;
      const valor = (campo.value || '').trim();
      const ok = r.test(valor, campo);
      cont.classList.toggle('invalid', !ok);
      campo.setAttribute('aria-invalid', String(!ok));

      let msg = cont.querySelector('.field-error');
      if (!msg) {
        msg = document.createElement('div');
        msg.className = 'field-error';
        cont.appendChild(msg);
      }
      msg.id = r.id + '-error';
      msg.textContent = ok ? '' : r.mensaje;
      if (ok) campo.removeAttribute('aria-describedby');
      else {
        campo.setAttribute('aria-describedby', msg.id);
        errores.push({ id: r.id, etiqueta: r.etiqueta, mensaje: r.mensaje });
      }
    });

    let sumario = el.querySelector('.error-sumario');
    if (!errores.length) { if (sumario) sumario.remove(); return true; }

    if (!sumario) {
      sumario = document.createElement('div');
      sumario.className = 'error-sumario';
      sumario.setAttribute('role', 'alert');
      sumario.setAttribute('tabindex', '-1');
      el.insertBefore(sumario, el.firstChild);
    }
    sumario.innerHTML =
      '<h3>Hay ' + errores.length + (errores.length === 1 ? ' dato que debes corregir' : ' datos que debes corregir') +
      ' antes de continuar</h3><ul>' +
      errores.map((e) => '<li>' + e.mensaje + ' <a href="#' + e.id + '" data-ir="' + e.id + '">Ir al campo ' +
        e.etiqueta + '</a></li>').join('') + '</ul>';
    sumario.querySelectorAll('[data-ir]').forEach((a) => {
      a.addEventListener('click', (ev) => {
        ev.preventDefault();
        const c = el.querySelector('#' + a.getAttribute('data-ir'));
        if (c) { c.focus(); c.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
      });
    });
    sumario.focus();   // el resumen recibe el foco al enviar (WCAG 3.3.1)
    return false;
  }

  window.Estados = { CATALOGO, pintar, cargando, desdeRespuesta, validar };
})();

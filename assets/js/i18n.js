// ============================================================
// INTEGRATEL PERÚ — i18n.js
// Cuatro idiomas: español, inglés, quechua sureño y aymara.
// El quechua y el aymara son idiomas oficiales en las zonas donde
// predominan (Constitución Política del Perú, art. 48).
//
// Traduce de dos maneras:
//   1. elementos con data-i18n="clave"   (pantallas nuevas)
//   2. un mapa de frases literales       (pantallas que ya existían)
// Además cambia el atributo lang de la página, para que el lector de
// pantalla use la pronunciación correcta (WCAG 3.1.1).
// ============================================================
(function () {
  'use strict';

  const IDIOMAS = {
    es: { tag: 'es-PE', nombre: 'Español', nativo: 'Perú' },
    en: { tag: 'en-US', nombre: 'English', nativo: 'United States' },
    qu: { tag: 'qu-PE', nombre: 'Runasimi', nativo: 'Quechua sureño' },
    ay: { tag: 'ay-PE', nombre: 'Aymar aru', nativo: 'Aymara' },
  };

  // --- frases de la interfaz. es = original; el resto, su traducción.
  const F = [
    // navegación y acciones
    ['Inicio', 'Home', 'Qallariy', 'Qalltäwi'],
    ['Nuevo reclamo', 'New complaint', 'Musuq willakuy', 'Machaq arxayawi'],
    ['Mis reclamos', 'My complaints', 'Willakuyniykuna', 'Arxayawinaka'],
    ['Seguimiento', 'Tracking', 'Qatipay', 'Arknaqäwi'],
    ['Perfil', 'Profile', 'Willañiy', 'Uñt’awi'],
    ['Notificaciones', 'Notifications', 'Willakuykuna', 'Yatiyäwinaka'],
    ['Accesibilidad', 'Accessibility', 'Haykunalla kay', 'Mantañataki'],
    ['Salir', 'Sign out', 'Lluqsiy', 'Mistuña'],
    ['Guardar', 'Save', 'Waqaychay', 'Imaña'],
    ['Guardar cambios', 'Save changes', 'Hukchasqata waqaychay', 'Mayjt’äwinak imaña'],
    ['Cancelar', 'Cancel', 'Saqiy', 'Jaytaña'],
    ['Continuar', 'Continue', 'Qatiy', 'Sarantaña'],
    ['Volver', 'Back', 'Kutiy', 'Kutt’aña'],
    ['Reintentar', 'Try again', 'Yapamanta ruway', 'Wasitat lurañcha'],
    ['Buscar', 'Search', 'Maskay', 'Thaqaña'],
    ['Descargar PDF', 'Download PDF', 'PDF urqhuy', 'PDF apaqaña'],
    ['Ver detalle', 'View details', 'Qhaway', 'Uñjaña'],
    ['Cerrar sesión', 'Sign out', 'Lluqsiy', 'Mistuña'],
    ['Iniciar sesión', 'Sign in', 'Yaykuy', 'Mantaña'],
    ['Crear cuenta', 'Create account', 'Cuentata kamay', 'Cuenta uñstayaña'],
    ['Restablecer', 'Reset', 'Kutichiy', 'Kutt’ayaña'],
    ['Restablecer todo', 'Reset everything', 'Llapanta kutichiy', 'Taqi kutt’ayaña'],
    // estados del reclamo
    ['Recibido', 'Received', 'Chaskisqa', 'Katuqata'],
    ['En proceso', 'In progress', 'Ruwachkan', 'Lurasiski'],
    ['Atendido', 'Resolved', 'Kutichisqa', 'Jaysata'],
    ['Improcedente', 'Rejected', 'Mana chaskisqa', 'Jani katuqata'],
    ['Todos', 'All', 'Llapan', 'Taqpacha'],
    // mensajes del portal
    ['Portal de Reclamos', 'Complaints Portal', 'Willakuy Punku', 'Arxayaw Punku'],
    ['Sistema de Gestión de Reclamos', 'Complaint Management System', 'Willakuy Kamachiy', 'Arxayaw Apnaqäwi'],
    ['Historial de reclamos', 'Complaint history', 'Willakuy ñawpaqkuna', 'Arxayaw nayrïrinaka'],
    ['Reclamos registrados', 'Registered complaints', 'Qillqasqa willakuykuna', 'Qillqata arxayawinaka'],
    ['Pendientes de revisión', 'Awaiting review', 'Qhawanapaq', 'Uñakipañataki'],
    ['Siendo evaluados', 'Being evaluated', 'Qhawachkan', 'Uñakipasiski'],
    ['Resueltos', 'Resolved', 'Kutichisqa', 'Jaysata'],
    ['Total', 'Total', 'Llapan', 'Taqpacha'],
    ['Recibidos', 'Received', 'Chaskisqakuna', 'Katuqatanaka'],
    ['Atendidos', 'Resolved', 'Kutichisqakuna', 'Jaysatanaka'],
    ['Aún no tienes reclamos registrados', 'You have no complaints yet',
     'Manaraq willakuyniyki kanchu', 'Janïr arxayawimäkiti'],
    ['Cuando registres uno, aparecerá aquí con su número de seguimiento.',
     'Once you register one, it will appear here with its tracking number.',
     'Hukta qillqaptiyki, kaypim rikurinqa qatipana yupaywan.',
     'Mä qillqantäta, akanwa uñstani arknaqaw jakhuwimpi.'],
    ['Registrar mi primer reclamo', 'Register my first complaint',
     'Ñawpaq willakuyniyta qillqay', 'Nayrïr arxayawija qillqantaña'],
    // accesibilidad
    ['Tamaño de texto', 'Text size', 'Qillqa sayay', 'Qillqa jach’a'],
    ['Modo noche', 'Dark mode', 'Tuta rikchay', 'Aruma uñacht’awi'],
    ['Alto contraste', 'High contrast', 'Sinchi t’ikray', 'Jach’a mayjt’awi'],
    ['Lectura por voz', 'Read aloud', 'Kunkawan ñawinchay', 'Arumpi ullaña'],
    ['Reducir movimiento', 'Reduce motion', 'Kuyuyta pisiyachiy', 'Unxtaw pisicht’aña'],
    ['Resaltar enlaces', 'Highlight links', 'Tinkikunata rikuchiy', 'Chinuwinak uñacht’aña'],
    ['Tipografía legible', 'Legible typeface', 'Ñawinchana qillqa', 'Ullañ qillqa'],
    ['Idioma', 'Language', 'Simi', 'Aru'],
    ['Idioma de la interfaz', 'Interface language', 'Panqapa simin', 'Uñstawin arupa'],
    ['Lectura fácil', 'Easy read', 'Facil ñawinchay', 'Jasa ullaña'],
    ['Activado', 'On', 'Kichasqa', 'Jist’arata'],
    ['Desactivado', 'Off', 'Wichqasqa', 'Jist’antata'],
    ['Saltar al contenido principal', 'Skip to main content',
     'Hatun qillqaman pasay', 'Jach’a qillqaru saraña'],
    ['Se guarda en tu cuenta', 'Saved to your account',
     'Cuentaykipim waqaychakun', 'Cuentamanwa imantasi'],
    ['Ver todos los ajustes', 'See all settings', 'Llapan allichaykunata qhaway', 'Taqi askichäwinak uñjaña'],
    // baja de cuenta
    ['Eliminar mi cuenta', 'Delete my account', 'Cuentayta pichay', 'Cuentaja chhaqtayaña'],
    ['Eliminar cuenta', 'Delete account', 'Cuentata pichay', 'Cuenta chhaqtayaña'],
    ['Recuperar mi cuenta', 'Restore my account', 'Cuentayta kutichiy', 'Cuentaja kutt’ayaña'],
    ['Tu cuenta fue eliminada', 'Your account was deleted',
     'Cuentayki pichasqaña', 'Cuentamax chhaqtayatawa'],
    // errores y estados
    ['No se pudo conectar con el servidor.', 'Could not reach the server.',
     'Mana servidorwan tinkiyta atinchu.', 'Janiw servidorampi chikachasiñ atkiti.'],
    ['Sin conexión a internet', 'No internet connection',
     'Mana internet tinkiy', 'Jani internet chinuwi'],
    ['Cargando…', 'Loading…', 'Chaqnachkan…', 'Apkatasiski…'],
    ['Hubo un problema', 'Something went wrong', 'Huk sasachakuy karqa', 'Mä jan waltäwiwa utjäna'],
  ];

  const DICC = { en: {}, qu: {}, ay: {} };
  F.forEach(([es, en, qu, ay]) => { DICC.en[es] = en; DICC.qu[es] = qu; DICC.ay[es] = ay; });

  // claves cortas para las pantallas nuevas (data-i18n)
  const CLAVES = {
    es: {}, // el HTML ya está en español
    en: {
      'a11y.titulo': 'Accessibility', 'a11y.sub': 'Settings are applied instantly and saved to your account.',
      'a11y.visual': 'Visual', 'a11y.auditivo': 'Audio', 'a11y.navegacion': 'Navigation and keyboard',
      'a11y.idioma': 'Language and easy read', 'a11y.resumen': 'Conformance summary',
      'estados.titulo': 'Screen states', 'baja.titulo': 'Delete my account',
    },
    qu: {
      'a11y.titulo': 'Haykunalla kay', 'a11y.sub': 'Allichaykunaqa kunallanmi ruwakun, cuentaykipitaq waqaychakun.',
      'a11y.visual': 'Qhawanapaq', 'a11y.auditivo': 'Uyarinapaq', 'a11y.navegacion': 'Purinapaq',
      'a11y.idioma': 'Simi', 'a11y.resumen': 'Pisi willakuy',
      'estados.titulo': 'Panqapa kaynin', 'baja.titulo': 'Cuentayta pichay',
    },
    ay: {
      'a11y.titulo': 'Mantañataki', 'a11y.sub': 'Askichäwinakax jank’akiw lurasi, cuentamanwa imantasi.',
      'a11y.visual': 'Uñjañataki', 'a11y.auditivo': 'Ist’añataki', 'a11y.navegacion': 'Sarnaqañataki',
      'a11y.idioma': 'Aru', 'a11y.resumen': 'Juk’a yatiyawi',
      'estados.titulo': 'Uñstawin saranakapa', 'baja.titulo': 'Cuentaja chhaqtayaña',
    },
  };

  let actual = 'es';
  const ORIGINALES = new WeakMap();   // nodo -> texto en español

  function guardarOriginal(nodo, prop, valor) {
    let m = ORIGINALES.get(nodo);
    if (!m) { m = {}; ORIGINALES.set(nodo, m); }
    if (!(prop in m)) m[prop] = valor;
    return m[prop];
  }

  function traducirTexto(txt, lang) {
    const limpio = (txt || '').trim();
    if (!limpio) return txt;
    if (lang === 'es') return txt;
    const t = DICC[lang] && DICC[lang][limpio];
    if (!t) return txt;
    return txt.replace(limpio, t);
  }

  function aplicar(lang) {
    if (!IDIOMAS[lang]) lang = 'es';
    actual = lang;
    document.documentElement.setAttribute('lang', IDIOMAS[lang].tag);
    document.documentElement.setAttribute('data-idioma', lang);

    // 1. elementos con data-i18n
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const clave = el.getAttribute('data-i18n');
      const base = guardarOriginal(el, 'text', el.textContent);
      const tabla = CLAVES[lang] || {};
      el.textContent = tabla[clave] || base;
    });

    // 2. nodos de texto que coincidan con el mapa de frases
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const p = n.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        const tag = p.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'CODE') return NodeFilter.FILTER_REJECT;
        if (p.closest('[data-no-traducir]')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodos = [];
    while (walker.nextNode()) nodos.push(walker.currentNode);
    nodos.forEach((n) => {
      const base = guardarOriginal(n, 'txt', n.nodeValue);
      n.nodeValue = lang === 'es' ? base : traducirTexto(base, lang);
    });

    // 3. placeholders, títulos y etiquetas accesibles
    document.querySelectorAll('[placeholder],[title],[aria-label]').forEach((el) => {
      ['placeholder', 'title', 'aria-label'].forEach((attr) => {
        if (!el.hasAttribute(attr)) return;
        const base = guardarOriginal(el, attr, el.getAttribute(attr));
        el.setAttribute(attr, lang === 'es' ? base : traducirTexto(base, lang));
      });
    });

    document.dispatchEvent(new CustomEvent('idioma:cambio', { detail: { lang } }));
  }

  window.I18N = {
    IDIOMAS,
    get actual() { return actual; },
    aplicar,
    t(clave) { return (CLAVES[actual] && CLAVES[actual][clave]) || clave; },
    frase(es) { return actual === 'es' ? es : traducirTexto(es, actual); },
  };
})();

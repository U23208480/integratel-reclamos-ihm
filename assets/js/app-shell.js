// ============================================================
// INTEGRATEL PERÚ — app-shell.js (shared across sistema/*.html)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();

  const toggle = document.getElementById('btn-sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // barra de navegacion inferior (solo movil), segun el diseño en Figma
  if (sidebar && !document.getElementById('bottom-nav')) {
    const here = location.pathname.split('/').pop();
    const items = [
      ['Inicio', 'nuevo-reclamo.html', 'M3 11l9-8 9 8M5 10v10h14V10'],
      ['Reclamos', 'mis-reclamos.html', 'M9 5h10M9 12h10M9 19h10M4 5h.01M4 12h.01M4 19h.01'],
      ['Seguimiento', 'mis-reclamos.html', 'M12 6v6l4 2M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z'],
      ['Perfil', 'perfil.html', 'M20 21a8 8 0 0 0-16 0M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z'],
    ];
    const nav = document.createElement('nav');
    nav.id = 'bottom-nav';
    nav.innerHTML = items.map(([t, href, d], i) => {
      const active = (i !== 2) && href === here ? ' class="active"' : '';
      return `<a href="${href}"${active}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${d}"/></svg><span>${t}</span></a>`;
    }).join('');
    document.body.appendChild(nav);
  }

  // shared identity chip + logout, present on every app-shell page
  if (window.Reclamos) {
    const nombreEl = document.getElementById('side-nombre');
    const dniEl = document.getElementById('side-dni');
    const avatarEl = document.getElementById('side-avatar');
    const nombre = Reclamos.getSessionNombre() || 'Usuario';
    if (nombreEl) nombreEl.textContent = nombre;
    if (dniEl) dniEl.textContent = 'DNI ' + (Reclamos.getSession() || '—');
    if (avatarEl) avatarEl.textContent = nombre.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', () => { Reclamos.clearSession(); window.location.href = 'index.html'; });

    // asistente de voz con agente de IA (Proyecto Final): solo con sesión iniciada
    if (Reclamos.getSession() && sidebar && !window.__asistente) {
      const s = document.createElement('script');
      s.src = '../assets/js/asistente.js';
      document.body.appendChild(s);
    }
  }
});

// ---------------------------------------------------------------- toast (shared copy, in case main.js isn't loaded)
function showToast(title, msg, ms = 4200) {
  let wrap = document.getElementById('toast-wrap');
  if (!wrap) { wrap = document.createElement('div'); wrap.id = 'toast-wrap'; document.body.appendChild(wrap); }
  const el = document.createElement('div');
  el.className = 'toast';
  el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg><div><b>${title}</b><span>${msg}</span></div>`;
  wrap.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateX(30px)'; setTimeout(() => el.remove(), 300); }, ms);
}
window.showToast = showToast;

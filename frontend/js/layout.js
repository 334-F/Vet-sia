/**
 * layout.js · Inyecta el navbar y el footer en todas las páginas
 *
 * En lugar de duplicar el HTML del navbar en cada página, se genera
 * dinámicamente desde aquí. Esto permite cambiar la navegación en
 * un solo sitio.
 */
(function() {

  function renderNavbar() {
    const user = window.VETESIA.auth.getUser();
    const isAdmin = window.VETESIA.auth.isAdmin();

    const menuUsuario = user ? `
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
          👤 ${window.VETESIA.ui.escapeHtml(user.nombre)}
        </a>
        <ul class="dropdown-menu dropdown-menu-end">
          <li><a class="dropdown-item" href="/pages/mi-cuenta.html">Mi cuenta</a></li>
          <li><a class="dropdown-item" href="/pages/mis-pedidos.html">Mis pedidos</a></li>
          <li><a class="dropdown-item" href="/pages/mis-direcciones.html">Mis direcciones</a></li>
          ${isAdmin ? '<li><hr class="dropdown-divider"></li><li><a class="dropdown-item" href="/pages/admin.html">⚙️ Panel admin</a></li>' : ''}
          <li><hr class="dropdown-divider"></li>
          <li><a class="dropdown-item" href="#" onclick="VETESIA.auth.logout(); return false;">Cerrar sesión</a></li>
        </ul>
      </li>
    ` : `
      <li class="nav-item"><a class="nav-link" href="/pages/login.html">Iniciar sesión</a></li>
      <li class="nav-item"><a class="nav-link" href="/pages/registro.html">Registrarse</a></li>
    `;

    return `
      <nav class="navbar navbar-expand-lg navbar-vetesia sticky-top">
        <div class="container">
          <a class="navbar-brand" href="/">🐾 VetÉsia</a>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarMain">
            <ul class="navbar-nav me-auto">
              <li class="nav-item"><a class="nav-link" href="/pages/catalogo.html">Catálogo</a></li>
              <li class="nav-item"><a class="nav-link" href="/pages/catalogo.html?categoria=5">Uniformidad</a></li>
            </ul>
            <ul class="navbar-nav">
              <li class="nav-item">
                <a class="nav-link" href="/pages/carrito.html">
                  🛒 Carrito <span class="badge-cart" style="display:none">0</span>
                </a>
              </li>
              ${menuUsuario}
            </ul>
          </div>
        </div>
      </nav>
    `;
  }

  function renderFooter() {
    return `
      <footer class="footer-vetesia">
        <div class="container">
          <div class="row">
            <div class="col-md-4 mb-3">
              <h5>VetÉsia</h5>
              <p class="small">Productos veterinarios y uniformidad técnica personalizable para profesionales y particulares.</p>
            </div>
            <div class="col-md-2 mb-3">
              <h6>Tienda</h6>
              <ul class="list-unstyled small">
                <li><a href="/pages/catalogo.html">Catálogo</a></li>
                <li><a href="/pages/catalogo.html?categoria=5">Uniformidad</a></li>
                <li><a href="/pages/catalogo.html?categoria=1">Alimentación</a></li>
              </ul>
            </div>
            <div class="col-md-3 mb-3">
              <h6>Mi cuenta</h6>
              <ul class="list-unstyled small">
                <li><a href="/pages/login.html">Iniciar sesión</a></li>
                <li><a href="/pages/registro.html">Registrarse</a></li>
                <li><a href="/pages/mis-pedidos.html">Mis pedidos</a></li>
              </ul>
            </div>
            <div class="col-md-3 mb-3">
              <h6>Contacto</h6>
              <ul class="list-unstyled small">
                <li>📧 info@vetesia.com</li>
                <li>📞 900 000 000</li>
                <li>Calle Mayor 1, 28001 Madrid</li>
              </ul>
            </div>
          </div>
          <div class="footer-bottom text-center">
            <p class="mb-0">© 2026 VetÉsia · Proyecto académico DAW · IES Pío Baroja</p>
          </div>
        </div>
      </footer>
    `;
  }

  function init() {
    const navHolder = document.getElementById('navbar-holder');
    if (navHolder) navHolder.innerHTML = renderNavbar();

    const footerHolder = document.getElementById('footer-holder');
    if (footerHolder) footerHolder.innerHTML = renderFooter();

    window.VETESIA.cart.inicializarBadge();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

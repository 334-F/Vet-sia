/**
 * config.js · Configuración global del frontend de VetÉsia
 *
 * Cambia API_BASE_URL según el entorno:
 *   - Local sin Docker:  http://localhost:5000/api
 *   - Local con Docker:  /api (Nginx hace de proxy)
 *   - Producción:        https://api.vetesia.com/api
 */
window.VETESIA = window.VETESIA || {};

window.VETESIA.config = {
  API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? (window.location.port === '5500' || window.location.port === '8080'
        ? 'http://localhost:5000/api'
        : '/api')
    : '/api',
  STRIPE_PUBLISHABLE_KEY: 'pk_test_cambia_esto_por_tu_clave',
  APP_NAME: 'VetÉsia',
};

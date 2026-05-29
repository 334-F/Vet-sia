# Guía de entrega · VetÉsia
## Qué tenéis que hacer entre hoy y la entrega final

Documento práctico con los pasos exactos para cumplir los requisitos de entrega que pide el centro:

> - Aplicación final. Enlace al repositorio.
> - Presentación (PowerPoint o Canva).
> - Documentación completa.
> - Enlace al website desplegado.
> - **IMPRESCINDIBLE**: Vídeo explicativo Ó link del sitio desplegado.
> - Registro de Participación rellena.

---

## ✅ Checklist final

| # | Requisito | Estado |
|---|---|---|
| 1 | Repositorio GitHub con el código | Pendiente (lo hacéis vosotros, 5 min) |
| 2 | Aplicación desplegada o vídeo | Elegir una opción (ver más abajo) |
| 3 | Presentación PowerPoint/Canva | Pendiente (plantilla más abajo) |
| 4 | Documentación completa | ✅ Hecha (los 2 docs Word) |
| 5 | Registro de Participación | Lo rellena Felipe a mano |

---

## 1. Subir a GitHub (15 min)

Necesitáis una cuenta de GitHub (cualquiera del grupo vale, o crear una de grupo).

```bash
# Descomprime el ZIP en una carpeta llamada vetesia/
cd vetesia

git init
git add .
git commit -m "Proyecto final VetEsia"

# En GitHub, crear un nuevo repositorio llamado "vetesia" (puede ser privado)
# Luego conectar el local con el remoto:
git remote add origin https://github.com/TUUSUARIO/vetesia.git
git branch -M main
git push -u origin main
```

**Importante**: el archivo `backend/.env` está en `.gitignore` y NO se sube. Está bien que sea así; las claves no deben estar en el repositorio público.

---

## 2. Desplegar o grabar vídeo (elegir UNA)

### Opción A: Desplegar en Render.com (gratis, 30-45 min)

Render permite desplegar Flask + MySQL gratis. Pasos:

1. **Crear cuenta** en https://render.com con la cuenta de GitHub.

2. **Crear la base de datos MySQL**:
   - Dashboard → "New +" → "PostgreSQL" → ⚠️ Render no tiene MySQL gratis. Usar **MySQL en PlanetScale** (gratis) o **MySQL de Aiven** (free tier).
   - Alternativa más fácil: cambiar `DATABASE_URL` a SQLite para la demo (`sqlite:///vetesia.db`) y olvidarse de MySQL externo. Para vuestra entrega académica funciona igual.

3. **Crear el backend** (Web Service):
   - "New +" → "Web Service" → conectar el repo de GitHub
   - **Root directory**: `backend`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn run:app`
   - **Environment**: añadir todas las variables de `.env.example` con valores reales

4. **Crear el frontend** (Static Site):
   - "New +" → "Static Site" → mismo repo
   - **Root directory**: `frontend`
   - **Publish directory**: `.` (la raíz del frontend)

5. **Conectar frontend con backend**:
   - Editar `frontend/js/config.js` y poner la URL del backend de Render
   - Hacer commit y push, Render redespliega automáticamente

6. **Pasar el enlace a la profesora**: algo como `https://vetesia.onrender.com`

### Opción B: Vídeo explicativo (mucho más fácil, 1 hora)

Si el despliegue da problemas, grabar un vídeo cumple el mismo requisito.

**Herramientas gratuitas para grabar**:
- **OBS Studio** (https://obsproject.com): la mejor opción, gratis, sin marca de agua
- **Loom** (https://loom.com): online, fácil, sin instalar, hasta 5 minutos gratis
- **Windows Game Bar** (Win+G en Windows): ya viene instalado
- **QuickTime** en Mac

**Qué grabar (5-10 minutos)**:

1. **Intro (30 seg)**: "Hola, somos el grupo 4 de DAW del IES Pío Baroja. Presentamos VetÉsia, una tienda online de productos veterinarios y uniformidad personalizable."

2. **Demo del cliente (3-4 min)**:
   - Abrir la home → mostrar productos destacados
   - Catálogo → filtrar por categoría "Uniformidad"
   - Ficha de bata veterinaria → elegir servicio Premium Bordado, escribir personalización
   - Añadir al carrito
   - Añadir un producto veterinario también (alimentación)
   - Ver carrito, ir al checkout
   - Loguearse como `maria@example.com / cliente123`
   - Elegir dirección, zona Península, método tarjeta
   - Confirmar pedido → "Para esta demo usaríamos la tarjeta 4242 4242 4242 4242"
   - Página de confirmación → descargar factura PDF y mostrarla

3. **Demo del admin (2-3 min)**:
   - Cerrar sesión, loguearse como `admin@vetesia.com / admin123`
   - Panel admin → ver el pedido que acaba de hacer María
   - Cambiar estado a "preparando", luego "enviado"
   - Ir a Productos → editar uno, mostrar cómo se gestiona el stock
   - Ir a Informes → mostrar el stock bajo y los más vendidos

4. **Cierre técnico (1-2 min)**:
   - Mostrar el repositorio en GitHub
   - Mencionar la arquitectura: "Frontend en HTML+Bootstrap+JS, backend en Flask con Python, base de datos MySQL, pagos con Stripe, contenedores Docker"
   - "Toda la documentación está en la carpeta docs/"

**Dónde subirlo**: YouTube (sin listar), Google Drive con permiso público de visualización, o Loom directamente.

---

## 3. Presentación (PowerPoint o Canva)

**Plantilla recomendada** (15-20 slides, 1 minuto por slide para una defensa de 15-20 min):

1. **Portada**: VetÉsia, logo, integrantes, fecha
2. **Índice**: lo que vais a ver
3. **El problema**: ¿qué necesidad cubrimos? Tienda online especializada
4. **Solución**: VetÉsia = productos veterinarios + uniformidad personalizable
5. **Usuarios objetivo**: dueños de mascotas y profesionales veterinarios
6. **Funcionalidades principales**: catálogo, carrito, pago, facturas, reseñas
7. **Roles**: cliente vs administrador (tabla de funcionalidades)
8. **Arquitectura técnica**: diagrama con frontend, backend, BBDD, Stripe
9. **Pila tecnológica**: lista de tecnologías con iconos
10. **Diagrama BBDD**: captura del diseño de las 14 tablas
11. **Diagrama de clases**: foto del modelo orientado a objetos
12. **Demo en vivo**: cambiar a la web durante 5 minutos para enseñarla
13. **Reparto de trabajo**: tabla de quién hizo qué
14. **Respuesta a las correcciones**: qué nos pidió la tutora y cómo lo hemos resuelto
15. **Dificultades encontradas**: ej. coordinación frontend-backend, integración Stripe
16. **Lo que aprendimos**: 3-4 bullets
17. **Mejoras futuras**: 3-4 bullets de lo que no dio tiempo
18. **Gracias / Preguntas**: portada de cierre

**Recursos visuales gratuitos**:
- **Canva** (https://canva.com): plantillas listas para presentaciones de proyecto
- **Iconos**: https://fontawesome.com o https://lucide.dev
- **Capturas de pantalla**: Win+Shift+S en Windows, Cmd+Shift+4 en Mac

---

## 4. Documentación completa

Ya está hecha. Entregad estos dos archivos:

- **01_VetEsia_Documento_Maestro.docx**: documento principal del grupo
- **02_VetEsia_Defensa_Felipe.docx**: defensa individual de Felipe

(Si Samuel y Jean Paul necesitan también una defensa individual cada uno, decídmelo y os los preparo).

---

## 5. Registro de Participación

Felipe lo rellena a mano según lo que cada uno haya hecho realmente. Si necesitas referencia de qué ha hecho cada uno según este proyecto:

| Persona | Tareas |
|---|---|
| Felipe Xu | Diseño BBDD, modelos SQLAlchemy, API REST completa, autenticación JWT, lógica de precios y promociones, generación de facturas PDF con ReportLab, integración Stripe, envío de emails, panel de administración (lógica backend), documentación técnica |
| Samuel Marugán | Diseño frontend HTML/CSS, todas las páginas (catálogo, ficha, carrito, checkout, cuenta, admin), integración con la API REST, validaciones de formularios, responsive |
| Jean Paul Milachay | Configuración Docker y Docker Compose, Dockerfile del backend, configuración Nginx, despliegue en VPS / Render, configuración HTTPS, optimizaciones de seguridad |

---

## ¿Algo más que necesites?

Si en cualquier momento un paso no funciona o necesitas ayuda con algo, dímelo. En particular:

- Si tras intentar desplegar en Render hay errores, mándame los logs y te ayudo
- Si necesitas guion concreto de qué decir en cada momento del vídeo
- Si quieres que te haga la presentación directamente (la genero en PowerPoint si me lo pides)
- Si Samuel o Jean Paul también necesitan documento de defensa individual

**Buena suerte con la entrega.**

# Documentación de Arquitectura, Migración a Firebase y Módulos del Sistema

Este documento describe de manera clara y detallada la arquitectura, cambios implementados, migración a Firebase y funcionamiento de los nuevos módulos para la sustentación ante la docente.

---

## 1. Mantenimiento del Patrón Modelo - Vista - Controlador (MVC)

El proyecto mantiene rigurosamente el patrón arquitectónico **MVC (Model - View - Controller)** sin alteraciones destructivas, implementando cada requerimiento de forma modular:

```
Tech_e-commerce/
│
├── models/                         # MODELO (Lógica de Datos y Reglas de Negocio)
│   ├── entities.py                 # Entidad Product con tipado inmutable
│   ├── catalog.py                  # Capa de acceso y consultas unificadas
│   ├── firebase_db.py              # Cliente REST nativo para Firebase Realtime Database
│   ├── auth_model.py               # Registro, autenticación y hash seguro de contraseñas
│   └── database.py                 # Manejo y soporte de conexión local
│
├── templates/                      # VISTA (Presentación e Interfaces de Usuario)
│   ├── base.html                   # Layout público maestro (Landing, Tienda, Carrito)
│   ├── index.html                  # Landing Page introductoria (Hero, Beneficios VIP, Carruseles, Contacto)
│   ├── shop.html                   # Tienda Oficial dedicada (Buscador, Filtros, Grilla, Paginación)
│   ├── product_detail.html         # Ficha técnica detallada de cada producto y visor 3D
│   ├── cart.html                   # Carrito de compras, cupones, descuento VIP y checkout autocompletado
│   ├── my_orders.html              # Historial de pedidos del cliente autenticado
│   ├── auth/                       # Vistas de Autenticación
│   │   ├── login.html              # Formulario de inicio de sesión con selector mostrar/ocultar contraseña
│   │   └── register.html           # Formulario de registro de clientes y programa de beneficios VIP
│   └── admin/                      # Vistas del Panel Administrativo Independiente
│       ├── base_admin.html         # Layout administrativo exclusivo con Sidebar Slider
│       ├── dashboard.html          # Panel de métricas e indicadores KPI
│       ├── products.html           # Inventario general con acciones de edición/eliminación
│       ├── product_form.html       # Formulario para crear y editar productos
│       ├── categories.html         # Gestión de categorías, ajuste de precios por categoría y cupones
│       ├── orders.html             # Gestión de pedidos y actualización atómica de stock
│       └── clients.html            # Gestión de usuarios y cambio de roles (cliente, vip, admin)
│
├── static/
│   ├── css/
│   │   ├── styles.css              # Estilos de la Tienda Pública y componentes compartidos
│   │   ├── admin.css               # Estilos exclusivos del Portal Administrativo
│   │   └── product-3d.css          # Estilos exclusivos del Visor e Inspector 3D
│
├── controllers/                    # CONTROLADOR (Rutas, Orquestación y Lógica Web)
│   ├── shop_controller.py          # Rutas de Landing (/), Tienda (/tienda), Carrito, Cupones y Mis Pedidos
│   ├── auth_controller.py          # Autenticación (/login, /registro, /logout), RBAC y aislamiento de carrito
│   ├── admin_controller.py         # Módulo administrativo protegido (/admin/*)
│   ├── admin_dash.py               # Analítica integral interactiva en Plotly Dash (/admin/analytics/)
│   └── api_controller.py           # API REST JSON (/api/v1/*) para operaciones asíncronas
│
├── configs/
│   └── settings.py                 # Variables de entorno y configuración de SQLite/Firebase
│
├── scripts/
│   ├── init_db.py                  # Inicialización completa de SQLite con catálogo, usuarios y cupones semilla
│   └── migrate_to_firebase.py      # Script de migración y población masiva en Firebase
│
└── tests/                          # Pruebas automatizadas Python y JavaScript
    ├── test_api.py                 # API, catálogo y cálculos COP
    ├── test_auth_admin.py          # Autenticación y permisos
    ├── test_orders.py              # Checkout y pedidos
    └── product-3d.test.js          # Componentes y especificaciones 3D
```

---

## 2. Migración a Firebase Realtime Database

### ¿Por qué Firebase Realtime Database?
Firebase aloja en la nube los datos del catálogo cuando se selecciona ese backend y los registros de usuario. La aplicación también utiliza SQLite para los pedidos y puede usarlo para el catálogo. Por lo tanto, Firebase no implica que todos los datos del sistema se guarden en la nube; configura respaldos y persistencia para ambos almacenamientos.

### Configuración de Conexión
La configuración se centraliza en `.env` y `configs/settings.py`. Define `FIREBASE_DATABASE_URL`, `FIREBASE_PROJECT_ID`, `FIREBASE_API_KEY`, `FIREBASE_AUTH_DOMAIN` y `FIREBASE_STORAGE_BUCKET` con valores del proyecto Firebase autorizado para el equipo. No incluyas claves, tokens ni archivos `.env` en documentación pública o commits.

### Estructura de Datos en Firebase
La base de datos en tiempo real organiza la información bajo los siguientes nodos raíz:
- `/categories`: Objeto JSON con las categorías principales (`id_main_cat`, `nombre`, `descripcion`).
- `/subcategories`: Subcategorías asociadas a cada categoría principal.
- `/brands`: Listado de fabricantes y marcas.
- `/products`: 3,718 productos tecnológicos con campos: `id_producto`, `nombre`, `descripcion`, `precio`, `stock`, `rating`, `reviews_count`, `marca`, `categoria`, `subcategoria`, `image_url`.
- `/users`: Usuarios registrados con contraseñas protegidas mediante hash de `werkzeug.security` (PBKDF2-SHA256).

### Script de Migración Automatizado
Se creó el script ejecutable:
```bash
python scripts/migrate_to_firebase.py
```
El script lee el dataset CSV (`amazon_tech_products_ecommerceGKALI.csv`) y carga el catálogo en Firebase. Revisa su configuración y el código de carga de usuarios antes de ejecutarlo; no lo uses contra datos reales o un proyecto compartido sin autorización y sin cambiar las credenciales de demostración.

---

## 3. Separación de Landing Page e Interfaz de Tienda

Siguiendo la indicación docente:
1. **Landing Page (`/`)**:
   - **Hero Introductorio**: Presentación corporativa con llamado a la acción directo ("Ir a la Tienda").
   - **Carrusel de Categorías**: Carrusel interactivo con botones anterior/siguiente y desplazamiento suave, con iconos vectoriales SVG para cada línea de producto.
   - **Carrusel de Productos Más Comprados**: Muestra los productos con mayor calificación y reseñas del catálogo.
   - **Pilares de Confianza**: Garantía oficial directa, envíos nacionales asegurados, precios claros en COP y soporte técnico.
   - **Información de Contacto y Formulario Funcional**: Datos corporativos (dirección, teléfono, correo, horarios) y formulario de mensaje directo.
   - **Pie de Página Profesional**: Enlaces de navegación rápida, categorías y soporte.
   - **Cero emojis**: Toda la iconografía utiliza gráficos SVG vectoriales profesionales.
   - **Sin badges técnicos de base de datos**: No se expone información de infraestructura al usuario final.

2. **Tienda Oficial (`/tienda` o `/catalogo`)**:
   - Página independiente dedicada 100% al comercio electrónico.
   - Barra de búsqueda por texto, filtro dinámico por categoría y ordenamiento (destacados, precio asc/desc, calificación).
   - Grilla responsive con botones para agregar al carrito en tiempo real.
   - Paginación dinámica (24 productos por página).

---

## 4. Sistema de Autenticación y Control de Acceso (RBAC)

### Rutas de Autenticación (`controllers/auth_controller.py`)
- `GET /login` y `POST /login`: Validación de credenciales contra Firebase con redirección según rol.
- `GET /registro` y `POST /registro`: Formulario para nuevos clientes, validación de formato de correo y longitud de contraseña, almacenamiento del hash y sesión automática.
- `GET /logout`: Cierre de sesión y limpieza de contexto.

### Decoradores de Seguridad
- `@login_required`: Restringe el acceso a usuarios autenticados.
- `@admin_required`: Restringe el acceso únicamente a usuarios cuyo rol sea `admin`. Si un cliente intenta acceder, el sistema deniega el acceso y lo devuelve con una alerta.

Para pruebas, registra una cuenta de cliente desde la aplicación o crea una cuenta administrativa con `scripts/create_admin.py`. Usa contraseñas únicas y seguras; los valores predeterminados del script son solo para desarrollo y deben reemplazarse.

---

## 5. Panel Administrativo Independiente con Sidebar Slider

El panel de administración (`/admin`) es un entorno aislado del portal de clientes:
- **Layout Independiente (`templates/admin/base_admin.html`)**: No comparte el menú ni el pie de página de la tienda pública.
- **Sidebar Colapsible (Slider)**:
  - En pantallas grandes (escritorio), cuenta con un botón en la barra superior para contraer y expandir el menú lateral con animación suave.
  - En dispositivos móviles y tablets, el sidebar se convierte en un cajón flotante (*drawer slider*) con botón de cierre y fondo con desenfoque (*backdrop*).
- **Módulos Disponibles**:
  1. **Dashboard (`/admin/dashboard`)**: Tarjetas de métricas en tiempo real (Total Productos, Total Categorías, Clientes Registrados, Unidades en Stock y Valoración en USD), productos más demandados y clientes recientes.
  2. **Inventario de Productos (`/admin/productos`)**: Tabla con imágenes en miniatura, búsqueda, filtro por categoría, badges de estado de stock y botones para crear, editar y eliminar.
  3. **Creación / Edición de Producto (`/admin/productos/nuevo`, `/admin/productos/editar/<id>`)**: Formulario completo para registrar o modificar productos en Firebase.
  4. **Gestión de Categorías (`/admin/categorias`)**: Visualización de categorías, conteo de productos vinculados, formulario para agregar nueva categoría, edición rápida y eliminación.
  5. **Gestión de Clientes (`/admin/clientes`)**: Listado completo de usuarios registrados, roles, teléfonos, ciudad y fecha de registro.

---

## 6. Bitácora Técnica: Qué se Hizo y Con Qué Finalidad

Esta sección documenta las mejoras implementadas en el sistema, organizadas por área funcional, detallando **qué se construyó** y **cuál es su finalidad técnica y de negocio**.

### 6.1. Modelo Relacional Unificado en SQLite y Roles de Usuario (`cliente`, `vip`, `admin`)
* **¿Qué se hizo?**
  * Se consolidó SQLite 3 (`database/lepetit.sqlite3`) como motor relacional principal autónomo, añadiendo la tabla `usuarios` con restricción `CHECK (rol IN ('admin', 'cliente', 'vip')) DEFAULT 'cliente'`, la relación `orders.user_id` y la tabla `cupones`.
  * Se creó el script `scripts/init_db.py` que inicializa automáticamente las 3,718 referencias del CSV, las categorías, los 3 usuarios de prueba por rol y los cupones promocionales semilla.
* **¿Con qué finalidad?**
  * Permitir que cualquier integrante del equipo o evaluador ejecute el proyecto localmente en cualquier sistema operativo sin depender de credenciales externas en la nube, garantizando integridad referencial y soporte nativo para tres niveles de acceso (`cliente`, `vip` y `admin`).

### 6.2. Programa de Beneficios VIP, Autocompletado de Checkout y Vista *Mis Pedidos*
* **¿Qué se hizo?**
  * **Descuento VIP automático:** En `services/cart_service.py`, cuando el usuario autenticado tiene rol `vip`, el carrito calcula y descuenta automáticamente un **10% preferencial** sobre el subtotal en COP.
  * **Autocompletado de Checkout:** En `/carrito` (`controllers/shop_controller.py` y `templates/cart.html`), los campos de nombre, correo, teléfono y dirección se rellenan automáticamente con los datos del perfil del usuario autenticado.
  * **Historial *Mis Pedidos* (`/mis-pedidos`):** Nueva vista (`templates/my_orders.html`) donde cada cliente consulta sus pedidos realizados, el estado actual (`Pendiente`, `Confirmado`, `Cancelado`) y el desglose de productos adquiridos.
  * **Apartado informativo de Membresía:** Sección comparativa en la Landing Page (`templates/index.html`) y en Registro (`templates/auth/register.html`) explicando los beneficios de registrarse como Cliente Normal y cómo obtener el nivel VIP.
* **¿Con qué finalidad?**
  * Darle un valor comercial real y tangible al rol `vip`, reducir la fricción durante el proceso de compra al evitar que el usuario registrado tenga que digitar sus datos repetidamente, y ofrecer trazabilidad transparente después de cada compra.

### 6.3. Aislamiento del Carrito por Usuario e Invitado y Mejoras de UI/UX
* **¿Qué se hizo?**
  * **Aislamiento de Carrito (`session["user_carts"]`):** Se particionó el almacenamiento del carrito en sesión usando la clave única del usuario autenticado (`user:<id>`) o `guest` para visitantes anónimos (`controllers/auth_controller.py`, `services/cart_service.py`). Al iniciar o cerrar sesión, cada cuenta conserva únicamente sus propios productos.
  * **Legibilidad y Accesibilidad en Formularios y Catálogo:**
    * Se eliminó la negrita excesiva en los títulos de productos y etiquetas de formularios (`static/css/styles.css`) para hacer la lectura más amena.
    * Se añadieron asteriscos rojos (`*`) en todos los campos obligatorios de Login, Registro y Checkout.
    * Se incorporó el botón interactivo del **ojito (mostrar/ocultar contraseña)** en los formularios de inicio de sesión y registro (`static/js/app.js`).
    * Se corrigió el contraste del botón e icono de **Registro** en la barra de navegación superior para que sea claro y legible sobre fondos oscuros.
* **¿Con qué finalidad?**
  * Corregir el defecto donde un producto agregado desde una cuenta (ej. VIP) aparecía o se borraba en otra cuenta (ej. Cliente Normal) en el mismo navegador, y mejorar la usabilidad, estética y accesibilidad de los formularios.

### 6.4. Gestión Administrativa de Pedidos, Roles, Precios por Categoría y Cupones
* **¿Qué se hizo?**
  * **Módulo de Pedidos (`/admin/pedidos`):** Vista administrativa (`templates/admin/orders.html`) que permite filtrar órdenes y cambiar su estado (`pending`, `confirmed`, `cancelled`). Al confirmar un pedido se descuenta atómicamente el stock de cada producto en SQLite; si se cancela un pedido previamente confirmado, el stock se revierte automáticamente.
  * **Gestión de Roles en Clientes (`/admin/clientes`):** Selector directo para promover o cambiar el rol de cualquier usuario entre `cliente`, `vip` y `admin` (`POST /admin/clientes/<id>/rol`).
  * **Ajuste Porcentual de Precios por Categoría y Cupones (`/admin/categorias`):**
    * Herramienta para aplicar descuentos o incrementos porcentuales masivos (ej. `-10%`, `-15%`, `+5%`) a todos los productos de una categoría principal.
    * CRUD completo de **Cupones de Descuento** (`cupones`) globales o restringidos a una categoría específica, redimibles por los clientes en `/carrito`.
* **¿Con qué finalidad?**
  * Cerrar el ciclo operativo entre las compras de los clientes y el inventario real de la tienda, y brindar al administrador herramientas comerciales ágiles para gestionar campañas de descuento, cupones promocionales y membresías VIP sin editar producto por producto.

### 6.5. Tablero de Analítica Integral Interactiva (`/admin/analytics/`)
* **¿Qué se hizo?**
  * Se rediseñó la aplicación Plotly Dash (`controllers/admin_dash.py`) incorporando una barra superior de navegación con botones claros de salida (**`← Volver al Panel Admin`**, accesos a Productos, Categorías, Pedidos, Clientes y **`Salir a la Tienda`**).
  * Se amplió el análisis más allá de productos destacados, añadiendo filtro interactivo por categoría y **6 visualizaciones**:
    1. Unidades en stock vs. número de referencias por categoría.
    2. Valorización del inventario en millones de COP por categoría.
    3. Productos destacados con mayor disponibilidad.
    4. Alertas de productos en bajo stock (`≤ 5` unidades) para reabastecimiento.
    5. Segmentación de usuarios por rol (`Cliente`, `VIP`, `Admin`).
    6. Distribución de pedidos por estado e ingresos confirmados, más tabla comparativa por categoría.
* **¿Con qué finalidad?**
  * Evitar que el administrador quede atrapado en la vista de analítica sin botón claro de retorno y proporcionar inteligencia de negocio completa sobre todas las dimensiones del e-commerce (categorías, inventario, clientes y ventas).

### 6.6. Seguridad CSRF, Contrato OpenAPI y Modularización de Hojas de Estilo CSS
* **¿Qué se hizo?**
  * **Protección CSRF:** Validación centralizada de tokens `_csrf_token` en `app.py` para todas las peticiones `POST` de formularios en autenticación, tienda y administración.
  * **Actualización de OpenAPI (`/api/docs`):** Documentación de los nuevos roles (`vip`), descuentos y rutas en `services/openapi_spec.py`.
  * **Modularización CSS:** Se dividió el archivo monolítico `static/css/styles.css` (que superaba las 3,750 líneas) extrayendo los estilos exclusivos del panel administrativo a `static/css/admin.css` y los del visor 3D a `static/css/product-3d.css`, reduciendo más de 1,000 líneas del CSS principal.
* **¿Con qué finalidad?**
  * Proteger las operaciones de cambio de estado contra ataques *Cross-Site Request Forgery* (CSRF), mantener la documentación Swagger sincronizada con el código real y mejorar el rendimiento de carga y la mantenibilidad de los estilos.

---

## 7. Verificación y Ejecución de Pruebas

Para inicializar o verificar la base de datos SQLite y ejecutar la aplicación localmente:
```bash
python scripts/init_db.py
python app.py
```
La aplicación queda disponible en `http://127.0.0.1:5000`.

Para ejecutar las pruebas automatizadas (52 pruebas de backend y suite frontend):
```bash
python -m pytest -q
python -m unittest discover tests
npm test
```

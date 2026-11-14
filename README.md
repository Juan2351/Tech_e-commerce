# LePetit

LePetit es una tienda web de demostración para consultar un catálogo de productos, filtrar por categoría, revisar detalles y mantener un carrito temporal. Está organizada por MVC y capas para separar las vistas, los controladores, las reglas del carrito y el acceso a los datos en Firebase o SQLite.

## Descripción del sistema

- **Problema:** presentar un catálogo de comercio electrónico tecnológico consultable, interacción de compra y un panel de gestión administrativa sin mezclar la interfaz con las capas de datos ni exponer secretos de infraestructura.
- **Objetivo:** exhibir productos, precios en pesos colombianos (COP), marcas, categorías, stock, permitir modificar un carrito de compras, autenticar usuarios y administrar inventario mediante un panel protegido.
- **Usuarios y Roles:**
  - **Visitante / Cliente (`cliente`):** navega por la Landing Page, explora la Tienda Oficial, filtra productos, gestiona su carrito de compras aislado, redime cupones promocionales, autocompleta el checkout y consulta su historial en *Mis Pedidos* (`/mis-pedidos`).
  - **Cliente VIP (`vip`):** además de los beneficios de cliente registrado, recibe automáticamente un **10% de descuento preferencial** sobre el subtotal de su carrito y prioridad en asignación de inventario.
  - **Administrador (`admin`):** accede al panel administrativo independiente (`/admin`) para gestionar productos (CRUD), categorías, ajustes porcentuales de precios por categoría, cupones de descuento, estados de pedidos (con descuento/reversión atómica de stock), roles de clientes y analítica interactiva (`/admin/analytics/`).
- **Funcionalidades implementadas:**
  - Landing Page (`/`) con Hero corporativo, modelo esquemático 3D de bajo consumo, carrusel de categorías con SVG, carrusel de productos destacados y formulario de contacto.
  - Fichas de producto con visor 3D opcional, centrado responsive y piezas seleccionables que muestran especificaciones disponibles del catálogo sin inventar datos.
  - Tienda Oficial (`/tienda`) con buscador, filtros por categoría, ordenamiento y paginación (24 productos por página).
  - Autenticación (`/login`, `/registro`, `/logout`) con hash de contraseñas PBKDF2-SHA256 y control de acceso basado en roles (RBAC).
  - Panel Administrativo (`/admin`) con sidebar slider colapsible, KPIs, gestión de inventario, categorías y clientes.
  - Carrito de compras con cálculo de subtotales en COP y persistencia en sesión firmada.
  - Checkout que registra pedidos con número único (`LP-fecha-código`), datos de contacto y productos/precios como captura histórica en SQLite; la confirmación ofrece continuar por WhatsApp.
  - API RESTful versionada (`/api/v1/*`) para catálogo y carrito público, login JWT para integraciones y métricas administrativas protegidas por rol.
  - Documentación interactiva Swagger UI (`/api/docs`) y dashboard analítico Plotly Dash solo para administradores (`/admin/analytics/`).
  - Pie de página con la sede en Galicia, Pereira, Risaralda y acceso directo a WhatsApp.
- **Persistencia e Integraciones:** Soporte dual configurable vía `.env`:
  - **Firebase Realtime Database (Nube):** Base de datos cloud en Google Firebase con sincronización y persistencia global.
  - **SQLite (Local):** Base de datos relacional local cargada desde el CSV de 3,718 productos.
  - El catálogo puede consultar Firebase o SQLite según `DATABASE_BACKEND`; las operaciones de autenticación usan Firebase y los pedidos del checkout se guardan en SQLite.
  - URLs de imágenes del CSV, respaldo tecnológico con Unsplash CDN y SVG local de respaldo.

### Pedidos y límites del checkout

El checkout valida los datos de contacto y la disponibilidad indicada por el catálogo, genera un número de pedido y guarda el pedido y sus productos en las tablas `orders` y `order_items` de SQLite. La solicitud queda **pendiente de confirmación** y el carrito se vacía después de guardarse correctamente. Se puede abrir WhatsApp con el número y total del pedido para coordinar con la tienda.

Este flujo no procesa pagos, no confirma una venta ni reserva inventario; la tienda debe verificar existencias, entrega y método de pago por WhatsApp. En despliegues con Firebase, los pedidos continúan almacenándose en el archivo SQLite configurado por `DATABASE_PATH`; el servidor debe contar con almacenamiento persistente y respaldos para conservarlos.

## Tecnologías y decisiones

| Área | Tecnología | Decisión |
|---|---|---|
| Backend | Python 3 y Flask | Backend único ligero, modularizado en controladores, servicios y modelos MVC. |
| Presentación | HTML5 semántico y Jinja2 | Vistas renderizadas del servidor con separación limpia entre Landing, Tienda y Admin. |
| Interacción frontend | JavaScript Vanilla y React | Las páginas siguen renderizadas con Jinja; React se carga solo en el selector de componentes 3D. Vite compila los módulos para servirlos desde Flask. |
| Componentes UI | Bootstrap 5 | Formularios y botones del componente React con estilos aislados para no alterar la interfaz existente. |
| Visualización 3D | Three.js | Modelos esquemáticos por categoría, cargados bajo demanda y sin animación continua para reducir el uso de CPU/GPU. |
| Estilos | CSS3 nativo avanzado | Variables CSS, diseño responsive, animaciones fluidas, modo oscuro y sidebar slider. |
| Persistencia (Cloud) | Firebase Realtime Database | Base NoSQL en la nube de Google para datos globales y gestión remota sin servidores dedicados. |
| Persistencia (Local) | SQLite3 y CSV | Base relacional local parametrizada que se inicializa automáticamente desde el dataset. |
| Autenticación | Werkzeug Security, Flask-JWT-Extended y RBAC | Hashing PBKDF2-SHA256, sesiones web y tokens Bearer con rol firmado y expiración de 15 minutos para la API. |
| Analítica | Plotly Dash | Dashboard de inventario interactivo montado en Flask y restringido a administradores. |
| Documentación API | OpenAPI 3 y Swagger UI | Contrato versionado y navegable en `/api/docs`, incluyendo la autorización JWT. |
| Configuración | `.env` y `python-dotenv` | Centraliza backend activo (`firebase`/`sqlite`), credenciales seguras y tasa USD/COP. |
| Pruebas | Python `unittest` | Pruebas automatizadas de API, roles, autenticación, catálogo, documentación y renderizado de vistas. |
| Documentación | Markdown, Mermaid y OpenAPI | Arquitectura C1-C4, esquema relacional y contratos REST interactivos. |

### Next.js: uso y evaluación

Este proyecto **no utiliza Next.js**. Flask/Jinja ya entrega las páginas HTML y concentra la API; React se limita a componentes interactivos que lo necesitan. Añadir Next.js supondría otro servidor y una migración o duplicación de la capa de presentación sin aportar una necesidad actual.

- **Ventajas si se adopta en el futuro:** renderizado React en servidor, routing integrado, optimización de recursos y buen soporte para páginas públicas que requieran estrategia SEO avanzada.
- **Desventajas para este proyecto:** runtime y despliegue Node adicional, duplicación con Flask/Jinja, integración más compleja de sesión/JWT y migración de plantillas que hoy ya funcionan.

La lista inicial también menciona Java. No se utiliza en esta versión: se seleccionó Python/Flask como único backend para mantener un solo servidor y una arquitectura coherente.

### Instalación y build del frontend

```powershell
npm.cmd install
npm.cmd run build
.\.venv\Scripts\python.exe app.py
```

En PowerShell, `npm.cmd` evita el bloqueo de `npm.ps1` que puede producir la política de ejecución de scripts. El build genera `static/dist/`, que sirve Flask. React, Three.js y el CSS Bootstrap se compilan en archivos separados; los módulos 3D se cargan cuando se necesitan. Configura `JWT_SECRET_KEY` en `.env` con un valor aleatorio independiente de `SECRET_KEY`.

Los valores `precio` del CSV son precios base en USD. Se muestran en COP calculando `precio × USD_TO_COP_RATE`. La tasa por defecto es `4200`, se valida como número finito positivo y puede cambiarse en `.env`; no representa una cotización en tiempo real ni requiere una integración monetaria externa.

## Arquitectura MVC y árbol de carpetas

```text
Tech_e-commerce/
├── app.py                         # Fábrica Flask, registro de rutas y manejadores de error
├── extensions.py                 # Extensión JWT compartida y respuestas de error JSON
├── configs/
│   └── settings.py                # Variables de entorno (Firebase/SQLite, USD/COP, Secret Key)
├── controllers/
│   ├── shop_controller.py         # Rutas públicas (Landing /, Tienda /tienda, Detalle, Carrito)
│   ├── auth_controller.py         # Autenticación (/login, /registro, /logout) y decoradores RBAC
│   ├── admin_controller.py        # Módulo de administración (/admin/*) para inventario, categorías y clientes
│   ├── admin_dash.py              # Dashboard analítico Plotly Dash con callback de métricas
│   └── api_controller.py          # Endpoints API REST JSON y autenticación JWT (/api/v1/*)
├── services/
│   └── cart_service.py            # Reglas de negocio del carrito, validación de stock y subtotales
├── models/
│   ├── firebase_db.py             # Cliente REST nativo para Firebase Realtime Database (Cloud)
│   ├── auth_model.py              # Gestión de usuarios, hashing PBKDF2 y persistencia
│   ├── catalog.py                 # Repositorio unificado de productos y categorías (Firebase/SQLite)
│   ├── database.py                # Conexión local SQLite, consultas parametrizadas y cierre
│   ├── database_setup.py          # Esquema relacional e importación inicial del CSV a SQLite
│   ├── database_errors.py         # Excepciones personalizadas de base de datos
│   └── entities.py                # Modelo Product tipado e inmutable y serialización
├── templates/
│   ├── base.html                  # Layout público maestro con navegación y pie de página
│   ├── index.html                 # Landing Page corporativa (Hero, Beneficios VIP, Carruseles y Contacto)
│   ├── shop.html                  # Tienda Oficial dedicada (Buscador, Filtros, Grilla, Paginación)
│   ├── product_detail.html        # Ficha técnica detallada del producto y visor 3D
│   ├── cart.html                  # Resumen del carrito, cupones, descuento VIP y checkout
│   ├── my_orders.html             # Historial y seguimiento de pedidos del cliente autenticado
│   ├── error.html                 # Manejo visual de errores HTTP
│   ├── auth/                      # Vistas de autenticación
│   │   ├── login.html             # Formulario de inicio de sesión con botón mostrar/ocultar contraseña
│   │   └── register.html          # Formulario de registro de clientes y programa VIP
│   └── admin/                     # Panel Administrativo independiente con Sidebar Slider
│       ├── base_admin.html        # Layout exclusivo del administrador
│       ├── dashboard.html         # Panel de métricas e indicadores KPI
│       ├── products.html          # Listado y gestión de inventario
│       ├── product_form.html      # Creación y edición de productos
│       ├── categories.html        # Gestión de categorías, ajuste de precios por categoría y cupones
│       ├── orders.html            # Gestión de pedidos y actualización de stock
│       └── clients.html           # Directorio y cambio de roles de clientes (cliente, vip, admin)
├── static/
│   ├── css/styles.css             # Estilos de la Tienda Pública y componentes compartidos
│   ├── css/admin.css              # Estilos exclusivos del Portal Administrativo
│   ├── css/product-3d.css         # Estilos exclusivos del Visor e Inspector 3D
│   ├── js/app.js                  # Lógica frontend: carrito, carruseles, ojito de contraseña y visor
│   ├── js/product-3d.js           # Modelos Three.js ligeros por categoría
│   ├── js/product-components.jsx  # Selector de componentes React con Bootstrap aislado
│   ├── dist/                      # Módulos frontend compilados por Vite para Flask
│   └── img/                       # Recursos gráficos locales y fotografías de respaldo
├── database/
│   ├── schema.sql                 # Tablas, relaciones e índices SQLite (productos, usuarios, cupones, pedidos)
│   ├── seed.sql                   # Taxonomía tecnológica de categorías y cupones semilla
│   ├── data/                      # Dataset CSV original con 3,718 productos
│   └── queries.sql                # Consultas de verificación relacional
├── scripts/
│   ├── init_db.py                 # Inicializa database/lepetit.sqlite3 con catálogo, usuarios y cupones
│   ├── migrate_to_firebase.py     # Script de migración y población masiva a Firebase
│   └── create_admin.py            # Creación del usuario administrador inicial
├── docs/
│   ├── actas/                     # Actas de reuniones y plantilla
│   ├── REQUISITOS.md              # Alcance y requisitos observables
│   ├── ARQUITECTURA_Y_MIGRACION.md # Guía técnica de arquitectura y persistencia
│   ├── C4.md                      # Explicación de modelos C1-C4
│   ├── openapi.yaml               # Especificación OpenAPI 3.0 de la API REST
│   └── diagramas/                 # Fuentes Mermaid de arquitectura y ER
├── tests/
│   ├── test_api.py                # API REST, catálogo, importación de datos y COP
│   ├── test_auth_admin.py         # Autenticación y control de acceso RBAC
│   ├── test_orders.py             # Checkout, pedidos y token de formulario
│   ├── test_jwt_dash_docs.py      # JWT, analítica y documentación de API
│   ├── test_catalog_dashboard.py  # Métricas del panel
│   ├── test_3d_viewer.py          # Visores 3D en las páginas
│   └── product-3d.test.js         # Componentes y especificaciones 3D
├── .env.example                   # Plantilla de variables de entorno segura
├── .gitignore                     # Exclusión de entornos, secretos y SQLite generado
├── requirements.txt               # Dependencias Python del proyecto
├── package.json                   # Dependencias y build de React/Three.js/Bootstrap
├── package-lock.json              # Versiones reproducibles del frontend
├── vite.config.js                 # Build local y aislamiento de estilos Bootstrap
└── README.md                      # Documentación integral del sistema
```

### Descripción de carpetas y archivos

| Ruta | Descripción |
|---|---|
| `app.py` | Fábrica principal de Flask; registra blueprints públicos, de autenticación, administrativos y API REST; maneja errores globales. |
| `configs/settings.py` | Carga `.env`; define el backend activo (`DATABASE_BACKEND`), credenciales seguras de Firebase, rutas y tasa USD/COP. |
| `controllers/shop_controller.py` | Controla las vistas públicas: Landing Page (`/`), Tienda Oficial (`/tienda`), Detalle de producto (`/productos/<id>`) y Carrito (`/carrito`). |
| `controllers/auth_controller.py` | Gestiona inicio de sesión, registro de nuevos clientes y cierre de sesión; implementa decoradores `@login_required` y `@admin_required`. |
| `controllers/admin_controller.py` | Controla el panel administrativo protegido: Dashboard de KPIs, CRUD completo de productos, gestión de categorías y clientes. |
| `controllers/api_controller.py` | Expone endpoints RESTful versionados (`/api/v1/*`) para catálogo y operaciones del carrito sin recargar la página. |
| `services/cart_service.py` | Reglas del carrito de compras: verificación de existencia, disponibilidad de stock y cálculo de totales en COP. |
| `models/firebase_db.py` | Capa de persistencia en la nube; realiza operaciones REST (GET, PUT, POST, PATCH, DELETE) sobre Firebase Realtime Database. |
| `models/auth_model.py` | Modelo de autenticación; valida credenciales, aplica hashing seguro de contraseñas (PBKDF2-SHA256) y gestiona usuarios. |
| `models/catalog.py` | Repositorio unificado de catálogo; abstrae el origen de datos (Firebase o SQLite) entregando entidades consistentes a la aplicación. |
| `models/database.py` | Maneja la conexión local SQLite por solicitud, transacciones y consultas parametrizadas. |
| `models/database_setup.py` | Crea las tablas SQLite e importa marcas, categorías y productos desde el CSV cuando se utiliza SQLite. |
| `models/database_errors.py` | Excepciones personalizadas para manejo controlado de fallas en conexiones de datos. |
| `models/entities.py` | Entidad `Product` inmutable con métodos de conversión y serialización para vistas y API. |
| `templates/index.html` | Landing Page moderna con Hero corporativo, carrusel interactivo de categorías con SVG, productos destacados y contacto. |
| `templates/shop.html` | Tienda Oficial dedicada con buscador integrado, filtros por categoría, ordenamiento y paginación. |
| `templates/auth/login.html` | Vista de inicio de sesión con alertas de error y redirección según rol. |
| `templates/auth/register.html` | Vista de registro para nuevos clientes con validación en servidor. |
| `templates/admin/` | Conjunto de vistas del panel administrativo con sidebar slider colapsible (Dashboard, Productos, Formulario, Categorías, Clientes). |
| `scripts/migrate_to_firebase.py` | Script automatizado para migrar y estructurar todo el catálogo CSV y usuarios en Firebase Realtime Database. |
| `scripts/create_admin.py` | Script interactivo/automático para dar de alta el usuario administrador inicial. |
| `docs/REQUISITOS.md` | Propósito, actores, requisitos funcionales y límites observables del sistema. |
| `docs/actas/PLANTILLA.md` | Plantilla vacía para documentar acuerdos y compromisos de reuniones reales. |
| `docs/ARQUITECTURA_Y_MIGRACION.md` | Documentación técnica específica para la sustentación sobre la migración cloud y separación de módulos. |
| `docs/C4.md` | Descripción de los diagramas de contexto, contenedores, componentes y código. |
| `docs/openapi.yaml` | Contrato de la API REST. |
| `tests/` | Pruebas Python y JavaScript para API, autenticación, pedidos, panel y visor 3D. |

### Separación de responsabilidades

- **Presentación:** `templates/`, `static/css/` y `static/js/`. El CSS se mantiene intencionalmente sencillo; el JS envía operaciones de carrito al servidor.
- **Controladores:** `controllers/`. Convierten rutas HTTP en llamadas a repositorios/servicios y devuelven HTML o JSON.
- **Servicios:** `services/`. Contienen reglas de negocio reutilizables, como cantidad positiva y disponibilidad.
- **Modelos y repositorios:** `models/`. `Product` expresa la entidad; `catalog.py` contiene las consultas; `database.py` aísla el conector.
- **Configuración:** `configs/` y `.env`. `app.py` se limita a ensamblar la aplicación y registrar rutas.

Flujo de página en configuración SQLite: `GET /` → `shop_controller.home` → `catalog.fetch_products` → `database.query_all` → SQLite → entidades `Product` → `templates/index.html` → HTML al navegador. Con Firebase configurado, el repositorio consulta el catálogo remoto. El template recibe los productos del repositorio; ni HTML ni JavaScript se conectan directamente a la base.

Flujo del carrito: `static/js/app.js` → `POST /api/v1/carrito/productos` → `api_controller.add_cart_product` → `cart_service.add_product` → `catalog.fetch_product` → repositorio configurado (Firebase o SQLite). Si la validación pasa, Flask guarda el identificador y la cantidad en la sesión firmada y devuelve JSON.

## Persistencia y catálogo tecnológico

El catálogo puede usar Firebase Realtime Database o SQLite local. En el modo SQLite, el CSV incluido en `database/data/amazon_tech_products_ecommerceGKALI.csv` se normaliza en tablas relacionadas; no se requiere un servidor de base de datos aparte ni se agregan productos ficticios. La autenticación utiliza Firebase y el checkout guarda pedidos en SQLite.

Fotografías recibidas: [diagrama E-R](Diagramas/00952644-87a4-4592-88a8-c89ece649397.jpg), [diagrama relacional](Diagramas/7fb1f902-c15e-4352-b5a3-c4fbf986b62c.jpg) y [definición de datos](Diagramas/a350a0e5-0d53-40ba-b681-b3a2be6532be.jpg).

| Tabla | Clave primaria | Campos y relación |
|---|---|---|
| `marca` | `id_marca` | `nombre` único. Una marca puede asociarse a muchos productos. |
| `categoria_principal` | `id_main_cat` | `nombre` único. Una categoría contiene subcategorías. |
| `subcategoria` | `id_subcat` | `id_main_cat` FK y `nombre`; nombre único dentro de su categoría. |
| `producto` | `id_producto` (`TEXT`) | Nombre del producto tecnológico, descripción, precio base en USD, calificación, reseñas, stock, enlaces e imagen, con claves foráneas a marca y subcategoría. |
| `usuarios` | `id` | `nombre_usuario`, `email` único, `password_hash`, `rol` (`admin`, `cliente`, `vip`), `telefono`, `direccion_entrega` y `created_at`. |
| `cupones` | `id` | `codigo` único (ej. `LEPETIT10`), `porcentaje_descuento`, `id_main_cat` opcional (FK a `categoria_principal`), `activo` y `created_at`. |
| `orders` | `id` | `order_number` único, `user_id` opcional (FK a `usuarios`), datos de contacto/entrega, `status` (`pending`, `confirmed`, `cancelled`), `total_cop` y `created_at`. |
| `order_items` | `id` | `order_id` (FK a `orders`), `id_producto` (FK a `producto`), `product_name`, `unit_price_cop`, `quantity` y `subtotal_cop`. |

Relaciones: marca 1:N producto; categoría principal 1:N subcategoría; subcategoría 1:N producto. Las claves foráneas y restricciones de SQLite protegen la integridad; los índices sirven las búsquedas y relaciones principales. `seed.sql` contiene solo la taxonomía tecnológica existente en los datos, mientras que los productos se importan desde el CSV como única fuente verificable.

El catálogo cubre smartphones Android e iPhone, laptops (incluidos equipos gaming), PC de escritorio y mini PC, mouse y teclados, monitores, audio, tablets, relojes, almacenamiento y docks. El CSV disponible no contiene productos clasificados como consolas ni videojuegos; no se inventan artículos ni se muestran categorías vacías. Para completar esas líneas se requiere un CSV real con esos productos.

La primera operación que necesita SQLite crea `database/lepetit.sqlite3`, ejecuta el esquema y las categorías y carga los productos en una transacción, si todavía no existen. La base poblada no se importa de nuevo en cada solicitud. Para reconstruirla desde un CSV actualizado, detén Flask y respalda la base antes de reemplazarla.

### Conexión entre Flask y SQLite

Cuando está seleccionado SQLite, la aplicación utiliza el módulo `sqlite3` incluido en Python; no requiere un servidor SQL separado, una cuenta de base de datos ni credenciales de MySQL. `models/database.py` abre una conexión a `DATABASE_PATH` cuando una solicitud Flask necesita datos, activa las claves foráneas y configura filas accesibles por nombre. La conexión queda asociada al contexto de esa solicitud y se cierra al terminarla. Las consultas usan parámetros `?` en lugar de concatenar valores del usuario.

Cuando una operación utiliza SQLite, `models/database_setup.py` crea las tablas definidas en `database/schema.sql`, aplica las categorías de `database/seed.sql` e importa el CSV si la tabla `producto` aún no tiene registros. La importación valida las columnas y valores, crea marcas y subcategorías faltantes y confirma los datos dentro de una transacción. Si faltan datos o hay conflictos, la carga se revierte y Flask reporta que la base no está disponible; no presenta un catálogo vacío como si hubiera sido importado correctamente.

La ruta `GET /api/v1/salud` comprueba el backend configurado: consulta Firebase cuando `DATABASE_BACKEND=firebase` o ejecuta `SELECT 1` con SQLite cuando se configura SQLite. La insignia del encabezado consulta esa ruta; el navegador nunca abre una conexión directa a la base de datos.

| Variable | Valor predeterminado | Uso |
|---|---|---|
| `DATABASE_PATH` | `database/lepetit.sqlite3` | Ruta de la base SQLite local. |
| `DATASET_CSV_PATH` | `database/data/amazon_tech_products_ecommerceGKALI.csv` | Ruta del catálogo tecnológico de origen. |
| `USD_TO_COP_RATE` | `4200` | Conversión de precios base USD a COP; no es una cotización en tiempo real. |

Las rutas relativas se resuelven desde la carpeta del proyecto. Se pueden cambiar en el archivo `.env`, creado a partir de `.env.example`; la base SQLite generada y las credenciales locales no se suben a Git.

### Tecnología y respaldo de imágenes

Cada producto conserva el campo `image_url` que viene en el CSV y la página intenta mostrar esa URL. Como algunas imágenes remotas de Amazon no responden en el navegador, `static/js/app.js` escucha los errores de carga y selecciona una fotografía representativa de Unsplash según la subcategoría. Si tampoco se puede cargar la imagen remota, se usa `static/img/product-placeholder.svg`.

Las fotografías de Unsplash se sirven desde su CDN mediante URLs directas por identificador; el proyecto no llama a una API de imágenes ni necesita una clave. Son recursos ilustrativos por categoría y no una garantía de que la fotografía corresponda al SKU exacto. Las imágenes remotas requieren conexión a Internet; el SVG local permite mantener un respaldo cuando la red o los CDNs no están disponibles.

## Guía de Instalación y Ejecución por Sistema Operativo (Windows, Linux y macOS)

> **Importante:** **No uses Live Server** de VS Code para abrir `index.html`. Las vistas usan plantillas Jinja2 renderizadas por Flask y consultan SQLite desde el backend Python.

### 1. Requisitos previos (para todos los sistemas operativos)
Antes de empezar, asegúrate de tener instalado:
1. **Python 3.10 o superior** (con `pip` y `venv` incluidos).
   - Verificar con: `python --version` o `python3 --version`
2. **Node.js 18+ y npm** (opcional si solo ejecutas el servidor, porque `static/dist/` ya está compilado, pero requerido si deseas recompilar los componentes 3D o correr pruebas JS).
   - Verificar con: `node --version` y `npm --version`
3. **Git** para clonar el repositorio.

---

### 2. Instalación paso a paso según tu Sistema Operativo

#### Opción A: Windows (PowerShell)

Abre **PowerShell** en la carpeta donde quieras descargar el proyecto y ejecuta:

```powershell
# 1. Clonar el repositorio y entrar a la carpeta
git clone https://github.com/Juan2351/Tech_e-commerce.git
Set-Location .\Tech_e-commerce

# 2. Crear y activar el entorno virtual de Python
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
# (Si PowerShell bloquea Activate.ps1, puedes usar directamente .\.venv\Scripts\python.exe en los pasos siguientes)

# 3. Instalar las dependencias de Python (requirements.txt)
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Crear el archivo de configuración .env a partir de la plantilla
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

# 5. Inicializar la base de datos SQLite (3,718 productos + usuarios + cupones)
.\.venv\Scripts\python.exe scripts\init_db.py

# 6. (Opcional) Instalar dependencias frontend y compilar el visor 3D
npm.cmd install
npm.cmd run build

# 7. Iniciar el servidor Flask
.\.venv\Scripts\python.exe app.py
```

#### Opción B: Windows (Símbolo del sistema / CMD)

```cmd
git clone https://github.com/Juan2351/Tech_e-commerce.git
cd Tech_e-commerce

python -m venv .venv
.venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt

if not exist .env copy .env.example .env
python scripts\init_db.py

npm install
npm run build

python app.py
```

#### Opción C: Linux (Ubuntu / Debian / Fedora / Arch)

Abre tu terminal y ejecuta:

```bash
# 0. (Solo si no tienes python3-venv instalado en Ubuntu/Debian)
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nodejs npm

# 1. Clonar el repositorio y entrar a la carpeta
git clone https://github.com/Juan2351/Tech_e-commerce.git
cd Tech_e-commerce

# 2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar las dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

# 4. Crear el archivo .env (viene preconfigurado con DATABASE_BACKEND=sqlite)
cp -n .env.example .env

# 5. Inicializar la base de datos SQLite local
python scripts/init_db.py

# 6. (Opcional) Compilar recursos frontend
npm install
npm run build

# 7. Iniciar el servidor Flask
python app.py
```

#### Opción D: macOS (Terminal zsh / bash)

Abre **Terminal** y ejecuta:

```bash
# 1. Clonar el repositorio y entrar a la carpeta
git clone https://github.com/Juan2351/Tech_e-commerce.git
cd Tech_e-commerce

# 2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar las dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

# 4. Crear el archivo .env
cp -n .env.example .env

# 5. Inicializar la base de datos SQLite local
python scripts/init_db.py

# 6. (Opcional) Compilar recursos frontend
npm install
npm run build

# 7. Iniciar el servidor Flask
python app.py
```

---

### 3. Acceso a la aplicación, cuentas de prueba y cupones

Una vez ejecutado `python app.py`, abre tu navegador en **`http://127.0.0.1:5000`**:

| Vista | URL local |
|---|---|
| Landing Page | `http://127.0.0.1:5000/` |
| Tienda Oficial | `http://127.0.0.1:5000/tienda` |
| Carrito y Checkout | `http://127.0.0.1:5000/carrito` |
| Iniciar Sesión / Registro | `http://127.0.0.1:5000/login` / `http://127.0.0.1:5000/registro` |
| Panel Administrativo | `http://127.0.0.1:5000/admin/dashboard` |
| Analítica Interactiva (Dash) | `http://127.0.0.1:5000/admin/analytics/` |
| Documentación Swagger API | `http://127.0.0.1:5000/api/docs` |

#### Cuentas listas para probar (creadas por `scripts/init_db.py`)

| Rol | Correo electrónico | Contraseña | Qué puedes probar con esta cuenta |
|---|---|---|---|
| **Administrador (`admin`)** | `admin@lepetit.com` | `admin123` | Acceso total a `/admin`: CRUD de productos, gestión de pedidos y stock, cambio de roles (`cliente`/`vip`/`admin`), ajuste de precios por categoría, cupones y analítica en `/admin/analytics/`. |
| **Cliente VIP (`vip`)** | `vip@lepetit.com` | `vip123` | **10% de descuento automático** en el carrito, carrito aislado propio, autocompletado en checkout y vista `/mis-pedidos`. |
| **Cliente Normal (`cliente`)** | `cliente@lepetit.com` | `cliente123` | Compras estándar, carrito aislado propio, uso de cupones promocionales, autocompletado en checkout y vista `/mis-pedidos`. |

#### Cupones promocionales de prueba (para redimir en `/carrito`)
* **`LEPETIT10`**: 10% de descuento en toda la tienda.
* **`LAPTOPS15`**: 15% de descuento en productos de la categoría *Laptops y Computadores*.
* **`SMART15`**: 15% de descuento en productos de la categoría *Smartphones y Celulares*.

### HTTPS local

El desarrollo local funciona en HTTP. Para probar HTTPS, genera un certificado de desarrollo fuera del repositorio y define `SSL_CERT_FILE` y `SSL_KEY_FILE` en `.env`; deben configurarse ambos. Flask inicia HTTPS local con ese certificado. No compartas ni subas certificados privados. En producción, termina HTTPS en un proxy inverso y activa `SESSION_COOKIE_SECURE=true`.

## Funcionalidades web

- **Landing Page (`/`):**
  - Presentación corporativa con Hero moderno y llamado a la acción.
  - Carrusel interactivo de categorías tecnológicas con navegación suave e iconografía SVG profesional (cero emojis).
  - Carrusel de productos más comprados y destacados basados en ratings reales.
  - Sección de garantías oficiales y formulario funcional de contacto directo.
- **Tienda Oficial (`/tienda` o `/catalogo`):**
  - Catálogo de 3,718 productos tecnológicos con paginación optimizada (24 artículos por página).
  - Búsqueda en tiempo real por nombre, marca o especificaciones.
  - Filtros dinámicos por categorías principales y subcategorías.
  - Ordenamiento por destacados, precio (ascendente/descendente) y mejor valoración.
  - Ficha de detalle (`/productos/<id>`) con información del producto y selector de cantidad.
- **Carrito de compras (`/carrito`):**
  - Agregar, modificar unidades y eliminar productos asíncronamente vía API REST.
  - Validación estricta de existencias y stock en servidor.
  - Conversión y presentación monetaria en Pesos Colombianos (COP) con separadores locales.
- **Módulo de Autenticación y Control de Acceso (RBAC):**
  - Registro de clientes con contraseñas protegidas mediante hash PBKDF2-SHA256 (`/registro`).
  - Inicio de sesión con redirección automática según rol (`/login`).
  - Decoradores de seguridad `@login_required` y `@admin_required` para proteger endpoints.
- **Panel Administrativo (`/admin`):**
  - Layout aislado con Sidebar Slider colapsible (menú retráctil en escritorio y drawer modal en móviles).
  - **Dashboard:** Métricas clave (KPIs) en tiempo real: total productos, categorías, clientes registrados, stock global y valuación.
  - **Inventario:** Tabla interactiva con búsqueda, badges de stock y acciones directas.
  - **CRUD de Productos:** Formulario para crear y editar productos completos.
  - **Gestión de Categorías:** CRUD y monitoreo de productos asociados por categoría.
  - **Gestión de Clientes:** Directorio de usuarios y roles registrados.

### Crear cuentas para pruebas

No uses credenciales compartidas o predeterminadas. Registra un cliente desde `/registro`. Para crear un administrador, configura Firebase y ejecuta `.\.venv\Scripts\python.exe scripts\create_admin.py`; ingresa una contraseña fuerte y única cuando el script la solicite. El script de migración también contiene usuarios de demostración: revísalos y cambia o elimina esas cuentas antes de usar datos reales.

## API REST

Prefijo y versión: `/api/v1`. Las respuestas exitosas con contenido usan `{ "data": ... }`; los errores usan `{ "error": { "code": "...", "message": "..." } }`. La eliminación exitosa del carrito responde `204` sin contenido.

| Método | Ruta | Parámetros / JSON | Respuestas principales |
|---|---|---|---|
| POST | `/api/v1/auth/login` | `{"email":"...","password":"..."}` | 200, 400, 401; devuelve JWT Bearer de 15 minutos |
| GET | `/api/v1/admin/dashboard` | JWT Bearer de administrador | 200, 401, 403, 503 |
| GET | `/api/v1/salud` | — | 200, 503 |
| GET | `/api/v1/productos` | Opcionales: `category_id`, `subcategory_id`, `q`, `sort` (`featured`, `price_asc`, `price_desc`, `rating_desc`) | 200, 400 |
| GET | `/api/v1/productos/{id}` | ID de producto | 200, 404 |
| GET | `/api/v1/categorias` | — | 200 |
| GET | `/api/v1/carrito` | — | 200 |
| POST | `/api/v1/carrito/productos` | `{"product_id":"LAP-B0BS4BP8FB","quantity":1}` | 201, 400, 404, 409 |
| PATCH | `/api/v1/carrito/productos/{id}` | `{"quantity":2}` | 200, 400, 404, 409 |
| DELETE | `/api/v1/carrito/productos/{id}` | ID de producto | 204, 404 |

`400` indica formato o valor inválido; `404`, recurso ausente; `409`, stock insuficiente; `503`, base de datos sin conexión/configuración. Los filtros y cantidades se validan en el servidor, los valores SQL se parametrizan y `sort` se escoge de una lista permitida.

El contrato legible por herramientas está en [docs/openapi.yaml](docs/openapi.yaml). El navegador y la API tienen el mismo origen; no se habilita CORS abierto. Si se separa el frontend en otro dominio, debe permitirse explícitamente solo ese origen y revisar credenciales/cookies antes de desplegar.

### Probar con curl

```powershell
curl.exe "http://127.0.0.1:5000/api/v1/productos?category_id=1&sort=price_asc"
curl.exe "http://127.0.0.1:5000/api/v1/productos/LAP-B0BS4BP8FB"
curl.exe -X POST "http://127.0.0.1:5000/api/v1/carrito/productos" `
  -H "Content-Type: application/json" `
  -d "{\"product_id\":\"LAP-B0BS4BP8FB\",\"quantity\":1}"
```

Para conservar la cookie de sesión entre llamadas API con curl, agrega `-c cookies.txt` al POST y `-b cookies.txt` a las consultas siguientes.

## Diagramas y exposición C4

La explicación y el flujo están en [docs/C4.md](docs/C4.md). Los fuentes editables Mermaid están en `docs/diagramas/`:

- [C1 Contexto](docs/diagramas/C1-contexto.mmd): actor, sistema y servicio externo de imágenes.
- [C2 Contenedores](docs/diagramas/C2-contenedores.mmd): navegador, aplicación Flask y SQLite local.
- [C3 Componentes](docs/diagramas/C3-componentes.mmd): componentes internos del backend.
- [C4 Código del carrito](docs/diagramas/C4-funcionalidad-carrito.mmd): módulos, métodos, base de datos y sesión.
- [Modelo ER](docs/diagramas/modelo-entidad-relacion.mmd): tablas, claves y cardinalidades.

Para explicar la exposición: C1, quién usa LePetit; C2, navegador, servidor y base de datos; C3, responsabilidades internas de Flask; C4, la petición de agregar un producto y sus validaciones.

## Actividades cubiertas

### Modelado y carga de catálogo

1. Se definieron producto, marca, categoría y subcategoría.
2. Se validó el CSV de tecnología: 3718 productos, identificadores sin duplicados y datos de precio, calificación y stock presentes.
3. Se documentaron entidades, atributos y cardinalidades en el ER.
4. Se declararon claves primarias, únicas y foráneas.
5. Se conservaron los diagramas entregados y se añadió el ER Mermaid coherente con el SQL.
6. `schema.sql` crea el esquema SQLite con tablas, restricciones e índices.
7. `seed.sql` define únicamente categorías y subcategorías tecnológicas.
8. `database_setup.py` importa los productos del CSV y los normaliza en las tablas relacionadas.
9. `queries.sql` revisa joins y posibles referencias inválidas.
10. La consulta de catálogo implementa búsqueda, filtro y ordenamiento; el stock se valida para el carrito.
11. `models/database.py` abre y cierra la base local por solicitud.

### Arquitectura web y contrato HTTP

- El blueprint de carpetas está implementado según el árbol anterior; no hay un `app.py` monolítico.
- El contrato API está versionado, usa sustantivos plurales, filtros y estados HTTP explícitos.
- Los endpoints API sirven tanto a la interfaz JavaScript como a clientes de prueba.
- No se activa CORS porque la aplicación consume la API en su mismo origen.
- HTTPS local se puede habilitar con certificado propio; HTTP queda para el desarrollo simple.
- Autenticación y Autorización implementadas: arquitectura RBAC con roles de Visitante, Cliente y Administrador. Contraseñas protegidas con salt y hash PBKDF2-SHA256 (`werkzeug.security`) y decoradores de ruta (`@login_required`, `@admin_required`).
- Gestión completa de inventario desde el panel administrativo (`/admin`).

### Git y GitHub

El repositorio del equipo es [Juan2351/Tech_e-commerce](https://github.com/Juan2351/Tech_e-commerce). El código de la tienda está organizado por responsabilidades: `templates/` contiene las vistas HTML, `static/` reúne CSS, JavaScript e imágenes locales, y `controllers/`, `services/` y `models/` separan rutas, reglas del carrito y acceso a datos. La tabla anterior describe el propósito de cada carpeta y archivo principal. El desarrollo y la publicación se hacen en la rama `main`; esta guía describe el estado del código sin atribuir cambios a commits o publicaciones que no se hayan verificado.

Para obtener el repositorio:

```powershell
git clone https://github.com/Juan2351/Tech_e-commerce.git
Set-Location .\Tech_e-commerce
```

Después sigue la sección [Instalación y ejecución en Windows](#instalación-y-ejecución-en-windows). Antes de iniciar la aplicación, configura `.env` con los datos del proyecto Firebase que tengas autorizado. Las variables principales son:

```env
DATABASE_BACKEND=firebase
FIREBASE_DATABASE_URL=https://<tu-proyecto>.firebasedatabase.app
FIREBASE_API_KEY=<tu-api-key>
FIREBASE_PROJECT_ID=<tu-project-id>
```

No uses valores de otro equipo o proyecto ni publiques credenciales. Para cargar datos, revisa el script antes de ejecutarlo:

```powershell
.\.venv\Scripts\python.exe scripts\migrate_to_firebase.py
```

Para usar SQLite en el catálogo, define `DATABASE_BACKEND=sqlite` y `DATABASE_PATH=database/lepetit.sqlite3` en `.env`. La autenticación y las cuentas siguen dependiendo de Firebase.

La aplicación se inicia con:

```powershell
.\.venv\Scripts\python.exe app.py
```

Abre `http://127.0.0.1:5000` en tu navegador.
- Landing Page: `http://127.0.0.1:5000/`
- Tienda Oficial: `http://127.0.0.1:5000/tienda`
- Iniciar Sesión: `http://127.0.0.1:5000/login`
- Panel Administrativo: `http://127.0.0.1:5000/admin` (requiere una cuenta con rol de administrador)

## Documentación del proyecto

- [Requisitos y alcance](docs/REQUISITOS.md): actores, capacidades y límites que describe la implementación actual.
- [Estado de trabajo reportado](docs/REQUISITOS.md#estado-de-trabajo-reportado): resumen de tareas en curso y pendientes según el tablero compartido por el equipo.
- [Plantilla de acta de reunión](docs/actas/PLANTILLA.md): formato vacío para documentar reuniones reales; completar asistentes, decisiones y compromisos con datos confirmados por el equipo.
- [Arquitectura y migración](docs/ARQUITECTURA_Y_MIGRACION.md): separación de módulos y persistencia.
- [Modelo C4](docs/C4.md) y [diagramas Mermaid](docs/diagramas/): contexto, contenedores, componentes, carrito y modelo entidad-relación.
- [Contrato OpenAPI](docs/openapi.yaml): especificación de la API.

Las actas completadas deben guardarse en `docs/actas/` con nombres descriptivos, por ejemplo `acta-AAAA-MM-DD.md`. Este repositorio no incluye actas completadas porque no se proporcionaron fechas, asistentes ni acuerdos verificables.

## Validación y pruebas automatizadas

Ejecuta las pruebas Python y JavaScript desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests -v
npm.cmd test
```

La suite Python cubre catálogo, API, carrito, pedidos, autenticación, permisos administrativos, JWT, panel analítico, documentación y renderizado de vistas. La suite JavaScript cubre el mapeo de componentes y especificaciones del visor 3D. El conteo de pruebas puede cambiar cuando se agreguen o retiren casos.

Para validar también la compilación del frontend:

```powershell
npm.cmd run build
```

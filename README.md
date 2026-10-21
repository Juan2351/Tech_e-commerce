# LePetit

LePetit es una tienda web de demostración para consultar un catálogo de productos, filtrar por categoría, revisar detalles y mantener un carrito temporal. Está organizada por MVC y capas para que las vistas, los controladores, las reglas del carrito y el acceso a SQLite no queden mezclados en un único archivo.

## Descripción del sistema

- **Problema:** presentar un catálogo de comercio electrónico tecnológico consultable, interacción de compra y un panel de gestión administrativa sin mezclar la interfaz con las capas de datos ni exponer secretos de infraestructura.
- **Objetivo:** exhibir productos, precios en pesos colombianos (COP), marcas, categorías, stock, permitir modificar un carrito de compras, autenticar usuarios y administrar inventario mediante un panel protegido.
- **Usuarios y Roles:**
  - **Visitante / Cliente:** navega por la Landing Page, explora la Tienda Oficial, filtra productos, gestiona el carrito de compras y puede registrarse o iniciar sesión.
  - **Administrador:** accede al panel administrativo independiente (`/admin`) para gestionar productos (CRUD), categorías y clientes, además de visualizar métricas en tiempo real.
- **Funcionalidades implementadas:**
  - Landing Page (`/`) con Hero corporativo, carrusel de categorías con SVG, carrusel de productos destacados y formulario de contacto.
  - Tienda Oficial (`/tienda`) con buscador, filtros por categoría, ordenamiento y paginación (24 productos por página).
  - Autenticación (`/login`, `/registro`, `/logout`) con encriptación PBKDF2-SHA256 y control de acceso basado en roles (RBAC).
  - Panel Administrativo (`/admin`) con sidebar slider colapsible, KPIs, gestión de inventario, categorías y clientes.
  - Carrito de compras con cálculo de subtotales en COP y persistencia en sesión firmada.
  - API RESTful versionada (`/api/v1/*`) para operaciones asíncronas de catálogo y carrito.
- **Persistencia e Integraciones:** Soporte dual configurable vía `.env`:
  - **Firebase Realtime Database (Nube):** Base de datos cloud en Google Firebase con sincronización y persistencia global.
  - **SQLite (Local):** Base de datos relacional local cargada desde el CSV de 3,718 productos.
  - URLs de imágenes del CSV, respaldo tecnológico con Unsplash CDN y SVG local de respaldo.

## Tecnologías y decisiones

| Área | Tecnología | Decisión |
|---|---|---|
| Backend | Python 3 y Flask | Backend único ligero, modularizado en controladores, servicios y modelos MVC. |
| Presentación | HTML5 semántico y Jinja2 | Vistas renderizadas del servidor con separación limpia entre Landing, Tienda y Admin. |
| Interacción frontend | JavaScript Vanilla | Manejo de carrito asíncrono, carruseles fluidos y slider del sidebar sin sobrecarga de frameworks. |
| Estilos | CSS3 nativo avanzado | Variables CSS, diseño responsive, animaciones fluidas, modo oscuro y sidebar slider. |
| Persistencia (Cloud) | Firebase Realtime Database | Base NoSQL en la nube de Google para datos globales y gestión remota sin servidores dedicados. |
| Persistencia (Local) | SQLite3 y CSV | Base relacional local parametrizada que se inicializa automáticamente desde el dataset. |
| Autenticación | Werkzeug Security & RBAC | Hashing seguro de contraseñas con PBKDF2-SHA256 y decoradores de protección de rutas (`@login_required`, `@admin_required`). |
| Configuración | `.env` y `python-dotenv` | Centraliza backend activo (`firebase`/`sqlite`), credenciales seguras y tasa USD/COP. |
| Pruebas | Python `unittest` | Suite de 24 pruebas automatizadas con 100% de éxito cubriendo API, roles, auth y catálogo. |
| Documentación | Markdown, Mermaid y OpenAPI | Arquitectura C1-C4, esquema relacional y contratos REST interactivos. |

La lista inicial también menciona Java. No se utiliza en esta versión: se seleccionó Python/Flask como único backend para mantener un solo servidor y una arquitectura coherente. El proyecto tampoco necesita React porque Flask entrega HTML y el JavaScript consume la API en el mismo origen.

Los valores `precio` del CSV son precios base en USD. Se muestran en COP calculando `precio × USD_TO_COP_RATE`. La tasa por defecto es `4200`, se valida como número finito positivo y puede cambiarse en `.env`; no representa una cotización en tiempo real ni requiere una integración monetaria externa.

## Arquitectura MVC y árbol de carpetas

```text
Tech_e-commerce/
├── app.py                         # Fábrica Flask, registro de rutas y manejadores de error
├── configs/
│   └── settings.py                # Variables de entorno (Firebase/SQLite, USD/COP, Secret Key)
├── controllers/
│   ├── shop_controller.py         # Rutas públicas (Landing /, Tienda /tienda, Detalle, Carrito)
│   ├── auth_controller.py         # Autenticación (/login, /registro, /logout) y decoradores RBAC
│   ├── admin_controller.py        # Módulo de administración (/admin/*) para inventario, categorías y clientes
│   └── api_controller.py          # Endpoints API REST JSON versionados (/api/v1/*)
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
│   ├── index.html                 # Landing Page corporativa (Hero, Carruseles y Contacto)
│   ├── shop.html                  # Tienda Oficial dedicada (Buscador, Filtros, Grilla, Paginación)
│   ├── product_detail.html        # Ficha técnica detallada del producto
│   ├── cart.html                  # Resumen del carrito y totales
│   ├── error.html                 # Manejo visual de errores HTTP
│   ├── auth/                      # Vistas de autenticación
│   │   ├── login.html             # Formulario de inicio de sesión
│   │   └── register.html          # Formulario de registro de clientes
│   └── admin/                     # Panel Administrativo independiente con Sidebar Slider
│       ├── base_admin.html        # Layout exclusivo del administrador
│       ├── dashboard.html         # Panel de métricas e indicadores KPI
│       ├── products.html          # Listado y gestión de inventario
│       ├── product_form.html      # Creación y edición de productos
│       ├── categories.html        # Gestión y CRUD de categorías
│       └── clients.html           # Directorio y roles de clientes
├── static/
│   ├── css/styles.css             # Estilos completos: diseño responsivo, dark mode, slider
│   ├── js/app.js                  # Lógica frontend: carrito asíncrono, carruseles, sidebar drawer
│   └── img/                       # Recursos gráficos locales y fotografías de respaldo
├── database/
│   ├── schema.sql                 # Tablas, relaciones e índices SQLite
│   ├── seed.sql                   # Taxonomía tecnológica de categorías
│   ├── data/                      # Dataset CSV original con 3,718 productos
│   └── queries.sql                # Consultas de verificación relacional
├── scripts/
│   ├── migrate_to_firebase.py     # Script de migración y población masiva a Firebase
│   └── create_admin.py            # Creación del usuario administrador inicial
├── docs/
│   ├── ARQUITECTURA_Y_MIGRACION.md # Guía detallada para sustentación docente
│   ├── C4.md                      # Explicación de modelos C1-C4
│   ├── openapi.yaml               # Especificación OpenAPI 3.0 de la API REST
│   └── diagramas/                 # Fuentes Mermaid de arquitectura y ER
├── tests/
│   ├── test_api.py                # Pruebas de API REST, catálogo y cálculos en COP
│   └── test_auth_admin.py         # Pruebas de autenticación y control de acceso RBAC
├── .env.example                   # Plantilla de variables de entorno segura
├── .gitignore                     # Exclusión de entornos, secretos y SQLite generado
├── requirements.txt               # Dependencias Python del proyecto
└── README.md                      # Documentación integral del sistema
```

### Descripción de carpetas y archivos

| Ruta | Descripción |
|---|---|
| `app.py` | Fábrica principal de Flask; registra blueprints públicos, de autenticación, administrativos y API REST; maneja errores globales. |
| `configs/settings.py` | Carga `.env`; define el backend activo (`DATABASE_BACKEND`), credenciales seguras de Firebase, rutas y tasa USD/COP. |
| `controllers/shop_controller.py` | Controla las vistas públicas: Landing Page (`/`), Tienda Oficial (`/tienda`), Detalle de producto (`/producto/<id>`) y Carrito (`/carrito`). |
| `controllers/auth_controller.py` | Gestiona inicio de sesión, registro de nuevos clientes y cierre de sesión; implementa decoradores `@login_required` y `@admin_required`. |
| `controllers/admin_controller.py` | Controla el panel administrativo protegido: Dashboard de KPIs, CRUD completo de productos, gestión de categorías y clientes. |
| `controllers/api_controller.py` | Expone endpoints RESTful versionados (`/api/v1/*`) para catálogo y operaciones del carrito sin recargar la página. |
| `services/cart_service.py` | Reglas del carrito de compras: verificación de existencia, disponibilidad de stock y cálculo de totales en COP. |
| `models/firebase_db.py` | Capa de persistencia en la nube; realiza operaciones REST (GET, PUT, POST, PATCH, DELETE) sobre Firebase Realtime Database. |
| `models/auth_model.py` | Modelo de autenticación; valida credenciales, aplica hashing seguro de contraseñas (PBKDF2-SHA256) y gestiona usuarios. |
| `models/catalog.py` | Repositorio unificado de catálogo; abstrae el origen de datos (Firebase o SQLite) entregando entidades consistentes a la aplicación. |
| `models/database.py` | Maneja la conexión local SQLite por solicitud, transacciones y consultas parametrizadas. |
| `models/database_setup.py` | Crea las tablas SQLite e importa marcas, categorías y los 3,718 productos desde el CSV al inicializarse. |
| `models/database_errors.py` | Excepciones personalizadas para manejo controlado de fallas en conexiones de datos. |
| `models/entities.py` | Entidad `Product` inmutable con métodos de conversión y serialización para vistas y API. |
| `templates/index.html` | Landing Page moderna con Hero corporativo, carrusel interactivo de categorías con SVG, productos destacados y contacto. |
| `templates/shop.html` | Tienda Oficial dedicada con buscador integrado, filtros por categoría, ordenamiento y paginación. |
| `templates/auth/login.html` | Vista de inicio de sesión con alertas de error y redirección según rol. |
| `templates/auth/register.html` | Vista de registro para nuevos clientes con validación en servidor. |
| `templates/admin/` | Conjunto de vistas del panel administrativo con sidebar slider colapsible (Dashboard, Productos, Formulario, Categorías, Clientes). |
| `scripts/migrate_to_firebase.py` | Script automatizado para migrar y estructurar todo el catálogo CSV y usuarios en Firebase Realtime Database. |
| `scripts/create_admin.py` | Script interactivo/automático para dar de alta el usuario administrador inicial. |
| `docs/ARQUITECTURA_Y_MIGRACION.md` | Documentación técnica específica para la sustentación sobre la migración cloud y separación de módulos. |
| `tests/test_auth_admin.py` | Pruebas unitarias de autenticación, hashing y protección de rutas administrativas. |
| `tests/test_api.py` | Pruebas unitarias del catálogo, carrito y endpoints REST. |

### Separación de responsabilidades

- **Presentación:** `templates/`, `static/css/` y `static/js/`. El CSS se mantiene intencionalmente sencillo; el JS envía operaciones de carrito al servidor.
- **Controladores:** `controllers/`. Convierten rutas HTTP en llamadas a repositorios/servicios y devuelven HTML o JSON.
- **Servicios:** `services/`. Contienen reglas de negocio reutilizables, como cantidad positiva y disponibilidad.
- **Modelos y repositorios:** `models/`. `Product` expresa la entidad; `catalog.py` contiene las consultas; `database.py` aísla el conector.
- **Configuración:** `configs/` y `.env`. `app.py` se limita a ensamblar la aplicación y registrar rutas.

Flujo de página: `GET /` → `shop_controller.home` → `catalog.fetch_products` → `database.query_all` → SQLite → entidades `Product` → `templates/index.html` → HTML al navegador. El template recibe los productos que leyó el repositorio; ni HTML ni JavaScript se conectan directamente a la base.

Flujo del carrito: `static/js/app.js` → `POST /api/v1/carrito/productos` → `api_controller.add_cart_product` → `cart_service.add_product` → `catalog.fetch_product` → `database.query_one` → SQLite. Si la validación pasa, Flask guarda el identificador y la cantidad en la sesión firmada y devuelve JSON.

## Base de datos SQLite y catálogo tecnológico

La aplicación utiliza SQLite local y el CSV tecnológico incluido en `database/data/amazon_tech_products_ecommerceGKALI.csv`. La carga normaliza los 3718 productos en tablas relacionadas; no requiere configurar un servidor de base de datos ni agrega productos ficticios.

Fotografías recibidas: [diagrama E-R](Diagramas/00952644-87a4-4592-88a8-c89ece649397.jpg), [diagrama relacional](Diagramas/7fb1f902-c15e-4352-b5a3-c4fbf986b62c.jpg) y [definición de datos](Diagramas/a350a0e5-0d53-40ba-b681-b3a2be6532be.jpg).

| Tabla | Clave primaria | Campos y relación |
|---|---|---|
| `marca` | `id_marca` | `nombre` único. Una marca puede asociarse a muchos productos. |
| `categoria_principal` | `id_main_cat` | `nombre` único. Una categoría contiene subcategorías. |
| `subcategoria` | `id_subcat` | `id_main_cat` FK y `nombre`; nombre único dentro de su categoría. |
| `producto` | `id_producto` (`TEXT`) | Nombre del producto tecnológico, descripción, precio base en USD, calificación, reseñas, stock, enlaces e imagen, con claves foráneas a marca y subcategoría. |

Relaciones: marca 1:N producto; categoría principal 1:N subcategoría; subcategoría 1:N producto. Las claves foráneas y restricciones de SQLite protegen la integridad; los índices sirven las búsquedas y relaciones principales. `seed.sql` contiene solo la taxonomía tecnológica existente en los datos, mientras que los productos se importan desde el CSV como única fuente verificable.

El catálogo cubre smartphones Android e iPhone, laptops (incluidos equipos gaming), PC de escritorio y mini PC, mouse y teclados, monitores, audio, tablets, relojes, almacenamiento y docks. El CSV disponible no contiene productos clasificados como consolas ni videojuegos; no se inventan artículos ni se muestran categorías vacías. Para completar esas líneas se requiere un CSV real con esos productos.

La primera solicitud web crea `database/lepetit.sqlite3`, ejecuta el esquema y las categorías y carga los productos en una transacción. La base poblada no se importa de nuevo en cada solicitud. Para reconstruirla desde un CSV actualizado, detén Flask y elimina el archivo SQLite generado.

### Conexión entre Flask y SQLite

La aplicación utiliza el módulo `sqlite3` incluido en Python; no requiere un servidor SQL separado, una cuenta de base de datos ni credenciales de MySQL. `models/database.py` abre una conexión a `DATABASE_PATH` cuando una solicitud Flask necesita datos, activa las claves foráneas y configura filas accesibles por nombre. La conexión queda asociada al contexto de esa solicitud y se cierra al terminarla. Las consultas usan parámetros `?` en lugar de concatenar valores del usuario.

En la primera consulta, `models/database_setup.py` crea las tablas definidas en `database/schema.sql`, aplica las categorías de `database/seed.sql` e importa el CSV si la tabla `producto` aún no tiene registros. La importación valida las columnas y valores, crea marcas y subcategorías faltantes y confirma los datos dentro de una transacción. Si faltan datos o hay conflictos, la carga se revierte y Flask reporta que la base no está disponible; no presenta un catálogo vacío como si hubiera sido importado correctamente.

La ruta `GET /api/v1/salud` ejecuta `SELECT 1` a través de la misma capa de datos. La insignia del encabezado consulta esa ruta y muestra el estado devuelto por Flask, por lo que el navegador nunca abre una conexión SQL directa.

| Variable | Valor predeterminado | Uso |
|---|---|---|
| `DATABASE_PATH` | `database/lepetit.sqlite3` | Ruta de la base SQLite local. |
| `DATASET_CSV_PATH` | `database/data/amazon_tech_products_ecommerceGKALI.csv` | Ruta del catálogo tecnológico de origen. |
| `USD_TO_COP_RATE` | `4200` | Conversión de precios base USD a COP; no es una cotización en tiempo real. |

Las rutas relativas se resuelven desde la carpeta del proyecto. Se pueden cambiar en el archivo `.env`, creado a partir de `.env.example`; la base SQLite generada y las credenciales locales no se suben a Git.

### Tecnología y respaldo de imágenes

Cada producto conserva el campo `image_url` que viene en el CSV y la página intenta mostrar esa URL. Como algunas imágenes remotas de Amazon no responden en el navegador, `static/js/app.js` escucha los errores de carga y selecciona una fotografía representativa de Unsplash según la subcategoría. Si tampoco se puede cargar la imagen remota, se usa `static/img/product-placeholder.svg`.

Las fotografías de Unsplash se sirven desde su CDN mediante URLs directas por identificador; el proyecto no llama a una API de imágenes ni necesita una clave. Son recursos ilustrativos por categoría y no una garantía de que la fotografía corresponda al SKU exacto. Las imágenes remotas requieren conexión a Internet; el SVG local permite mantener un respaldo cuando la red o los CDNs no están disponibles.

## Instalación y ejecución en Windows

**No uses Live Server para abrir `index.html`.** Las vistas usan Jinja y los datos se cargan desde Flask; JavaScript se comunica con la API Flask y Flask ejecuta SQL contra SQLite. Al abrir el HTML estático no existen esas rutas ni la conexión a la base de datos.

Desde PowerShell, en la carpeta del proyecto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Ejecuta Flask; el esquema y la base se inicializan automáticamente desde el CSV:

```powershell
python app.py
```

Abre `http://127.0.0.1:5000`. La primera carga importa el CSV y puede tardar unos segundos. Si la inicialización falla, la aplicación presenta un error `503`; confirma que existe el CSV y que `database/` permita escritura.

La insignia superior llama a `GET /api/v1/salud`. El endpoint ejecuta `SELECT 1` desde Flask y confirma la conexión con SQLite. JavaScript no abre conexiones SQL directamente desde el navegador.

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
  - Ficha de detalle (`/producto/<id>`) con galería, reseñas y selector de cantidad.
- **Carrito de compras (`/carrito`):**
  - Agregar, modificar unidades y eliminar productos asíncronamente vía API REST.
  - Validación estricta de existencias y stock en servidor.
  - Conversión y presentación monetaria en Pesos Colombianos (COP) con separadores locales.
- **Módulo de Autenticación y Control de Acceso (RBAC):**
  - Registro de clientes con contraseñas encriptadas mediante PBKDF2-SHA256 (`/registro`).
  - Inicio de sesión con redirección automática según rol (`/login`).
  - Decoradores de seguridad `@login_required` y `@admin_required` para proteger endpoints.
- **Panel Administrativo (`/admin`):**
  - Layout aislado con Sidebar Slider colapsible (menú retráctil en escritorio y drawer modal en móviles).
  - **Dashboard:** Métricas clave (KPIs) en tiempo real: total productos, categorías, clientes registrados, stock global y valuación.
  - **Inventario:** Tabla interactiva con búsqueda, badges de stock y acciones directas.
  - **CRUD de Productos:** Formulario para crear y editar productos completos.
  - **Gestión de Categorías:** CRUD y monitoreo de productos asociados por categoría.
  - **Gestión de Clientes:** Directorio de usuarios y roles registrados.

### Cuentas de Acceso para Pruebas

| Rol | Correo Electrónico | Contraseña | Acceso |
|---|---|---|---|
| **Administrador** | `admin@lepetit.com` | `admin123` | Portal de Tienda y Panel `/admin` |
| **Cliente** | `cliente@lepetit.com` | `cliente123` | Portal de Tienda y Carrito |

## API REST

Prefijo y versión: `/api/v1`. Las respuestas exitosas usan `{ "data": ... }`; los errores usan `{ "error": { "code": "...", "message": "..." } }`.

| Método | Ruta | Parámetros / JSON | Respuestas principales |
|---|---|---|---|
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

Para obtener y ejecutar la versión publicada:

```powershell
git clone https://github.com/Juan2351/Tech_e-commerce.git
Set-Location .\Tech_e-commerce
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configura en tu archivo `.env` el motor de persistencia deseado:
- Para usar **Firebase Realtime Database (Nube)**:
  ```env
  DATABASE_BACKEND=firebase
  FIREBASE_DATABASE_URL=https://lepetit-e4386-default-rtdb.firebaseio.com
  FIREBASE_API_KEY=tu-api-key
  ```
  *(Opcional: ejecuta `python scripts/migrate_to_firebase.py` para sincronizar o poblar Firebase desde el CSV).*

- Para usar **SQLite (Local)**:
  ```env
  DATABASE_BACKEND=sqlite
  DATABASE_PATH=database/lepetit.sqlite3
  ```

Inicia la aplicación:
```powershell
python app.py
```

Abre `http://127.0.0.1:5000` en tu navegador.
- Landing Page: `http://127.0.0.1:5000/`
- Tienda Oficial: `http://127.0.0.1:5000/tienda`
- Iniciar Sesión: `http://127.0.0.1:5000/login`
- Panel Administrativo: `http://127.0.0.1:5000/admin` (Credenciales: `admin@lepetit.com` / `admin123`)

## Validación y Pruebas Automatizadas

Instala dependencias y ejecuta la suite completa de pruebas:

```powershell
python -m unittest discover tests -v
```

Los 24 tests automatizados comprueban:
- Endpoints RESTful de productos, categorías, salud y carrito.
- Cálculos y validaciones de stock, cantidades positivas y subtotales en COP.
- Autenticación, registro, hashing seguro de contraseñas y cierre de sesión.
- Control de acceso RBAC protegiendo el panel `/admin` contra accesos no autorizados.
- Renderizado de vistas HTML y fallback visual de imágenes.


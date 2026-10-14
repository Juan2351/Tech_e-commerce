# LePetit

LePetit es una tienda web de demostración para consultar un catálogo de productos, filtrar por categoría, revisar detalles y mantener un carrito temporal. Está organizada por MVC y capas para que las vistas, los controladores, las reglas del carrito y el acceso a SQLite no queden mezclados en un único archivo.

## Descripción del sistema

- **Problema:** presentar un catálogo de comercio electrónico consultable y una interacción básica de compra sin mezclar la interfaz con las consultas de datos.
- **Objetivo:** mostrar productos, precios en pesos colombianos (COP), marcas, categorías, stock y permitir modificar un carrito.
- **Usuarios:** cliente visitante. No hay cuentas de usuario ni panel de administración en este prototipo.
- **Funcionalidades implementadas:** listar, buscar y filtrar productos; ordenar por precio o calificación; consultar detalle; agregar, actualizar y quitar productos del carrito; consultar endpoints REST.
- **Información almacenada:** título del producto, precio base, calificación, reseñas, stock, enlaces, imagen, marca, categoría principal y subcategoría. El carrito se guarda temporalmente en la sesión Flask firmada.
- **Integraciones:** SQLite local para el catálogo y un CDN externo para imágenes de muestra. No se integra pasarela de pagos, autenticación, mapas, correo ni WhatsApp.

## Tecnologías y decisiones

| Área | Tecnología | Decisión |
|---|---|---|
| Backend | Python 3 y Flask | Backend único ligero, dividido en controladores y servicios. |
| Presentación | HTML5 semántico y Jinja | Las páginas se renderizan desde el servidor. |
| Interacción del navegador | JavaScript sin framework | La API REST gestiona el carrito sin recargar la página al agregar. |
| Estilos | CSS propio mínimo | Paleta blanca, gris y negra, adaptable a pantallas pequeñas y efectos hover discretos. |
| Persistencia | SQLite | Base relacional local que se crea automáticamente; no requiere instalar ni configurar un servidor. |
| Acceso a datos | `sqlite3` de Python y SQL parametrizado | Evita sumar ORM y mantiene visibles el DDL y las relaciones SQL. |
| Configuración | `.env` local y `python-dotenv` | Permite cambiar rutas locales y la tasa de conversión sin incluir configuración privada. |
| Documentación | Mermaid y OpenAPI 3.0 | Fuentes editables para C1-C4, modelo relacional y contrato HTTP. |

La lista inicial también menciona Java. No se utiliza en esta versión: se seleccionó Python/Flask como único backend para mantener un solo servidor y una arquitectura coherente. El proyecto tampoco necesita React porque Flask entrega HTML y el JavaScript consume la API en el mismo origen.

Los valores `precio` del CSV son precios base en USD. Se muestran en COP calculando `precio × USD_TO_COP_RATE`. La tasa por defecto es `4200`, se valida como número finito positivo y puede cambiarse en `.env`; no representa una cotización en tiempo real ni requiere una integración monetaria externa.

## Arquitectura MVC y árbol de carpetas

```text
ECOMMERCELEPETIT/
├── app.py                         # Fábrica Flask, registro de rutas y errores
├── configs/
│   └── settings.py                # Variables de entorno y configuración
├── controllers/
│   ├── api_controller.py          # Endpoints JSON versionados
│   └── shop_controller.py         # Rutas de las páginas HTML
├── services/
│   └── cart_service.py            # Reglas de stock y carrito
├── models/
│   ├── database.py                # Conexión SQLite, consultas y cierre
│   ├── database_setup.py          # Creación del esquema e importación inicial del CSV
│   ├── database_errors.py         # Error de configuración y carga del catálogo
│   ├── catalog.py                 # Repositorio SQL de productos y categorías
│   └── entities.py                # Modelo Product y serialización
├── templates/                     # Páginas HTML renderizadas por Flask/Jinja
├── static/
│   ├── css/styles.css             # Estilos adaptables de la tienda
│   ├── js/app.js                  # Interacción del carrito y estado de la base local
│   └── img/product-placeholder.svg # Imagen de respaldo para productos
├── database/
│   ├── schema.sql                 # Tablas, relaciones e índices SQLite
│   ├── seed.sql                   # Categorías tecnológicas del catálogo
│   ├── data/                      # CSV de catálogo cargado automáticamente
│   └── queries.sql                # Consultas SQLite para validación
├── Diagramas/                     # Fotografías compartidas como insumo
├── docs/
│   ├── C4.md                      # Explicación C1-C4 y flujo principal
│   ├── openapi.yaml               # Contrato de la API REST
│   └── diagramas/                 # Mermaid: C1, C2, C3, C4 y ER
├── tests/
├── .env.example                   # Plantilla sin secretos
├── .gitignore
├── requirements.txt
└── README.md
```

### Descripción de carpetas y archivos

| Ruta | Descripción |
|---|---|
| `app.py` | Crea la aplicación Flask, registra las rutas de la tienda y la API, configura el cierre de conexiones y presenta errores HTTP o de base de datos. |
| `configs/settings.py` | Carga `.env` y centraliza las rutas de SQLite y del CSV, la tasa USD/COP y HTTPS local. |
| `controllers/shop_controller.py` | Atiende las páginas HTML: catálogo, detalle de producto y carrito. Valida filtros de búsqueda y entrega los datos a las plantillas. |
| `controllers/api_controller.py` | Expone las rutas JSON versionadas para consultar salud, productos, categorías y modificar el carrito. |
| `services/cart_service.py` | Implementa las reglas del carrito: validar identificador y cantidad, comprobar existencia y stock, y calcular subtotales. |
| `models/database.py` | Abre y cierra conexiones SQLite por solicitud y proporciona consultas parametrizadas de una fila o varias filas. |
| `models/database_setup.py` | Crea las tablas e importa marcas, categorías y productos del CSV la primera vez que se usa la base. |
| `models/database_errors.py` | Define el error explícito de inicialización o configuración de la base local. |
| `models/catalog.py` | Consulta productos, categorías y subcategorías; aplica búsqueda, filtros y ordenamiento, y convierte filas a entidades. |
| `models/entities.py` | Define la entidad `Product` y la conversión de registros de base de datos a productos de la aplicación. |
| `templates/base.html` | Estructura compartida de las páginas: idioma, metadatos, navegación, contador del carrito, avisos, CSS y JavaScript. |
| `templates/index.html` | Página del catálogo; muestra búsqueda, filtros, ordenamiento y tarjetas de productos con precio, stock y acción para agregar al carrito. |
| `templates/product_detail.html` | Detalle de producto con imagen, descripción, marca, calificación, precio, disponibilidad y selector de cantidad. |
| `templates/cart.html` | Resumen del carrito con cantidades editables, opción para quitar productos y total estimado; informa que no procesa pagos. |
| `templates/error.html` | Página de error HTML para solicitudes del sitio que no pueden completarse. |
| `static/css/styles.css` | Reglas visuales de la tienda, componentes, estados y presentación adaptable a distintos tamaños de pantalla. |
| `static/js/app.js` | Envía operaciones del carrito a la API, actualiza el contador y los mensajes, verifica la base local y reemplaza imágenes que no cargan por el recurso local. |
| `static/img/product-placeholder.svg` | Imagen local utilizada cuando un producto no tiene imagen disponible o la imagen remota falla. |
| `database/schema.sql` | Define las tablas SQLite, las claves foráneas, las restricciones y los índices del catálogo. |
| `database/seed.sql` | Prepara categorías y subcategorías de tecnología; no incluye productos ficticios. |
| `database/data/amazon_tech_products_ecommerceGKALI.csv` | Datos de entrada con 3718 productos tecnológicos que se importan en el primer acceso a SQLite. |
| `database/lepetit.sqlite3` | Base de datos generada automáticamente; no se versiona y se regenera desde el CSV si se elimina. |
| `database/queries.sql` | Incluye consultas de comprobación para explorar los datos y validar relaciones. |
| `docs/openapi.yaml` | Describe el contrato de la API REST, sus parámetros, respuestas y errores. |
| `docs/C4.md` y `docs/diagramas/` | Explican la arquitectura y contienen fuentes Mermaid editables para los diagramas C1-C4 y el modelo entidad-relación. |
| `Diagramas/` | Conserva las imágenes de diagramas y definiciones recibidas como material de referencia. |
| `tests/test_api.py` | Prueba endpoints, validaciones, reglas del carrito, conversión de precios y renderizado HTML usando datos controlados. |
| `.env.example` | Plantilla de variables de entorno sin credenciales reales; se copia a `.env` para configurar cada entorno local. |
| `.gitignore` | Evita incluir archivos locales o generados que no pertenecen al código versionado. |
| `requirements.txt` | Declara las dependencias Python necesarias para ejecutar la aplicación. |
| `.vscode/settings.json` | Configuración del editor VS Code para este proyecto. |
| `README.md` | Guía del proyecto: arquitectura, configuración, ejecución, base de datos, API y validación. |

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

- Catálogo de 3718 productos tecnológicos importado desde CSV a SQLite y paginado en bloques de 24 para mantener ágil la página.
- Búsqueda por nombre, descripción o marca.
- Filtro por categoría principal y orden por precio ascendente/descendente o valoración.
- Página de detalle con descripción, rating, reseñas y existencias.
- Precios en COP con separador local colombiano y tasa configurable.
- Carrito: agregar, cambiar cantidad, quitar productos; valida existencia y stock.
- Mensajes accesibles de éxito/error; si falla la imagen original de Amazon, carga una foto tecnológica representativa por categoría desde Unsplash y conserva un recurso local como último respaldo.
- Diseño adaptativo básico en gris, blanco y negro. Sin efectos visuales ni dependencias de frontend.

El carrito es temporal en una cookie de sesión Flask firmada. La sesión no contiene el precio como fuente confiable: el servidor vuelve a leer precio y stock en SQLite. No se registra una orden, no se descuenta stock y no se procesa un pago.

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
- No hay autenticación: el MVP solo permite catálogo y carrito de visitante. No se aceptan escrituras de productos ni pagos.

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
# La base local se importa automáticamente desde el CSV:
python app.py
```

No abras `templates/index.html` con Live Server: arranca Flask con `python app.py` y abre `http://127.0.0.1:5000`. Para contribuir después, crea una rama (`git switch -c feature/mi-cambio`), prueba el cambio, haz commit y súbela (`git push -u origin feature/mi-cambio`) para abrir un PR contra `main`. Agregar colaboradores, aprobar PRs o cambiar permisos requiere acceso autorizado al repositorio.

## Validación

Instala dependencias y ejecuta las pruebas:

```powershell
python -m unittest discover -s tests -v
```

Los tests automatizados comprueban formato API, filtros, errores de validación, stock, carrito, renderizado de precios e importación del CSV a SQLite.

## Equipo indicado en las guías

- **Actividad Git, Grupo Ying Yang:** Juan Alberto Trujillo Herrera, Martín Camilo Corredor Pescador y Rubén Darío Peña.
- **Actividad de base de datos, Grupo Matrix:** Juan José Herrera, Francisco Manuel Bermúdez y Rafael Ángel Hernández.
- **Cuenta GitHub facilitada:** CrisArbo.

Los integrantes se listan porque aparecen en las instrucciones compartidas; el equipo debe confirmar si ambos grupos trabajan sobre el mismo repositorio antes de asignar responsabilidades.

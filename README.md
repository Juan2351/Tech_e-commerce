# LePetit

LePetit es una tienda web de demostración para consultar un catálogo de productos, filtrar por categoría, revisar detalles y mantener un carrito temporal. Está organizada por MVC y capas para que las vistas, los controladores, las reglas del carrito y el acceso a MySQL no queden mezclados en un único archivo.

## Descripción del sistema

- **Problema:** presentar un catálogo de comercio electrónico consultable y una interacción básica de compra sin mezclar la interfaz con las consultas de datos.
- **Objetivo:** mostrar productos, precios en pesos colombianos (COP), marcas, categorías, stock y permitir modificar un carrito.
- **Usuarios:** cliente visitante. No hay cuentas de usuario ni panel de administración en este prototipo.
- **Funcionalidades implementadas:** listar, buscar y filtrar productos; ordenar por precio o calificación; consultar detalle; agregar, actualizar y quitar productos del carrito; consultar endpoints REST.
- **Información almacenada:** productos, precio base, descripción, rating, reseñas, stock, URL de imagen, marca, categoría principal y subcategoría. El carrito se guarda temporalmente en la sesión Flask firmada.
- **Integraciones:** MySQL para el catálogo y un CDN externo para imágenes de muestra. No se integra pasarela de pagos, autenticación, mapas, correo ni WhatsApp.

## Tecnologías y decisiones

| Área | Tecnología | Decisión |
|---|---|---|
| Backend | Python 3 y Flask | Backend único ligero, dividido en controladores y servicios. |
| Presentación | HTML5 semántico y Jinja | Las páginas se renderizan desde el servidor. |
| Interacción del navegador | JavaScript sin framework | La API REST gestiona el carrito sin recargar la página al agregar. |
| Estilos | CSS propio mínimo | Paleta blanca, gris y negra, adaptable a pantallas pequeñas y efectos hover discretos. |
| Persistencia | MySQL 8 e InnoDB | Modelo relacional preparado para ejecución y consulta desde DBeaver. |
| Acceso a datos | `mysql-connector-python` y SQL parametrizado | Evita sumar ORM al prototipo y deja visibles el DDL y las relaciones SQL. |
| Configuración | `.env` local y `python-dotenv` | Las credenciales no se escriben en el código ni se suben al repositorio. |
| Documentación | Mermaid y OpenAPI 3.0 | Fuentes editables para C1-C4, modelo relacional y contrato HTTP. |

La lista inicial también menciona Java. No se utiliza en esta versión: se seleccionó Python/Flask como único backend para mantener un solo servidor y una arquitectura coherente. El proyecto tampoco necesita React porque Flask entrega HTML y el JavaScript consume la API en el mismo origen.

Los valores `precio` del esquema y de los datos de ejemplo son precios base en USD. Se muestran en COP calculando `precio × USD_TO_COP_RATE`. La tasa por defecto es `4200`, se valida como número finito positivo y se configura manualmente en `.env`; no representa una cotización en tiempo real ni requiere una integración monetaria externa. Actualiza la tasa antes de una demostración si necesitas otra conversión.

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
│   ├── database.py                # Conexión MySQL, consultas y cierre
│   ├── catalog.py                 # Repositorio SQL de productos y categorías
│   └── entities.py                # Modelo Product y serialización
├── templates/                     # Vistas HTML Jinja
├── static/
│   ├── css/styles.css             # Estilos básicos gris/blanco/negro
│   ├── js/app.js                  # Cliente JavaScript de la API del carrito
│   └── img/product-placeholder.svg
├── database/
│   ├── schema.sql                 # Creación de base y tablas MySQL
│   ├── seed.sql                   # Datos de ejemplo
│   └── queries.sql                # Consultas para validación
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

### Separación de responsabilidades

- **Presentación:** `templates/`, `static/css/` y `static/js/`. El CSS se mantiene intencionalmente sencillo; el JS envía operaciones de carrito al servidor.
- **Controladores:** `controllers/`. Convierten rutas HTTP en llamadas a repositorios/servicios y devuelven HTML o JSON.
- **Servicios:** `services/`. Contienen reglas de negocio reutilizables, como cantidad positiva y disponibilidad.
- **Modelos y repositorios:** `models/`. `Product` expresa la entidad; `catalog.py` contiene las consultas; `database.py` aísla el conector.
- **Configuración:** `configs/` y `.env`. `app.py` se limita a ensamblar la aplicación y registrar rutas.

Flujo de página: `GET /` → `shop_controller.home` → `catalog.fetch_products` → `database.query_all` → MySQL → entidades `Product` → `templates/index.html` → HTML al navegador. El template recibe los productos que leyó el repositorio; ni HTML ni JavaScript se conectan directamente a MySQL.

Flujo del carrito: `static/js/app.js` → `POST /api/v1/carrito/productos` → `api_controller.add_cart_product` → `cart_service.add_product` → `catalog.fetch_product` → `database.query_one` → MySQL. Si la validación pasa, Flask guarda el identificador y la cantidad en la sesión firmada y devuelve JSON.

## Base de datos MySQL

El diagrama parte de las fotos compartidas y del ER suministrado. Se conservan las cuatro entidades y sus claves, se añade `nombre` al producto para que el catálogo tenga un título visible y se marca el precio como USD base para documentar la transformación a COP.

Fotografías recibidas: [diagrama E-R](Diagramas/00952644-87a4-4592-88a8-c89ece649397.jpg), [diagrama relacional](Diagramas/7fb1f902-c15e-4352-b5a3-c4fbf986b62c.jpg) y [definición de datos](Diagramas/a350a0e5-0d53-40ba-b681-b3a2be6532be.jpg).

| Tabla | Clave primaria | Campos y relación |
|---|---|---|
| `marca` | `id_marca` | `nombre` único. Una marca puede asociarse a muchos productos. |
| `categoria_principal` | `id_main_cat` | `nombre` único. Una categoría contiene subcategorías. |
| `subcategoria` | `id_subcat` | `id_main_cat` FK y `nombre`; nombre único dentro de su categoría. |
| `producto` | `id_producto` (`VARCHAR(64)`) | Nombre, descripción, precio `DECIMAL`, rating, reseñas, stock, URL, imagen, `id_marca` FK y `id_subcat` FK. |

Relaciones: marca 1:N producto; categoría principal 1:N subcategoría; subcategoría 1:N producto. Las restricciones de clave foránea protegen la integridad. InnoDB aplica las relaciones; no se permite borrar una marca/categoría referenciada. Los índices sirven las búsquedas y relaciones principales.

### Crear y poblar la base

1. Instala y ejecuta MySQL 8.
2. Abre DBeaver, crea una conexión MySQL y conéctate con un usuario que pueda crear la base de datos.
3. Ejecuta `database/schema.sql`; crea `lepetit` y sus cuatro tablas.
4. Ejecuta `database/seed.sql` para insertar los datos de demostración.
5. Ejecuta `database/queries.sql` para revisar joins, categorías, productos disponibles y posibles referencias inválidas.
6. Crea un usuario de aplicación con permiso de lectura sobre `lepetit` (las operaciones del catálogo son de consulta); el usuario administrativo de la base no debe quedar en `.env` de producción.
7. Copia `.env.example` como `.env`, completa `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` y la tasa COP. El controlador de productos usa conexión MySQL y no crea ni modifica tablas automáticamente.

Los datos de `seed.sql` son sintéticos, no proceden de un Excel/CSV del equipo; por eso no se afirma que se haya limpiado una fuente externa. Si se recibe un archivo real, revisar duplicados, nombres, categorías, precios y stock antes de importarlo.

## Instalación y ejecución en Windows

**No uses Live Server para abrir `index.html`.** Las vistas usan Jinja y los datos se cargan desde Flask; JavaScript se comunica con la API Flask y Flask ejecuta SQL contra MySQL. Al abrir el HTML estático no existen esas rutas ni la conexión a la base de datos.

Desde PowerShell, en la carpeta del proyecto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Completa `.env`, configura MySQL y ejecuta:

```powershell
python app.py
```

Abre `http://127.0.0.1:5000`. El servidor no crea el esquema: la base y los datos deben cargarse antes siguiendo los pasos anteriores. En caso de error de conexión la aplicación presenta un error `503` explícito; revisa la configuración y que MySQL esté activo.

La insignia superior llama a `GET /api/v1/salud`. El endpoint ejecuta `SELECT 1` desde el backend y muestra si Flask logró comunicarse con MySQL. JavaScript no guarda credenciales ni abre conexiones SQL directamente desde el navegador.

### HTTPS local

El desarrollo local funciona en HTTP. Para probar HTTPS, genera un certificado de desarrollo fuera del repositorio y define `SSL_CERT_FILE` y `SSL_KEY_FILE` en `.env`; deben configurarse ambos. Flask inicia HTTPS local con ese certificado. No compartas ni subas certificados privados. En producción, termina HTTPS en un proxy inverso y activa `SESSION_COOKIE_SECURE=true`.

## Funcionalidades web

- Catálogo poblado desde MySQL.
- Búsqueda por nombre, descripción o marca.
- Filtro por categoría principal y orden por precio ascendente/descendente o valoración.
- Página de detalle con descripción, rating, reseñas y existencias.
- Precios en COP con separador local colombiano y tasa configurable.
- Carrito: agregar, cambiar cantidad, quitar productos; valida existencia y stock.
- Mensajes accesibles de éxito/error y fallback local si una imagen externa no carga.
- Diseño adaptativo básico en gris, blanco y negro. Sin efectos visuales ni dependencias de frontend.

El carrito es temporal en una cookie de sesión Flask firmada. La sesión no contiene el precio como fuente confiable: el servidor vuelve a leer precio y stock en MySQL. No se registra una orden, no se descuenta stock y no se procesa un pago.

## API REST

Prefijo y versión: `/api/v1`. Las respuestas exitosas usan `{ "data": ... }`; los errores usan `{ "error": { "code": "...", "message": "..." } }`.

| Método | Ruta | Parámetros / JSON | Respuestas principales |
|---|---|---|---|
| GET | `/api/v1/salud` | — | 200, 503 |
| GET | `/api/v1/productos` | Opcionales: `category_id`, `subcategory_id`, `q`, `sort` (`featured`, `price_asc`, `price_desc`, `rating_desc`) | 200, 400 |
| GET | `/api/v1/productos/{id}` | ID de producto | 200, 404 |
| GET | `/api/v1/categorias` | — | 200 |
| GET | `/api/v1/carrito` | — | 200 |
| POST | `/api/v1/carrito/productos` | `{"product_id":"LP-001","quantity":1}` | 201, 400, 404, 409 |
| PATCH | `/api/v1/carrito/productos/{id}` | `{"quantity":2}` | 200, 400, 404, 409 |
| DELETE | `/api/v1/carrito/productos/{id}` | ID de producto | 204, 404 |

`400` indica formato o valor inválido; `404`, recurso ausente; `409`, stock insuficiente; `503`, base de datos sin conexión/configuración. Los filtros y cantidades se validan en el servidor, los valores SQL se parametrizan y `sort` se escoge de una lista permitida.

El contrato legible por herramientas está en [docs/openapi.yaml](docs/openapi.yaml). El navegador y la API tienen el mismo origen; no se habilita CORS abierto. Si se separa el frontend en otro dominio, debe permitirse explícitamente solo ese origen y revisar credenciales/cookies antes de desplegar.

### Probar con curl

```powershell
curl.exe "http://127.0.0.1:5000/api/v1/productos?category_id=1&sort=price_asc"
curl.exe "http://127.0.0.1:5000/api/v1/productos/LP-001"
curl.exe -X POST "http://127.0.0.1:5000/api/v1/carrito/productos" `
  -H "Content-Type: application/json" `
  -d "{\"product_id\":\"LP-001\",\"quantity\":1}"
```

Para conservar la cookie de sesión entre llamadas API con curl, agrega `-c cookies.txt` al POST y `-b cookies.txt` a las consultas siguientes.

## Diagramas y exposición C4

La explicación y el flujo están en [docs/C4.md](docs/C4.md). Los fuentes editables Mermaid están en `docs/diagramas/`:

- [C1 Contexto](docs/diagramas/C1-contexto.mmd): actor, sistema y servicio externo de imágenes.
- [C2 Contenedores](docs/diagramas/C2-contenedores.mmd): navegador, aplicación Flask y MySQL.
- [C3 Componentes](docs/diagramas/C3-componentes.mmd): componentes internos del backend.
- [C4 Código del carrito](docs/diagramas/C4-funcionalidad-carrito.mmd): módulos, métodos, base de datos y sesión.
- [Modelo ER](docs/diagramas/modelo-entidad-relacion.mmd): tablas, claves y cardinalidades.

Para explicar la exposición: C1, quién usa LePetit; C2, navegador, servidor y base de datos; C3, responsabilidades internas de Flask; C4, la petición de agregar un producto y sus validaciones.

## Actividades cubiertas

### Modelado y MySQL

1. Se definieron producto, marca, categoría y subcategoría.
2. Se acordaron formatos de categoría y valores de ejemplo; no se recibió fuente real para depurar.
3. Se documentaron entidades, atributos y cardinalidades en el ER.
4. Se declararon claves primarias, únicas y foráneas.
5. Se conservaron los diagramas entregados y se añadió el ER Mermaid coherente con el SQL.
6. `schema.sql` crea el esquema MySQL con tipos, restricciones e índices.
7. `seed.sql` registra productos de demostración en orden relacional.
8. `queries.sql` revisa joins y posibles referencias inválidas.
9. La consulta de catálogo implementa búsqueda, filtro y ordenamiento; el stock se valida para el carrito.
10. `models/database.py` conecta Flask con MySQL desde variables locales.

### Arquitectura web y contrato HTTP

- El blueprint de carpetas está implementado según el árbol anterior; no hay un `app.py` monolítico.
- El contrato API está versionado, usa sustantivos plurales, filtros y estados HTTP explícitos.
- Los endpoints API sirven tanto a la interfaz JavaScript como a clientes de prueba.
- No se activa CORS porque la aplicación consume la API en su mismo origen.
- HTTPS local se puede habilitar con certificado propio; HTTP queda para el desarrollo simple.
- No hay autenticación: el MVP solo permite catálogo y carrito de visitante. No se aceptan escrituras de productos ni pagos.

### Git y GitHub

El repositorio del equipo es [Juan2351/Tech_e-commerce](https://github.com/Juan2351/Tech_e-commerce). Esta entrega reemplaza el árbol funcional anterior por LePetit y conserva el historial Git existente. El desarrollo y la publicación se hacen en la rama `main`; no se crean commits ficticios ni se afirma que existan PRs o invitaciones de colaboradores.

Para obtener y ejecutar la versión publicada:

```powershell
git clone https://github.com/Juan2351/Tech_e-commerce.git
Set-Location .\Tech_e-commerce
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edita .env, prepara MySQL siguiendo la sección anterior y luego:
python app.py
```

No abras `templates/index.html` con Live Server: arranca Flask con `python app.py` y abre `http://127.0.0.1:5000`. Para contribuir después, crea una rama (`git switch -c feature/mi-cambio`), prueba el cambio, haz commit y súbela (`git push -u origin feature/mi-cambio`) para abrir un PR contra `main`. Agregar colaboradores, aprobar PRs o cambiar permisos requiere acceso autorizado al repositorio.

## Validación

Instala dependencias y ejecuta las pruebas:

```powershell
python -m unittest discover -s tests -v
```

Los tests automatizados comprueban formato API, filtros, errores de validación, stock, carrito y renderizado de precios. La ejecución de sentencias DDL y del seed en MySQL debe validarse en la instancia de MySQL/DBeaver del equipo.

## Equipo indicado en las guías

- **Actividad Git, Grupo Ying Yang:** Juan Alberto Trujillo Herrera, Martín Camilo Corredor Pescador y Rubén Darío Peña.
- **Actividad MySQL, Grupo Matrix:** Juan José Herrera, Francisco Manuel Bermúdez y Rafael Ángel Hernández.
- **Cuenta GitHub facilitada:** CrisArbo.

Los integrantes se listan porque aparecen en las instrucciones compartidas; el equipo debe confirmar si ambos grupos trabajan sobre el mismo repositorio antes de asignar responsabilidades.

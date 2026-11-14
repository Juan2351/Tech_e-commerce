# Requisitos y alcance de LePetit

> Documento descriptivo de la implementación actual. No representa una aprobación formal de requisitos por parte de clientes, docente o integrantes del equipo; las necesidades pendientes deben validarse con ellos.

## Propósito

LePetit es una aplicación web de comercio electrónico de demostración para explorar un catálogo tecnológico, mantener un carrito y gestionar productos. El checkout registra solicitudes de pedido, pero no procesa pagos ni confirma ventas.

## Actores

| Actor | Capacidades |
|---|---|
| Visitante | Consultar la página inicial y el catálogo, buscar y filtrar productos, abrir fichas de producto, y registrarse o iniciar sesión. |
| Cliente autenticado | Usar las funciones de cliente, mantener un carrito de sesión y enviar un pedido para confirmación posterior. |
| Administrador autenticado | Consultar métricas y gestionar productos, categorías y clientes desde el panel administrativo. |
| Integración API | Consultar el catálogo y operar el carrito; usar autenticación JWT para las rutas que la requieren. |

## Requisitos funcionales observables

| ID | Requisito |
|---|---|
| RF-01 | La aplicación debe mostrar una página inicial y un catálogo con búsqueda, filtros por categoría, ordenamiento y paginación. |
| RF-02 | La ficha de producto debe mostrar la información disponible en el catálogo y puede incluir un visor 3D esquemático. Las especificaciones presentadas deben derivarse de los datos disponibles. |
| RF-03 | El carrito debe permitir agregar, actualizar y retirar productos, validar cantidades y disponibilidad en el servidor, y calcular importes en COP. |
| RF-04 | El checkout debe validar el formulario, registrar un pedido y su detalle con una captura de los productos y precios, y presentar el pedido como pendiente de confirmación. |
| RF-05 | El registro público debe crear cuentas de cliente. La autenticación y los usuarios se gestionan mediante Firebase; las contraseñas se almacenan con hash, no en texto plano. |
| RF-06 | El acceso al panel y a sus funciones administrativas debe restringirse por rol. El administrador puede consultar el panel y gestionar el inventario, las categorías y los clientes. |
| RF-07 | La API versionada debe ofrecer operaciones de salud, catálogo, categorías y carrito, y publicar su contrato OpenAPI/Swagger. |
| RF-08 | La API debe emitir tokens JWT para inicio de sesión y aplicar autorización de administrador a las operaciones protegidas. |
| RF-09 | La interfaz debe ofrecer recursos gráficos locales de respaldo cuando imágenes externas no estén disponibles. |

## Requisitos no funcionales observables

- **Tecnología:** backend Python con Flask y plantillas Jinja; frontend HTML, CSS y JavaScript, con React/Three.js para componentes 3D específicos.
- **Persistencia:** el catálogo puede usar Firebase Realtime Database o SQLite según la configuración. Las tablas SQLite se inicializan desde el esquema y el CSV local cuando SQLite se utiliza. Los pedidos se almacenan en SQLite; la autenticación usa Firebase.
- **Integridad:** las consultas SQLite parametrizan valores y aplican claves foráneas. Las cantidades y filtros se validan en el servidor.
- **Moneda:** los precios de origen son valores base en USD y la conversión a COP utiliza `USD_TO_COP_RATE`; no es una tasa en tiempo real.
- **Sesión:** el carrito utiliza la sesión de Flask. Para despliegue, las claves y los parámetros de cookies deben configurarse para el entorno y servirse sobre HTTPS.
- **Recursos externos:** las imágenes remotas requieren conectividad; se proporciona un recurso SVG local como respaldo.
- **Ejecución:** Flask sirve las vistas y los recursos compilados; abrir los templates directamente con Live Server no sustituye al backend.

## Límites y fuera de alcance

- No hay pasarela de pago ni procesamiento de cobros.
- El pedido queda pendiente de confirmación; no confirma una venta ni reserva inventario.
- La conversión USD/COP es configurable, pero no consulta una cotización en tiempo real.
- Las imágenes ilustrativas de respaldo no garantizan corresponder al SKU exacto.
- Esta documentación no certifica que el sistema esté preparado para producción; la configuración, los secretos, la persistencia, los respaldos y el despliegue deben revisarse antes de publicar.

## Estado de trabajo reportado

Resumen del tablero Scrum compartido por el equipo, con corte al **11 de noviembre de 2026**. Los estados y prioridades de esta tabla reflejan la captura; las iniciales se transcriben tal como aparecen y no identifican por sí solas a una persona.

| Estado en el tablero | Tarea | Asignación mostrada | Prioridad |
|---|---|---|---|
| En curso | HU 13: Visualización de estado vacío en búsquedas sin resultados | J | — |
| En curso | HU 16: Creación de la sección de Preguntas Frecuentes | J | — |
| En curso | HU 18: Pruebas unitarias básicas de rutas principales | C | — |
| En curso | Validaciones con una API pública | K | — |
| En curso | Seguimiento de métricas (Burndown chart / velocidad del equipo) | J | Urgente |
| En curso | Configuración y mantenimiento del tablero Scrum en ClickUp | J | — |
| En curso | Planificación y facilitación de los Sprints | J | — |
| Pendiente | HU-19: Poner en la página principal un producto en 3D | K | Urgente |
| Pendiente | HU-20: Documentación, contrato técnico y pruebas de la API REST | C | — |
| Pendiente | HU-21: Sistema responsivo y maquetación ágil de la interfaz | K | Urgente |

**Resumen:** 7 tareas en curso y 3 pendientes. La captura no muestra fechas límite.

### Contraste con el repositorio

El estado del tablero representa el seguimiento del equipo; no se modificó a partir de una inspección aislada del código. Hay funcionalidades y evidencia técnica relacionadas que ya aparecen en el repositorio:

- HU 13: `templates/shop.html` ya muestra un mensaje cuando la búsqueda no encuentra productos.
- HU 18: existen pruebas automatizadas Python para rutas y módulos principales; al momento de actualizar esta documentación, la suite registró 39 pruebas aprobadas.
- HU-19: la página inicial ya incluye un escenario 3D y `tests/test_3d_viewer.py` comprueba su renderizado.
- HU-20: existen `docs/openapi.yaml`, Swagger UI y pruebas de API/documentación; la tarea puede incluir trabajo adicional o criterios de aceptación pendientes.
- HU-21: `static/css/styles.css` contiene reglas responsive; esto no acredita por sí solo que la historia cumpla todos sus criterios.

Estos artefactos no implican que las historias estén terminadas o aceptadas. El equipo debe contrastar cada criterio de aceptación y actualizar ClickUp si corresponde. HU 16 y la integración con una API pública siguen descritas según el estado del tablero; no se verificó su finalización en esta actualización.

## Verificación en el código

La suite automatizada cubre, entre otros aspectos, catálogo y API (`tests/test_api.py`), inicio de sesión y permisos (`tests/test_auth_admin.py`), emisión JWT y protección del panel (`tests/test_jwt_dash_docs.py`), checkout (`tests/test_orders.py`) y componentes 3D (`tests/test_3d_viewer.py`, `tests/product-3d.test.js`). Las pruebas sirven como evidencia de comportamiento, pero no sustituyen la aprobación de requisitos por los responsables del proyecto.

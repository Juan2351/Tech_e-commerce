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
│   ├── index.html                  # Landing Page introductoria (Hero, Carruseles, Contacto)
│   ├── shop.html                   # Tienda Oficial dedicada (Buscador, Filtros, Grilla, Paginación)
│   ├── product_detail.html         # Ficha técnica detallada de cada producto
│   ├── cart.html                   # Carrito de compras y cálculo de subtotales
│   ├── auth/                       # Vistas de Autenticación
│   │   ├── login.html              # Formulario de inicio de sesión
│   │   └── register.html           # Formulario de registro de clientes
│   └── admin/                      # Vistas del Panel Administrativo Independiente
│       ├── base_admin.html         # Layout administrativo exclusivo con Sidebar Slider
│       ├── dashboard.html          # Panel de métricas e indicadores KPI
│       ├── products.html           # Inventario general con acciones de edición/eliminación
│       ├── product_form.html       # Formulario para crear y editar productos en Firebase
│       ├── categories.html         # Gestión y CRUD de categorías
│       └── clients.html            # Gestión y listado de usuarios/clientes
│
├── controllers/                    # CONTROLADOR (Rutas, Orquestación y Lógica Web)
│   ├── shop_controller.py          # Rutas de Landing (/), Tienda (/tienda) y Contacto (/contacto)
│   ├── auth_controller.py          # Autenticación (/login, /registro, /logout) y decoradores RBAC
│   ├── admin_controller.py         # Módulo administrativo protegido (/admin/*)
│   └── api_controller.py           # API REST JSON (/api/v1/*) para operaciones asíncronas
│
├── configs/
│   └── settings.py                 # Variables de entorno y configuración de Firebase
│
├── scripts/
│   └── migrate_to_firebase.py      # Script de migración y población masiva en Firebase
│
└── tests/                          # Suite de Pruebas Automatizadas (24 tests pasando)
    ├── test_api.py                 # Pruebas de API, catálogo y cálculos COP
    └── test_auth_admin.py          # Pruebas de autenticación y control de acceso admin
```

---

## 2. Migración a Firebase Realtime Database

### ¿Por qué Firebase Realtime Database?
Permite alojar la base de datos completamente en la nube de Google sin necesidad de administrar servidores VPS, bases de datos relacionales complejas ni túneles de red. Toda la información persiste en la nube y está disponible globalmente.

### Configuración de Conexión
La configuración se centraliza en `.env` y `configs/settings.py`:
- `FIREBASE_DATABASE_URL`: `https://lepetit-e4386-default-rtdb.firebaseio.com`
- `FIREBASE_PROJECT_ID`: `lepetit-e4386`
- `FIREBASE_API_KEY`: `AIzaSyBhrtT0Ld-45e0jcY9hW5Jf0dSdzS4A3Zc`

### Estructura de Datos en Firebase
La base de datos en tiempo real organiza la información bajo los siguientes nodos raíz:
- `/categories`: Objeto JSON con las categorías principales (`id_main_cat`, `nombre`, `descripcion`).
- `/subcategories`: Subcategorías asociadas a cada categoría principal.
- `/brands`: Listado de fabricantes y marcas.
- `/products`: 3,718 productos tecnológicos con campos: `id_producto`, `nombre`, `descripcion`, `precio`, `stock`, `rating`, `reviews_count`, `marca`, `categoria`, `subcategoria`, `image_url`.
- `/users`: Usuarios registrados con contraseñas encriptadas mediante `werkzeug.security` (PBKDF2-SHA256).

### Script de Migración Automatizado
Se creó el script ejecutable:
```bash
python scripts/migrate_to_firebase.py
```
Este script realiza la lectura del dataset CSV (`amazon_tech_products_ecommerceGKALI.csv`), estructura las 10 categorías canónicas, 15 subcategorías, 45 marcas, los 3,718 productos y crea los usuarios iniciales en Firebase.

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
- `GET /registro` y `POST /registro`: Formulario para nuevos clientes, validación de formato de correo y longitud de contraseña, almacenamiento encriptado y sesión automática.
- `GET /logout`: Cierre de sesión y limpieza de contexto.

### Decoradores de Seguridad
- `@login_required`: Restringe el acceso a usuarios autenticados.
- `@admin_required`: Restringe el acceso únicamente a usuarios cuyo rol sea `admin`. Si un cliente intenta acceder, el sistema deniega el acceso y lo devuelve con una alerta.

### Cuentas Iniciales para Pruebas
| Rol | Correo Electrónico | Contraseña |
| :--- | :--- | :--- |
| **Administrador** | `admin@lepetit.com` | `admin123` |
| **Cliente** | `cliente@lepetit.com` | `cliente123` |

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

## 6. Verificación y Ejecución de Pruebas

Para ejecutar la aplicación localmente:
```bash
python app.py
```
La aplicación queda disponible en `http://127.0.0.1:5000`.

Para ejecutar las 24 pruebas unitarias automatizadas:
```bash
python -m unittest discover tests
```
Resultado: **24 pruebas exitosas en ~2.8 segundos (0 fallos, 0 errores)**.

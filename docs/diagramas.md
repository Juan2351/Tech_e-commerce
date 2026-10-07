# Arquitectura y modelo de datos

## Componentes

```mermaid
flowchart LR
    Browser[Frontend HTML CSS JavaScript]
    API[API REST Flask]
    Controllers[Controladores]
    Services[Servicios]
    Models[Modelos y acceso a datos]
    MySQL[(MySQL)]
    SQLite[(SQLite local)]
    CSV[CSV fuente]

    Browser -->|HTTP JSON| API
    API --> Controllers
    Controllers --> Services
    Services --> Models
    Models --> MySQL
    Models -.->|contingencia| SQLite
    CSV -->|inicializacion local| SQLite
```

La API expone rutas bajo `/api/v1`. La capa de servicios valida las operaciones y
la capa de modelos ejecuta consultas parametrizadas. Si MySQL no esta disponible,
la API puede inicializar SQLite a partir del CSV local.

## Modelo relacional

```mermaid
erDiagram
    MARCA ||--o{ PRODUCTO : identifica
    CATEGORIA_PRINCIPAL ||--|{ SUBCATEGORIA : contiene
    SUBCATEGORIA ||--o{ PRODUCTO : clasifica

    MARCA {
        int id_marca PK
        string nombre UK
    }
    CATEGORIA_PRINCIPAL {
        int id_main_cat PK
        string nombre UK
    }
    SUBCATEGORIA {
        int id_subcat PK
        int id_main_cat FK
        string nombre
    }
    PRODUCTO {
        string id_producto PK
        string descripcion
        decimal precio
        decimal rating
        int reviews_count
        int stock
        int id_marca FK
        int id_subcat FK
    }
```

## Flujo de importacion

```mermaid
flowchart LR
    CSV[conjunto_datos CSV] --> ETL[database/import_csv.py]
    Schema[database/schema.sql] --> MySQL[(MySQL)]
    ETL --> MySQL
    MySQL --> API[API REST]
    API --> Frontend[Frontend]
```

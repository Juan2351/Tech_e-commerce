CREATE TABLE IF NOT EXISTS marca (
    id_marca INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS categoria_principal (
    id_main_cat INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS subcategoria (
    id_subcat INTEGER PRIMARY KEY,
    id_main_cat INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    UNIQUE (id_main_cat, nombre),
    FOREIGN KEY (id_main_cat)
        REFERENCES categoria_principal (id_main_cat)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS producto (
    id_producto TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    precio NUMERIC NOT NULL CHECK (precio >= 0),
    rating NUMERIC NOT NULL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
    reviews_count INTEGER NOT NULL DEFAULT 0 CHECK (reviews_count >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    url TEXT,
    image_url TEXT,
    id_marca INTEGER NOT NULL,
    id_subcat INTEGER NOT NULL,
    FOREIGN KEY (id_marca)
        REFERENCES marca (id_marca)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (id_subcat)
        REFERENCES subcategoria (id_subcat)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_producto_categoria
    ON producto (id_subcat);
CREATE INDEX IF NOT EXISTS idx_producto_marca
    ON producto (id_marca);
CREATE INDEX IF NOT EXISTS idx_producto_precio
    ON producto (precio);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL UNIQUE,
    checkout_token TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending_confirmation'
        CHECK (status IN ('pending_confirmation', 'confirmed', 'cancelled')),
    customer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    delivery_address TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    total_cop INTEGER NOT NULL CHECK (total_cop >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cop INTEGER NOT NULL CHECK (unit_price_cop >= 0),
    line_total_cop INTEGER NOT NULL CHECK (line_total_cop >= 0),
    FOREIGN KEY (order_id)
        REFERENCES orders (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_orders_created_at
    ON orders (created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON order_items (order_id);

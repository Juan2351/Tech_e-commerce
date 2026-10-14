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

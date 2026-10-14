CREATE DATABASE IF NOT EXISTS lepetit
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE lepetit;

CREATE TABLE IF NOT EXISTS marca (
    id_marca INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_marca),
    UNIQUE KEY uq_marca_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categoria_principal (
    id_main_cat INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_main_cat),
    UNIQUE KEY uq_categoria_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subcategoria (
    id_subcat INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_main_cat INT UNSIGNED NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_subcat),
    UNIQUE KEY uq_subcategoria_categoria_nombre (id_main_cat, nombre),
    CONSTRAINT fk_subcategoria_categoria
        FOREIGN KEY (id_main_cat)
        REFERENCES categoria_principal (id_main_cat)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producto (
    id_producto VARCHAR(64) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    precio DECIMAL(12, 2) UNSIGNED NOT NULL COMMENT 'Precio base en USD',
    rating DECIMAL(2, 1) UNSIGNED NOT NULL DEFAULT 0.0,
    reviews_count INT UNSIGNED NOT NULL DEFAULT 0,
    stock INT UNSIGNED NOT NULL DEFAULT 0,
    url VARCHAR(2048) NULL COMMENT 'Enlace informativo del producto',
    image_url VARCHAR(2048) NULL,
    id_marca INT UNSIGNED NOT NULL,
    id_subcat INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_producto),
    KEY idx_producto_categoria (id_subcat),
    KEY idx_producto_marca (id_marca),
    KEY idx_producto_precio (precio),
    CONSTRAINT chk_producto_rating CHECK (rating <= 5.0),
    CONSTRAINT fk_producto_marca
        FOREIGN KEY (id_marca)
        REFERENCES marca (id_marca)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_producto_subcategoria
        FOREIGN KEY (id_subcat)
        REFERENCES subcategoria (id_subcat)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

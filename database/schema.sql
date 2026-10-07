-- Base de datos: ecommerce_db
-- Motor: MySQL 8.0+

CREATE DATABASE IF NOT EXISTS ecommerce_db
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE ecommerce_db;

-- 1. Tabla Marca
CREATE TABLE IF NOT EXISTS marca (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 2. Tabla Categoria Principal
CREATE TABLE IF NOT EXISTS categoria_principal (
    id_main_cat INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 3. Tabla Subcategoria
CREATE TABLE IF NOT EXISTS subcategoria (
    id_subcat INT AUTO_INCREMENT PRIMARY KEY,
    id_main_cat INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT fk_subcat_maincat FOREIGN KEY (id_main_cat) 
        REFERENCES categoria_principal(id_main_cat) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT uq_subcat_per_main UNIQUE (id_main_cat, nombre)
) ENGINE=InnoDB;

-- 4. Tabla Producto
CREATE TABLE IF NOT EXISTS producto (
    id_producto VARCHAR(64) PRIMARY KEY,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    reviews_count INT DEFAULT 0,
    stock INT NOT NULL DEFAULT 0,
    url VARCHAR(500),
    image_url VARCHAR(500),
    id_marca INT,
    id_subcat INT,
    CONSTRAINT fk_producto_marca FOREIGN KEY (id_marca) 
        REFERENCES marca(id_marca) 
        ON UPDATE CASCADE 
        ON DELETE SET NULL,
    CONSTRAINT fk_producto_subcat FOREIGN KEY (id_subcat) 
        REFERENCES subcategoria(id_subcat) 
        ON UPDATE CASCADE 
        ON DELETE SET NULL
) ENGINE=InnoDB;

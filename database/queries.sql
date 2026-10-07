-- Validacion e Integridad de Datos y Consultas de Analisis
-- Base de datos: ecommerce_db

USE ecommerce_db;

-- 1. Conteo general de registros por entidad
SELECT
    (SELECT COUNT(*) FROM marca) AS total_marcas,
    (SELECT COUNT(*) FROM categoria_principal) AS total_categorias,
    (SELECT COUNT(*) FROM subcategoria) AS total_subcategorias,
    (SELECT COUNT(*) FROM producto) AS total_productos;

-- 2. Validacion de integridad referencial (no deben existir huerfanos)
SELECT COUNT(*) AS productos_sin_marca
FROM producto
WHERE id_marca IS NULL;

SELECT COUNT(*) AS productos_sin_subcategoria
FROM producto
WHERE id_subcat IS NULL;

-- 3. Top 10 productos mas costosos con marca y categoria
SELECT
    p.id_producto,
    p.descripcion,
    m.nombre AS marca,
    c.nombre AS categoria,
    s.nombre AS subcategoria,
    p.precio,
    p.stock
FROM producto p
INNER JOIN marca m ON p.id_marca = m.id_marca
INNER JOIN subcategoria s ON p.id_subcat = s.id_subcat
INNER JOIN categoria_principal c ON s.id_main_cat = c.id_main_cat
ORDER BY p.precio DESC
LIMIT 10;

-- 4. Top 10 productos mejor valorados (con minimo 100 resenas)
SELECT
    p.id_producto,
    p.descripcion,
    m.nombre AS marca,
    p.rating,
    p.reviews_count,
    p.precio
FROM producto p
INNER JOIN marca m ON p.id_marca = m.id_marca
WHERE p.reviews_count >= 100
ORDER BY p.rating DESC, p.reviews_count DESC
LIMIT 10;

-- 5. Analisis por marca: total de productos, precio promedio y rating medio
SELECT
    m.nombre AS marca,
    COUNT(p.id_producto) AS total_productos,
    ROUND(AVG(p.precio), 2) AS precio_promedio,
    ROUND(AVG(p.rating), 2) AS rating_promedio,
    SUM(p.stock) AS stock_total
FROM marca m
INNER JOIN producto p ON m.id_marca = p.id_marca
GROUP BY m.id_marca, m.nombre
ORDER BY total_productos DESC
LIMIT 15;

-- 6. Distribucion de productos por categoria principal y subcategoria
SELECT
    c.nombre AS categoria_principal,
    s.nombre AS subcategoria,
    COUNT(p.id_producto) AS cantidad_productos,
    ROUND(AVG(p.precio), 2) AS precio_promedio
FROM categoria_principal c
INNER JOIN subcategoria s ON c.id_main_cat = s.id_main_cat
LEFT JOIN producto p ON s.id_subcat = p.id_subcat
GROUP BY c.id_main_cat, c.nombre, s.id_subcat, s.nombre
ORDER BY c.nombre, cantidad_productos DESC;

-- 7. Productos con bajo inventario (alerta de reabastecimiento: stock < 20)
SELECT
    p.id_producto,
    p.descripcion,
    m.nombre AS marca,
    p.stock,
    p.precio
FROM producto p
LEFT JOIN marca m ON p.id_marca = m.id_marca
WHERE p.stock < 20
ORDER BY p.stock ASC
LIMIT 10;

-- 8. Subconsulta: Productos cuyo precio supera el promedio general
SELECT
    p.id_producto,
    p.descripcion,
    p.precio,
    (SELECT ROUND(AVG(precio), 2) FROM producto) AS precio_promedio_general
FROM producto p
WHERE p.precio > (SELECT AVG(precio) FROM producto)
ORDER BY p.precio DESC
LIMIT 10;

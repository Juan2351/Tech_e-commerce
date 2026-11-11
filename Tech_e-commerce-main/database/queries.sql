-- Catálogo con marca, subcategoría y categoría principal.
SELECT p.id_producto, p.nombre, p.precio, p.stock, p.rating,
       m.nombre AS marca, s.nombre AS subcategoria,
       c.nombre AS categoria
FROM producto AS p
JOIN marca AS m ON m.id_marca = p.id_marca
JOIN subcategoria AS s ON s.id_subcat = p.id_subcat
JOIN categoria_principal AS c ON c.id_main_cat = s.id_main_cat
ORDER BY p.nombre;

-- Buscar por categoría y disponibilidad.
SELECT p.id_producto, p.nombre, p.precio, p.stock
FROM producto AS p
JOIN subcategoria AS s ON s.id_subcat = p.id_subcat
WHERE s.id_main_cat = 1 AND p.stock > 0
ORDER BY p.precio;

-- Comprobar productos sin marca o subcategoría válida.
SELECT p.id_producto
FROM producto AS p
LEFT JOIN marca AS m ON m.id_marca = p.id_marca
LEFT JOIN subcategoria AS s ON s.id_subcat = p.id_subcat
WHERE m.id_marca IS NULL OR s.id_subcat IS NULL;

-- Conteo de productos agrupado por categoría.
SELECT c.nombre, COUNT(p.id_producto) AS total_productos
FROM categoria_principal AS c
LEFT JOIN subcategoria AS s ON s.id_main_cat = c.id_main_cat
LEFT JOIN producto AS p ON p.id_subcat = s.id_subcat
GROUP BY c.id_main_cat, c.nombre
ORDER BY c.nombre;

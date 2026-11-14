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

-- Autenticación básica: buscar usuario por email o nombre de usuario.
SELECT id, nombre_usuario, email, password_hash, rol,
       telefono, direccion_entrega, created_at
FROM usuarios
WHERE lower(email) = lower(?) OR lower(nombre_usuario) = lower(?);

-- Listar usuarios por rol (por ejemplo, clientes VIP para descuentos preferenciales).
SELECT id, nombre_usuario, email, rol, telefono, direccion_entrega, created_at
FROM usuarios
WHERE rol = 'vip'
ORDER BY created_at DESC;

-- Catálogo con proyección de precio preferencial para usuarios con rol 'vip' (10% de descuento).
SELECT p.id_producto, p.nombre, p.precio AS precio_regular,
       ROUND(p.precio * 0.90, 2) AS precio_vip,
       p.stock
FROM producto AS p
WHERE p.stock > 0
ORDER BY p.nombre;

-- Consultar pedidos junto con la información del usuario registrado (o invitado si user_id es NULL).
SELECT o.id, o.order_number, o.status, o.total_cop, o.created_at,
       o.user_id, u.nombre_usuario, COALESCE(u.rol, 'invitado') AS rol_comprador,
       o.customer_name, o.phone, o.email, o.delivery_address
FROM orders AS o
LEFT JOIN usuarios AS u ON u.id = o.user_id
ORDER BY o.created_at DESC;

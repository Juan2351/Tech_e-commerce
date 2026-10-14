USE lepetit;

INSERT IGNORE INTO marca (id_marca, nombre) VALUES
    (1, 'LePetit'),
    (2, 'Natura'),
    (3, 'Urban'),
    (4, 'AeroFit'),
    (5, 'Luna');

INSERT IGNORE INTO categoria_principal (id_main_cat, nombre) VALUES
    (1, 'Mujer'),
    (2, 'Hombre'),
    (3, 'Accesorios');

INSERT IGNORE INTO subcategoria (id_subcat, id_main_cat, nombre) VALUES
    (1, 1, 'Ropa casual'),
    (2, 1, 'Bolsos'),
    (3, 2, 'Ropa deportiva'),
    (4, 2, 'Calzado'),
    (5, 3, 'Joyería'),
    (6, 3, 'Tecnología');

INSERT IGNORE INTO producto
    (id_producto, nombre, descripcion, precio, rating, reviews_count, stock, url, image_url, id_marca, id_subcat)
VALUES
    ('LP-001', 'Chaqueta ligera LePetit', 'Chaqueta de uso diario con diseño sobrio y cómodo.', 79.99, 4.8, 128, 18, NULL, 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80', 1, 1),
    ('LP-002', 'Bolso de tela', 'Bolso funcional con compartimentos para el día a día.', 64.50, 4.6, 91, 12, NULL, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80', 2, 2),
    ('LP-003', 'Conjunto deportivo', 'Prendas de entrenamiento con tejido transpirable.', 89.00, 4.7, 110, 9, NULL, 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80', 4, 3),
    ('LP-004', 'Zapatillas urbanas', 'Calzado de suela flexible para caminar todo el día.', 92.30, 4.5, 77, 15, NULL, 'https://images.unsplash.com/photo-1543508282-6319a3e2621f?auto=format&fit=crop&w=900&q=80', 3, 4),
    ('LP-005', 'Collar minimalista', 'Accesorio sencillo para combinar con cualquier estilo.', 29.99, 4.9, 211, 34, NULL, 'https://images.unsplash.com/photo-1617038220319-276d3cfab638?auto=format&fit=crop&w=900&q=80', 5, 5),
    ('LP-006', 'Auriculares Bluetooth', 'Auriculares inalámbricos con batería de larga duración.', 119.99, 4.8, 143, 10, NULL, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80', 1, 6);

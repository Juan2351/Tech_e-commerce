INSERT OR IGNORE INTO categoria_principal (id_main_cat, nombre) VALUES
    (1, 'Smartphones'),
    (2, 'Mini PCs & Desktops'),
    (3, 'Mice & Keyboards'),
    (4, 'Laptops & Notebooks'),
    (5, 'Audio & Headphones'),
    (6, 'Monitors & Displays'),
    (7, 'Tablets & E-Readers'),
    (8, 'Smartwatches & Wearables'),
    (9, 'Storage & Networking'),
    (10, 'Accessories & Hubs');

INSERT OR IGNORE INTO subcategoria (id_subcat, id_main_cat, nombre) VALUES
    (1, 1, 'Android Smartphones'),
    (2, 1, 'iPhones (Apple)'),
    (3, 2, 'Desktop PCs & All-in-Ones'),
    (4, 2, 'Mini PCs'),
    (5, 3, 'Computer Mice'),
    (6, 3, 'Keyboards'),
    (7, 4, 'Business Laptops'),
    (8, 4, 'Gaming Laptops'),
    (9, 4, 'General Laptops'),
    (10, 5, 'Earbuds & Headphones'),
    (11, 6, 'Monitors'),
    (12, 7, 'Tablets & E-Ink'),
    (13, 8, 'Smartwatches'),
    (14, 9, 'SSD & Networking'),
    (15, 10, 'Power & Docks');

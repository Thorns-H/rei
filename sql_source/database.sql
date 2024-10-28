CREATE TABLE users (
    user_id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(255) NOT NULL DEFAULT 'default_user.jpg',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE notes (
    note_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    title VARCHAR(30) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remove_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)  
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE products (
    product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(255) NOT NULL DEFAULT 'default_product.jpg',
    category ENUM('Celular', 'Accesorio', 'Chip', 'Otro') NOT NULL,
    description TEXT,
    price FLOAT(10,2) NOT NULL,
    stock INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE repair_parts (
    repair_part_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(255) NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    price FLOAT(10,2) NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE repair_orders (
    repair_order_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    repair_part_id INT UNSIGNED DEFAULT NULL,
    client_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP DEFAULT NULL,
    model VARCHAR(255) NOT NULL,
    service VARCHAR(255) NOT NULL,
    observations TEXT,
    cost FLOAT(10,2) NOT NULL,
    investment FLOAT(10,2) NOT NULL DEFAULT 0.0,
    status ENUM('Cancelado', 'Pendiente', 'Entregado') NOT NULL DEFAULT 'Pendiente',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (repair_part_id) REFERENCES repair_parts(repair_part_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE sale_orders (
    sale_order_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    status ENUM('Cancelado', 'Finalizado') NOT NULL DEFAULT 'Finalizado'
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE sale_order_products (
    sale_order_product_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sale_order_id INT UNSIGNED NOT NULL,
    product_id INT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    FOREIGN KEY (sale_order_id) REFERENCES sale_orders(sale_order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE order_media(
    media_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    repair_order_id INT UNSIGNED NOT NULL,
    directory VARCHAR(255) NOT NULL,
    FOREIGN KEY (repair_order_id) REFERENCES repair_orders(repair_order_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

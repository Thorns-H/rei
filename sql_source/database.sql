CREATE TABLE Producto (
    ID INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Proveedor VARCHAR(255) NOT NULL,
    Precio FLOAT(10,2) NOT NULL
);

CREATE TABLE Orden_Productos (
    ID INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Fecha_Emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    Fecha_Entrega TIMESTAMP DEFAULT NULL,
    Servicio TEXT NOT NULL,
    Notas TEXT,
    Costo FLOAT(10,2) NOT NULL,
    Estatus ENUM('Cancelado', 'Pendiente', 'Entregado') NOT NULL DEFAULT 'Pendiente'
);
"""
    Este archivo define las funciones relacionadas a las instancias de la base de datos,
    es importante que al usar este módulo, recuerden cerrar cada instancia hecha del mismo.
"""

import pymysql
import os
from dotenv import load_dotenv

def get_connection() -> pymysql.connections.Connection:

    load_dotenv()

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_port = int(os.getenv("DB_PORT"))

    return pymysql.connect(host = db_host, user = db_user, password = db_password, db = db_name, port = db_port)

class product:
    def __init__(self, data: tuple) -> None:
        self.id = data[0]
        self.name = data[1]
        self.supplier = data[2]
        self.price = data[3]

    def to_dict(self) -> None:
        return {
            'id': self.id,
            'name': self.name,
            'supplier': self.supplier,
            'price': self.price
        }
    
def convert_set(table: tuple, type: str) -> tuple:

    items: list = []

    for item in table:
        if type == 'product':
            items.append(product(item).to_dict())
        elif type == 'order':
            items.append(order(item).to_dict())
        elif type == 'order_photo':
            items.append(order_photo(item).to_dict())
        
    return tuple(items)

def get_products_by_name(keywords: list) -> tuple:
    try:
        connection = get_connection()

        if not keywords:
            return ()

        query = "SELECT * FROM Producto WHERE "
        conditions = [f"Nombre LIKE '%{keyword}%'" for keyword in keywords]
        query += " AND ".join(conditions)

        with connection.cursor() as cursor:
            cursor.execute(query)
            products = cursor.fetchall()

        connection.close()

        return convert_set(products, 'product')
    except Exception as e:
        return False
    
class order:
    def __init__(self, data: tuple = None) -> None:
        self.id = data[0]
        self.customer_name = data[1]
        self.issue_date = data[2]
        self.delivery_date = data[3]
        self.service = data[4]
        self.notes = data[5]
        self.cost = data[6]
        self.status = data[7]
        self.investment = data[8]

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'issue_date': self.issue_date,
            'delivery_date': self.delivery_date,
            'service': self.service,
            'notes': self.notes,
            'cost': self.cost,
            'status': self.status,
            'investment': self.investment
        }

def new_order(name: str, service: str, notes: str, cost: float, invest: float) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO orden_productos(Nombre, Servicio, Notas, Costo, Inversion) VALUES (%s, %s, %s, %s, %s)", (name, service, notes, cost, invest))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'new_order'")
        return False
    
def get_order(order_id: int) -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orden_productos WHERE ID = %s", (order_id,))
            order_result = cursor.fetchone()

        connection.close()

        return order(order_result).to_dict()
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_order'")
        return False
    
def update_order(name: str, service: str, notes: str, cost: float, investment: float, order_id: int) ->  bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE orden_productos SET Nombre = %s, Servicio = %s, Notas = %s, Costo = %s, Inversion = %s WHERE ID = %s", (name, service, notes, cost, investment, order_id))

        connection.commit()
        connection.close()

        return True

    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'update_order'")
        return False
    
def get_all_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orden_productos ORDER BY Fecha_Emision DESC")
            orders = cursor.fetchall()

        connection.close()

        return convert_set(orders, 'order')
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_orders'")
    
def get_unfinished_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orden_productos WHERE Estatus = 'Pendiente' ORDER BY Fecha_Emision DESC")
            orders = cursor.fetchall()

        connection.close()

        return convert_set(orders, 'order')
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_orders'")

def delete_order(order_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM orden_productos WHERE ID = %s", (order_id,))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'delete_order'")
        return False
    
class order_photo:
    def __init__(self, data: tuple) -> None:
        self.id = data[0]
        self.order_id = data[1]
        self.directory = data[2]

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'directory': self.directory
        }

def new_order_photo(order_id: int, directory: str) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Orden_Foto (ID_Orden, Directorio)VALUES (%s, %s)", (order_id, directory))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'new_order'")
        return False
    
def delete_order_photo(id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT Directorio FROM Orden_Foto WHERE ID = %s", (id,))
            result = cursor.fetchone()

            if result:
                photo_path = result[0]
                full_path = os.path.join('static', photo_path)
                full_path = os.path.abspath(full_path)
                
                if os.path.exists(full_path) and os.access(full_path, os.W_OK):
                    os.remove(full_path)

                cursor.execute("DELETE FROM Orden_Foto WHERE ID = %s", (id,))
        
        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'delete_order_photo'")
        return False
    
def get_order_photos(id_orden: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM orden_foto WHERE ID_Orden = '{id_orden}' ORDER BY ID DESC")
            order_photos = cursor.fetchall()

        connection.close()

        return convert_set(order_photos, 'order_photo')
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_order_photos'")
    
def get_user(username: str) -> str:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM usuario WHERE Nombre_Usuario = '{username}'")
            user = cursor.fetchone()

        connection.close()

        return user
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_user'")

"""
    Este apartado contiene funciones de prueba para generar usuarios en la base de datos,
    en teoria no deberia ser llamada jamás en app.py, recomiendo crear otro archivo .py
    incluir estas funciones y correrlas ahí.
"""

import hashlib

def new_user(username: str, password: str, name: str) -> str:
    try:
        connection = get_connection()

        password = hashlib.md5(password.encode()).hexdigest()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Usuario(Nombre_Usuario, Contraseña, Nombre, Foto) VALUES (%s, %s, %s, %s)", (username, password, name, 'images/default_user.jpg'))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'new_user', this function is only for testing.")
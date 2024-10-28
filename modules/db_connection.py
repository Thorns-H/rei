"""
    Este archivo define las funciones relacionadas a las instancias de la base de datos,
    es importante que al usar este módulo, recuerden cerrar cada instancia hecha del mismo.
"""

import pymysql
import os
from dotenv import load_dotenv

RED = "\033[91m"
RESTORE = "\033[0m"

def get_connection() -> pymysql.connections.Connection:

    load_dotenv(override = True)

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_port = int(os.getenv("DB_PORT"))

    return pymysql.connect(host = db_host, user = db_user, password = db_password, db = db_name, port = db_port, ssl = None)

class repair_part:
    def __init__(self, data: tuple) -> None:
        self.repair_part_id = data[0]
        self.model = data[1]
        self.supplier = data[2]
        self.price = data[3]

    def to_dict(self) -> None:
        return {
            'repair_part_id': self.repair_part_id,
            'model': self.model,
            'supplier': self.supplier,
            'price': self.price
        }
    
def convert_set(table: tuple, type: str) -> tuple:

    items: list = []

    for item in table:
        if type == 'repair_part':
            items.append(repair_part(item).to_dict())
        elif type == 'repair_order':
            items.append(repair_order(item).to_dict())
        elif type == 'order_media':
            items.append(order_media(item).to_dict())
        
    return tuple(items)

def get_parts_by_name(keywords: list) -> tuple:
    
    try:
        connection = get_connection()

        if not keywords:
            return ()

        query = "SELECT * FROM repair_parts WHERE "
        conditions = [f"model LIKE '%{keyword}%'" for keyword in keywords]
        query += " AND ".join(conditions)

        with connection.cursor() as cursor:
            cursor.execute(query)
            parts = cursor.fetchall()

        connection.close()

        return convert_set(parts, 'repair_part')

    except Exception as e:
        print(f"Error ({e}) at modules/db_connection at func get_parts_by_name")
        return False
    
class repair_order:
    def __init__(self, data: tuple = None) -> None:
        self.repair_order_id = data[0]
        self.user_id = data[1]
        self.repair_part_id = data[2]
        self.client_name = data[3]
        self.created_at = data[4]
        self.delivered_at = data[5]
        self.model = data[6]
        self.service = data[7]
        self.observations = data[8]
        self.cost = data[9]
        self.investment = data[10]
        self.status = data[11]

    def to_dict(self) -> dict:
        return {
            'repair_order_id': self.repair_order_id,
            'user_id': self.user_id,
            'client_name': self.client_name,
            'created_at': self.created_at,
            'delivered_at': self.delivered_at,
            'model': self.model,
            'service': self.service,
            'observations': self.observations,
            'cost': self.cost,
            'investment': self.investment,
            'status': self.status
        }

def new_repair_order(client_name: str, user_id: str, model: str, service: str, observations: str, cost: float, investment: float) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO repair_orders(client_name, user_id, model, service, observations, cost, investment) VALUES (%s, %s, %s, %s, %s, %s, %s)", (client_name, user_id, model, service, observations, cost, investment))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"{RED}Error ({e}) at modules/db_connection func 'new_repair_order'{RESTORE}")
        return False
    
def get_repair_order(order_id: int) -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            order_result = cursor.fetchone()

        connection.close()

        return repair_order(order_result).to_dict()
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_order'")
        return False
    
def update_repair_order(client_name: str, model: str, service: str, observations: str, cost: float, investment: float, repair_order_id: int) ->  bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE repair_orders SET client_name = %s, model = %s, service = %s, observations = %s, cost = %s, investment = %s WHERE repair_order_id = %s", (client_name, model, service, observations, cost, investment, repair_order_id))

        connection.commit()
        connection.close()

        return True

    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'update_repair_order'")
        return False
    
def get_all_repair_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM repair_orders ORDER BY created_at DESC")
            orders = cursor.fetchall()

        connection.close()

        return convert_set(orders, 'repair_order')
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_all_repair_orders'")
    
def get_unfinished_repair_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM repair_orders WHERE status = 'Pendiente' ORDER BY created_at DESC")
            orders = cursor.fetchall()

        connection.close()

        return convert_set(orders, 'repair_order')
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_unfinished_repair_orders'")

def delete_repair_order(repair_order_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM repair_orders WHERE repair_order_id = %s", (repair_order_id,))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'delete_repair_order'")
        return False
    
class order_media:
    def __init__(self, data: tuple) -> None:
        self.media_id = data[0]
        self.order_id = data[1]
        self.directory = data[2]

    def to_dict(self) -> dict:
        return {
            'media_id': self.id,
            'order_id': self.order_id,
            'directory': self.directory
        }

def new_order_media(order_id: int, directory: str) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO order_media (order_id, directory)VALUES (%s, %s)", (order_id, directory))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'new_order_media'")
        return False
    
def delete_order_media(media_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT directory FROM order_media WHERE media_id = %s", (media_id,))
            result = cursor.fetchone()

            if result:
                photo_path = result[0]
                full_path = os.path.join('static', photo_path)
                full_path = os.path.abspath(full_path)
                
                if os.path.exists(full_path) and os.access(full_path, os.W_OK):
                    os.remove(full_path)

                cursor.execute("DELETE FROM order_media WHERE media_id = %s", (media_id,))
        
        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'delete_order_media'")
        return False
    
def get_order_media(media_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM order_media WHERE media_id = '{media_id}' ORDER BY media_id DESC")
            order_photos = cursor.fetchall()

        connection.close()

        return convert_set(order_photos, 'order_media')
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'get_order_media'")
    
def get_user(email: str) -> str:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
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
"""
    Este archivo define las funciones relacionadas a las instancias de la base de datos,
    es importante que al usar este módulo, recuerden cerrar cada instancia hecha del mismo.
"""

import pymysql
import os
import sys
from dotenv import load_dotenv

from modules.db_objects import product, repair_part, repair_order, order_media

RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Helpers para el resto de funciones en el código.

def get_connection() -> pymysql.connections.Connection:

    load_dotenv(override = True)

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_port = int(os.getenv("DB_PORT"))

    return pymysql.connect(host = db_host, user = db_user, password = db_password, db = db_name, port = db_port, ssl = None)
    
def convert_set(table: tuple, type: str) -> tuple:

    items: list = []

    for item in table:
        if type == 'repair_part':
            items.append(repair_part(item).to_dict())
        elif type == 'repair_order':
            items.append(repair_order(item).to_dict())
        elif type == 'order_media':
            items.append(order_media(item).to_dict())
        elif type == 'product':
            items.append(product(item).to_dict())
        
    return tuple(items)

# Relacionado con la entidad 'notes'

# TODO

# Relacionado a la entidad 'users'

def get_user(email: str) -> str:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
            user = cursor.fetchone()

        connection.close()

        return user
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_user'")
        sys.exit(1)

# Relacionado a la entidad 'sale_orders'

# TODO

# Relacionado a la entidad 'sale_order_products'

# TODO

# Relacionado a la entidad 'repair_orders'

def new_repair_order(client_name: str, user_id: str, model: str, service: str, observations: str, cost: float, investment: float) -> None:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO repair_orders(client_name, user_id, model, service, observations, cost, investment) VALUES (%s, %s, %s, %s, %s, %s, %s)", (client_name, user_id, model, service, observations, cost, investment))

        connection.commit()
        connection.close()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'new_repair_order'")
        sys.exit(1)

def get_repair_order(order_id: int) -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM repair_orders WHERE repair_order_id = %s", (order_id,))
            order_result = cursor.fetchone()

        connection.close()

        return repair_order(order_result).to_dict()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_order'")
        sys.exit(1)
    
def update_repair_order(client_name: str, model: str, service: str, observations: str, cost: float, investment: float, repair_order_id: int) ->  bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE repair_orders SET client_name = %s, model = %s, service = %s, observations = %s, cost = %s, investment = %s WHERE repair_order_id = %s", (client_name, model, service, observations, cost, investment, repair_order_id))

        connection.commit()
        connection.close()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'update_repair_order'")
        sys.exit(1)
    
def get_all_repair_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM repair_orders ORDER BY created_at DESC")
            orders = cursor.fetchall()

        connection.close()

        return convert_set(orders, 'repair_order')
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_all_repair_orders'")
        sys.exit(1)
    
def get_unfinished_repair_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM repair_orders WHERE status = 'Pendiente' ORDER BY created_at DESC")
            orders = cursor.fetchall()

        connection.close()

        return convert_set(orders, 'repair_order')
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_unfinished_repair_orders'")
        sys.exit(1)

def validate_repair_order(repair_order_id) -> None:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE repair_orders SET status = 'Entregado', delivered_at = NOW() WHERE repair_order_id = %s", (repair_order_id,))

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'validate_repair_order'")
        sys.exit(1)

def delete_repair_order(repair_order_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM repair_orders WHERE repair_order_id = %s", (repair_order_id,))

        connection.commit()
        connection.close()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'delete_repair_order'")
        sys.exit(1)

# Relacionado a la entidad 'order_media'

def new_order_media(order_id: int, directory: str) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO order_media (repair_order_id, directory)VALUES (%s, %s)", (order_id, directory))

        connection.commit()
        connection.close()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'new_order_media'")
        sys.exit(1)
    
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

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'delete_order_media'")
        sys.exit(1)
    
def get_order_media(repair_order_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM order_media WHERE repair_order_id = '{repair_order_id}' ORDER BY repair_order_id DESC")
            order_photos = cursor.fetchall()

        connection.close()

        return convert_set(order_photos, 'order_media')
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_order_media'")
        sys.exit(1)

# Relacionado a la entidad 'products'
    
def get_products() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

        connection.close()

        return convert_set(products, 'product')
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_products'")
        sys.exit(1)

# Relacionado a la entidad 'repair_parts'

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
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection at func get_parts_by_name")
        sys.exit(1)
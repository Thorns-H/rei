"""
    Este archivo define las funciones relacionadas a las instancias de la base de datos,
    es importante que al usar este módulo, recuerden cerrar cada instancia hecha del mismo.
"""

import pymysql
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

from modules.db_objects import product, repair_part, repair_order, order_media, note

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
        elif type == 'note':
            items.append(note(item).to_dict())
        
    return tuple(items)

# Relacionado con la entidad 'notes'

def new_note(user_id: int, title: str, content: str, created_at: str, remove_at: str) -> None:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO notes(user_id, title, content, created_at, remove_at) VALUES (%s, %s, %s, %s, %s)", (user_id, title, content, created_at, remove_at))

        connection.commit()
        connection.close()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'new_note'")
        sys.exit(1)

def get_notes() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            query = """
                SELECT 
                    notes.note_id, 
                    notes.user_id, 
                    notes.title, 
                    notes.content, 
                    notes.created_at, 
                    notes.remove_at, 
                    users.name, 
                    users.profile_picture
                FROM notes
                INNER JOIN users ON notes.user_id = users.user_id
                ORDER BY notes.created_at DESC
            """
            cursor.execute(query)
            notes = cursor.fetchall()

        connection.close()
        return convert_set(notes, 'note')
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_notes'")
        sys.exit(1)

def get_note_by_id(note_id: int) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    notes.note_id, 
                    notes.user_id, 
                    notes.title, 
                    notes.content, 
                    notes.created_at, 
                    notes.remove_at, 
                    users.name, 
                    users.profile_picture
                FROM notes
                INNER JOIN users ON notes.user_id = users.user_id
                WHERE notes.note_id = %s
            """
            cursor.execute(query, (note_id,))
            note_data = cursor.fetchone()
        connection.close()
        
        if note_data:
            return {
                'note_id': note_data[0],
                'user_id': note_data[1],
                'title': note_data[2],
                'content': note_data[3],
                'created_at': note_data[4],
                'remove_at': note_data[5],
                'user_name': note_data[6],
                'user_profile_picture': note_data[7]
            }
        return None

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_note_by_id'")
        sys.exit(1)

def remove_note(note_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE note_id = %s", (note_id,))

        connection.commit()
        connection.close()

    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'remove_note'")
        sys.exit(1)

def update_note(note_id: int, title: str, content: str, remove_at: str) -> None:
    try:
        connection = get_connection()
        if not remove_at:
            remove_at = None
        
        with connection.cursor() as cursor:
            cursor.execute("UPDATE notes SET title = %s, content = %s, remove_at = %s WHERE note_id = %s", 
                           (title, content, remove_at, note_id))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'update_note'")
        sys.exit(1)

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

def new_repair_order(client_name: str, user_id: str, model: str, service: str, observations: str, repair_details: str, post_details: str, cost: float, investment: float) -> None:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO repair_orders(client_name, user_id, model, service, observations, repair_details, post_details, cost, investment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (client_name, user_id, model, service, observations, repair_details, post_details, cost, investment))

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
    
def update_repair_order(client_name: str, model: str, service: str, observations: str, repair_details: str, post_details: str, cost: float, investment: float, repair_order_id: int) ->  bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE repair_orders SET client_name = %s, model = %s, service = %s, observations = %s, repair_details = %s, post_details = %s, cost = %s, investment = %s WHERE repair_order_id = %s", (client_name, model, service, observations, repair_details, post_details, cost, investment, repair_order_id))

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

import os

def delete_repair_order(repair_order_id: int) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT directory FROM order_media WHERE repair_order_id = %s", (repair_order_id,))
            photos = cursor.fetchall()

            for photo in photos:
                file_path = os.path.join('static', photo[0])
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Archivo eliminado: {file_path}")
                else:
                    print(f"{YELLOW}Advertencia:{RESET} No se encontró el archivo {file_path}")

            cursor.execute("DELETE FROM order_media WHERE repair_order_id = %s", (repair_order_id,))
            cursor.execute("DELETE FROM repair_orders WHERE repair_order_id = %s", (repair_order_id,))

        connection.commit()
        connection.close()

    except Exception as e:
        # Manejar errores y mostrar mensaje de error
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


def new_product(name: str, image: str, category: str, description: str, price: float, stock: int) -> None:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
                INSERT INTO products (name, image, category, description, price, stock) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, image, category, description, price, stock))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'new_product'")
        sys.exit(1)

def get_product_by_id(product_id: int) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product_data = cursor.fetchone()
        connection.close()
        
        if product_data:

            return {
                'product_id': product_data[0],
                'name': product_data[1],
                'image': product_data[2],
                'category': product_data[3],
                'description': product_data[4],
                'price': product_data[5],
                'stock': product_data[6],
                'created_at': product_data[7] 
            }
        return None
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'get_product_by_id'")
        sys.exit(1)

def update_product(product_id: int, name: str, category: str, description: str, price: float, stock: int, image: str = None) -> None:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            if image:
                
                query = """
                    UPDATE products SET name=%s, category=%s, description=%s, price=%s, stock=%s, image=%s 
                    WHERE product_id=%s
                """
                cursor.execute(query, (name, category, description, price, stock, image, product_id))
            else:
                
                query = """
                    UPDATE products SET name=%s, category=%s, description=%s, price=%s, stock=%s 
                    WHERE product_id=%s
                """
                cursor.execute(query, (name, category, description, price, stock, product_id))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'update_product'")
        sys.exit(1)

def delete_product(product_id: int) -> None:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT image FROM products WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()
            if result:
                image_name = result[0]
                
                if image_name != 'default_product.jpg':
                    file_path = os.path.join('static', 'images', image_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'delete_product'")
        sys.exit(1)

def sell_product(product_id: int, user_id: int) -> bool:
    """
    Vende un producto: baja el stock en 1 y crea un registro de venta
    en 'repair_orders' para que cuente en las ganancias.
    Devuelve True si la venta fue exitosa, False si no hay stock.
    """
    connection = get_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
           
            connection.begin()
            
          
            cursor.execute("SELECT name, price, stock FROM products WHERE product_id = %s FOR UPDATE", (product_id,))
            product = cursor.fetchone()
            
            if not product or product['stock'] <= 0:
               
                connection.rollback()
                return False
                
           
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE product_id = %s", (product_id,))
            

            query_order = """
                INSERT INTO repair_orders 
                (user_id, client_name, model, service, cost, investment, status, delivered_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_order, (
                user_id,
                'Venta de Producto',    
                product['name'],        
                'Venta',                
                product['price'],      
                0.00,                   
                'Entregado',            
                datetime.now()          
            ))
            
           
            connection.commit()
            return True
            
    except Exception as e:
        print(f"{RED}Error:{RESET} {YELLOW}'{e}'{RESET} at modules/db_connection func 'sell_product'")
        connection.rollback() 
        return False
    finally:
        connection.close()

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
"""
    Este archivo define las funciones relacionadas a las instancias de la base de datos,
    es importante que al usar este módulo, recuerden cerrar cada instancia hecha del mismo.
"""

import pymysql
import os
from dotenv import load_dotenv

def get_connection() -> pymysql.connections.Connection:

    load_dotenv()

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_port = int(os.getenv("DB_PORT"))

    return pymysql.connect(host = 'localhost', user = db_user, password = db_password, db = db_name, port = db_port)

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

        return products
    except Exception as e:
        return False

def new_order(name: str, service: str, notes: str, cost: float) -> bool:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO orden_productos(Nombre, Servicio, Notas, Costo) VALUES (%s, %s, %s, %s)", (name, service, notes, cost))

        connection.commit()
        connection.close()

        return True
    except Exception as e:
        print(f"Error ({e}) at modules/db_connection func 'new_order'")
        return False
    
def get_unfinished_orders() -> tuple:
    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orden_productos WHERE Estatus = 'Pendiente'")
            orders = cursor.fetchall()

        connection.close()

        return orders
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
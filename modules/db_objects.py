"""
    Este archivo contiene todos los objetos utilizados para la base de datos, usamos un método 
    que vuelve los objetos diccionarios debido a que jinja2 en flask le da mejor legibilidad al 
    momento de cargar la información en los templates.
"""

# La clase note, es la relacionada a la entidad 'notes'.

class note:
    def __init__(self, data: tuple) -> None:
        self.note_id = data[0]
        self.user_id = data[1]
        self.title = data[2]
        self.content = data[3]
        self.created_at = data[4]
        self.remove_at = data[5]
        self.user_name = data[6]
        self.user_profile_picture = data[7]

    def to_dict(self) -> dict:
        return {
            'note_id': self.note_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'remove_at': self.remove_at,
            'user_name': self.user_name,
            'user_profile_picture': self.user_profile_picture
        }

# La clase product, es la relacionada la entidad 'products', relacionado al inventario.

class product:
    def __init__(self, data: tuple) -> None:
        self.product_id = data[0]
        self.name = data[1]
        self.image = data[2]
        self.category = data[3]
        self.description = data[4]
        self.price = data[5]
        self.stock = data[6]
        self.created_at = data[7]

    def to_dict(self) -> dict:
        return {
            'product_id': self.product_id,
            'name': self.name,
            'image': self.image,
            'category': self.category,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'created_at': self.created_at
        }

# La clase repair_part es la relacionada a la entidad 'repair_parts' relacionado a las refacciones de celulares.

class repair_part:
    def __init__(self, data: tuple) -> None:
        self.repair_part_id = data[0]
        self.model = data[1]
        self.supplier = data[2]
        self.price = data[3]

    def to_dict(self) -> dict:
        return {
            'repair_part_id': self.repair_part_id,
            'model': self.model,
            'supplier': self.supplier,
            'price': self.price
        }

# La clase repair_order es la relacionada a la entiedad 'repair_orders', que vincula las ordenes de REPARACIÓN únicamente.

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

# La clase order_media es la relacionada a la entidad 'order_media' que controla las fotos o videos de las reparaciones en las ordenes.

class order_media:
    def __init__(self, data: tuple) -> None:
        self.media_id = data[0]
        self.media_id = data[0]
        self.order_id = data[1]
        self.directory = data[2]

    def to_dict(self) -> dict:
        return {
            'media_id': self.media_id,
            'order_id': self.order_id,
            'directory': self.directory
        }
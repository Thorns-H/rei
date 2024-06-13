"""
    Este es el archivo principal de la aplicación, recuerden no compartir datos sensibles
    en este apartado, recomiendo usar .env en todo momento.
"""

from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import requests
import os

from modules.db_connection import get_connection, get_products_by_name, new_order, get_all_orders, delete_order

if __name__ == '__main__':

    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    """
        El parámetro de host en 0.0.0.0 hará que puedan ver el render de las rutas de la
        página desde la ip de su máquina, pueden probarlo con su celular u otra máquina
        siempre que esten conectados en la misma red.

        También recuersen hacerlo usando https y no http.

        Ejemplo: https://192.168.100.10:5000

        Si quieren cambiar el protocolo de https a http, solo quiten ssl_context como parámetro.
    """

    @app.route('/')
    def index() -> str:
        return render_template('index.html')

    @app.route('/marcas')
    def brands() -> str:
        search_query = request.args.get('search', '').lower()
        response = requests.get('http://phone-specs-api-2.azharimm.dev/brands')
        data = response.json()
        brands = data['data'] if data['status'] else []

        if search_query:
            brands = [brand for brand in brands if search_query in brand['brand_name'].lower()]

        return render_template('brands.html', brands=brands)
    
    @app.route('/cotizacion', methods=['GET', 'POST'])
    def price_request():

        if request.method == 'POST':
            search_text = request.form.get('search', '').strip()
            keywords = search_text.split()
        else:
            keywords = []

        products = get_products_by_name(keywords)

        return render_template('products.html', products=products, search_text='')

    @app.route('/marcas/<brand_slug>')
    def information(brand_slug) -> str:
        search_query = request.args.get('search', '').lower()
        page = request.args.get('page', 1, type=int)

        all_phones = []
        response = requests.get(f'http://phone-specs-api-2.azharimm.dev/brands/{brand_slug}')
        data = response.json()
        
        if data['status']:
            title = data['data']['title']
            current_page = data['data']['current_page']
            last_page = data['data']['last_page']

            for page_num in range(1, last_page + 1):
                response = requests.get(f'http://phone-specs-api-2.azharimm.dev/brands/{brand_slug}?page={page_num}')
                page_data = response.json()
                if page_data['status']:
                    all_phones.extend(page_data['data']['phones'])

        if search_query:
            all_phones = [phone for phone in all_phones if search_query in phone['phone_name'].lower()]

        phones_per_page = 20
        start = (page - 1) * phones_per_page
        end = start + phones_per_page
        paginated_phones = all_phones[start:end]

        return render_template('phones.html', title=title, brand_slug=brand_slug, phones=paginated_phones, current_page=page, last_page=(len(all_phones) // phones_per_page) + 1, search_query=search_query)
    
    @app.route('/ordenes', methods=['GET', 'POST'])
    def orders():
        if request.method == 'POST':
            name = request.form.get('name')
            service = request.form.get('service')
            notes = request.form.get('notes', '')
            cost = float(request.form.get('cost'))
            new_order(name, service, notes, cost)
            return redirect(url_for('orders'))

        orders = get_all_orders()
        return render_template('orders.html', orders=orders)
    
    @app.route('/ordenes/validar/<int:order_id>', methods=['POST'])
    def validate_order(order_id):
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE orden_productos SET Estatus = 'Entregado' WHERE ID = %s", (order_id,))

        connection.commit()
        connection.close()

        return redirect(url_for('orders'))

    @app.route('/ordenes/eliminar/<int:order_id>', methods=['POST'])
    def delete_order_route(order_id):
        delete_order(order_id)
        return redirect(url_for('orders'))
    
    @app.route('/ordenes/editar/<int:order_id>', methods=['GET', 'POST'])
    def edit_order(order_id):
        connection = get_connection()
        
        if request.method == 'POST':
            name = request.form.get('name')
            service = request.form.get('service')
            notes = request.form.get('notes')
            cost = float(request.form.get('cost'))

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE orden_productos
                    SET Nombre = %s, Servicio = %s, Notas = %s, Costo = %s
                    WHERE ID = %s
                """, (name, service, notes, cost, order_id))

            connection.commit()
            connection.close()

            return redirect(url_for('orders'))
        
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM orden_productos WHERE ID = %s", (order_id,))
                order = cursor.fetchone()

            connection.close()
            
            return render_template('edit_order.html', order=order)

    try:
        app.run(host = '0.0.0.0', port = 5050, debug = True)
    except KeyboardInterrupt:
        exit()
"""
    Este es el archivo principal de la aplicación, recuerden no compartir datos sensibles
    en este apartado, recomiendo usar .env en todo momento.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_caching import Cache
from dotenv import load_dotenv
from PIL import Image, ExifTags
import requests
import hashlib
import random
import string
import os

from modules.db_connection import get_connection
from modules.db_connection import get_products_by_name
from modules.db_connection import new_order, update_order, get_order, delete_order, get_all_orders, get_unfinished_orders
from modules.db_connection import new_order_photo, get_order_photos, delete_order_photo
from modules.db_connection import get_user

if __name__ == '__main__':

    load_dotenv()

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/order_photos'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    class User(UserMixin):
        def __init__(self, user_id, username, name, photo):
            self.id = user_id
            self.username = username
            self.name = name
            self.photo = photo
                
    @login_manager.user_loader
    def load_user(user_id):
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario WHERE ID = %s", (user_id,))
            user = cursor.fetchone()

        connection.close()

        if user:
            return User(user[0], user[1], user[3], user[4])
        else:
            return None

    """
        El parámetro de host en 0.0.0.0 hará que puedan ver el render de las rutas de la
        página desde la ip de su máquina, pueden probarlo con su celular u otra máquina
        siempre que esten conectados en la misma red.

        También recuersen hacerlo usando https y no http.

        Ejemplo: https://192.168.100.10:5000

        Si quieren cambiar el protocolo de https a http, solo quiten ssl_context como parámetro.
    """

    @app.route('/')
    @login_required
    def index() -> str:
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login() -> str:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            username = request.form['username']
            password = request.form['password']

            possible_user = get_user(username)
            if possible_user and hashlib.md5(password.encode()).hexdigest() == possible_user[2]:
                user = User(possible_user[0], possible_user[1], possible_user[3], possible_user[4])
                login_user(user)
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))

            
    @app.route('/logout')
    @login_required
    def logout() -> str:
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/cotizacion', methods=['GET', 'POST'])
    @login_required
    def price_request() -> str:

        if request.method == 'POST':
            search_text = request.form.get('search', '').strip()
            keywords = search_text.split()
        else:
            keywords = []

        products = get_products_by_name(keywords)

        return render_template('products.html', products=products, search_text='')
    
    @app.route('/liberaciones', methods=['GET'])
    @login_required
    def unlocks() -> str:
        return render_template('unlocks.html')
    
    def generate_random_string(length=6):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def generate_temp_email():
        username = generate_random_string()
        domain = "1secmail.com"
        email_address = f"{username}@{domain}"
        return username, domain, email_address

    @app.route('/generate_temp_email')
    @login_required
    def generate_temp_email_route():
        username, domain, email_address = generate_temp_email()
        return jsonify({"username": username, "domain": domain, "email_address": email_address})
    
    @app.route('/read_email/<username>/<domain>/<mail_id>')
    def get_email_content(username, domain, mail_id):
        api_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={mail_id}"
        response = requests.get(api_url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch email content."}), 500

    @app.route('/check_inbox/<username>/<domain>')
    @login_required
    def check_inbox(username, domain):
        api_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
        response = requests.get(api_url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch emails."}), 500
    
    @app.route('/ordenes/todas', methods=['GET'])
    @login_required
    def all_orders():
        orders = get_all_orders()
        return render_template('all_orders.html', orders=orders)

    @app.route('/ordenes', methods=['GET', 'POST'])
    @login_required
    def orders():
        if request.method == 'POST':
            name = request.form.get('name')
            service = request.form.get('service')
            notes = request.form.get('notes', '')
            cost = float(request.form.get('cost'))
            invest = float(request.form.get('invest'))
            new_order(name, service, notes, cost, invest)
            return redirect(url_for('orders'))

        orders = get_unfinished_orders()
        return render_template('orders.html', orders=orders)
    
    @app.route('/ordenes/validar/<int:order_id>', methods=['POST'])
    @login_required
    def validate_order(order_id):
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("UPDATE orden_productos SET Estatus = 'Entregado', Fecha_Entrega = NOW() WHERE ID = %s", (order_id,))

        connection.commit()
        connection.close()

        return redirect(url_for('orders'))

    @app.route('/ordenes/eliminar/<int:order_id>', methods=['POST'])
    @login_required
    def delete_order_route(order_id):
        delete_order(order_id)
        return redirect(url_for('orders'))
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def compress_image(image_path, output_path, quality=85):
        with Image.open(image_path) as img:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            try:
                exif = dict(img._getexif().items())
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)

            except Exception as e:
                ...

            img.save(output_path, optimize=True, quality=quality)

    @app.route('/ordenes/eliminar_foto/<int:photo_id>', methods=['POST'])
    @login_required
    def delete_photo(photo_id):
        delete_order_photo(photo_id)
        return redirect(url_for('orders'))

    @app.route('/ordenes/editar/<int:order_id>', methods=['GET', 'POST'])
    @login_required
    def edit_order(order_id):
        if request.method == 'POST':
            name = request.form['name']
            service = request.form['service']
            notes = request.form['notes']
            cost = request.form['cost']
            investment = request.form['investment']

            update_order(name, service, notes, cost, investment, order_id)
            
            if 'files' in request.files:
                files = request.files.getlist('files')
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{order_id}_' + filename)
                        file.save(file_path)
                        compress_image(file_path, compressed_path)
                        os.remove(file_path)

                        new_order_photo(order_id, f'order_photos/{order_id}_{filename}'.replace('\\', '/'))

            return redirect(url_for('orders'))

        else:
            order = get_order(order_id)
            order_photos = get_order_photos(order_id)

            if order_photos == ():
                order_photos = ((-1,-1, 'order_photos/no_image.jpg'),)
            return render_template('edit_order.html', order=order, order_photos=order_photos)

    @app.route('/marcas')
    @cache.cached(timeout=60*5)
    @login_required
    def brands() -> str:
        search_query = request.args.get('search', '').lower()
        error = None
        brands = []

        try:
            response = requests.get('http://phone-specs-api-2.azharimm.dev/brands')
            data = response.json()
            brands = data['data'] if data['status'] else []
        except Exception as e:
            error = "Hubo un problema al comunicarse con la API de especificaciones de teléfonos."

        if search_query:
            brands = [brand for brand in brands if search_query in brand['brand_name'].lower()]

        return render_template('brands.html', brands=brands, error=error)
    
    @app.route('/marcas/<brand_slug>')
    @cache.cached(timeout = 60*3)
    @login_required
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
    
    def get_phone_details(detail_url):
        response = requests.get(detail_url)
        return response.json()

    @app.route('/details/', methods=['GET'])
    @login_required
    def phone_details():
        detail_url = request.args.get('url')
        phone = get_phone_details(detail_url)
        return render_template('phone_details.html', phone=phone['data'])

    @app.route('/api/order-stats', methods=['GET'])
    @login_required
    def order_stats():
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT SUM(Costo) FROM orden_productos WHERE Estatus='Entregado'")
        delivered_cost = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(Inversion) FROM orden_productos WHERE Estatus='Entregado'")
        delivered_investment = cursor.fetchone()[0] or 0

        profit = delivered_cost - delivered_investment
        
        cursor.execute("SELECT SUM(Costo) FROM orden_productos WHERE Estatus='Pendiente'")
        pending_cost = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(Inversion) FROM orden_productos WHERE Estatus='Pendiente'")
        pending_investment = cursor.fetchone()[0] or 0

        pending_cost = pending_cost - pending_investment
        
        connection.close()
        
        return jsonify({'profit': profit, 'invest': delivered_investment + pending_investment, 'pending': pending_cost})
    try:
        app.run(host = '0.0.0.0', port = 5050, debug = True)
    except KeyboardInterrupt:
        exit()
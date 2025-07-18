"""
    Este es el archivo principal de la aplicación, recuerden no compartir datos sensibles
    en este apartado, recomiendo usar .env en todo momento.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_caching import Cache
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
import threading
import user_agents
import requests
import hashlib
import os
import subprocess
from datetime import datetime

from modules.db_connection import get_connection
from modules.db_connection import new_note, get_notes
from modules.db_connection import get_products
from modules.db_connection import get_parts_by_name
from modules.db_connection import new_repair_order, update_repair_order, get_repair_order, validate_repair_order, delete_repair_order, get_all_repair_orders, get_unfinished_repair_orders
from modules.db_connection import new_order_media, get_order_media, delete_order_media
from modules.db_connection import get_user
from modules.backup_implementation import auto_backup_thread, perform_backup

from modules.email_handlers import generate_temp_email

from modules.image_handlers import allowed_file, compress_image

from modules.cache_implementation import start_cache_updater, load_brands_from_cache, save_brands_to_cache, fetch_brands_from_api

if __name__ == '__main__':

    # Encargado de cargar las variables establecidas en el .env

    load_dotenv(override = True)

    # Configuramos la aplicación para soportar la subida de imagenes

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/order_photos'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    # Para la api de los telefonos y la interfaz usamos un cache simple

    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    """
        Las configuraciones y estructuras de nuestro usuario usando el login manager
        que nos provee flask_login.

        Importante si modificamos la base de datos en los atributos de usuario a futuro
        para tener los datos cargados siempre, debemos modificar la clase User, asi como
        la función load_user que sobrescribe el user_loader de flask_login.
    """

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    def format_date_and_difference(created_at) -> str:
        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                created_at = datetime.strptime(created_at, '%Y-%m-%d')
        
        current_date = datetime.now()
        difference_in_days = (current_date - created_at).days

        formatted_date = created_at.strftime('%Y-%m-%d')
        
        return f"{formatted_date} (hace {difference_in_days} días)"

    app.jinja_env.filters['format_date_and_difference'] = format_date_and_difference

    class User(UserMixin):
        def __init__(self, data: tuple):
            self.id = data[0]
            self.name = data[1]
            self.email = data[2]
            self.password = data[3]
            self.profile_picture = data[4]
            self.created_at = data[5]

    @login_manager.user_loader
    def load_user(user_id) -> Optional[User]:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

        connection.close()

        if user:
            return User(user)
        else:
            return None

    """
        Todas las rutas menos 'login' tienen que tener el decorador @login_required para asegurar
        la integridad de la base de datos.
    """

    @app.route('/')
    @login_required
    def index() -> Response:
        user = current_user
        user_agent = request.headers.get('User-Agent')
        ua = user_agents.parse(user_agent)

        products = get_products()

        if ua.is_mobile:
            return render_template('index_mobile.html', user=user, products=products)
        else:
            return render_template('index.html', user=user, products=products)

    @app.route('/user_dashboard')
    @login_required
    def user_dashboard() -> Response:

        user = current_user
        user_agent = request.headers.get('User-Agent')
        ua = user_agents.parse(user_agent)

        if ua.is_mobile:
            return render_template('user_dashboard_mobile.html', user=user)
        else:
            return render_template('user_dashboard.html', user=user)

    @app.route("/update_repo", methods=["GET", "POST"])
    @login_required
    def update_repo():
        if request.method == 'POST':
            try:
                result = subprocess.run(["git", "pull"], cwd=os.getcwd(), capture_output = True, text = True)

                if "Already up to date." in result.stdout:
                    flash("El repositorio ya está actualizado.", "info")
                else:
                    flash("Repositorio actualizado con éxito.", "success")
                
            except Exception as e:
                flash(f"Error al actualizar: {str(e)}", "danger")

            return redirect(url_for("update_repo"))
        else:
            return redirect(url_for("user_dashboard"))

    @app.route("/backup_db", methods=["GET", "POST"])
    @login_required
    def backup_db():
        try:
            load_dotenv(override=True)

            db_host = os.getenv("DB_HOST")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_name = os.getenv("DB_NAME")
            db_port = os.getenv("DB_PORT")

            backup_dir = os.path.join(os.getcwd(), "sql_source")
            os.makedirs(backup_dir, exist_ok=True) 

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"{db_name}_backup_{timestamp}.sql")

            dump_command = [
                "mysqldump",
                "-h", db_host,
                "-P", str(db_port),
                "-u", db_user,
                f"--password={db_password}",
                "--databases", db_name,
                "--routines",
                "--events",
                "--single-transaction",
                "--quick",
                "--compact"
            ]

            with open(backup_file, "w") as f:
                subprocess.run(dump_command, stdout=f, check=True)

            return redirect(url_for("user_dashboard"))
            
        except Exception as e:
            return str(e)

    @app.route('/notes')
    @login_required
    def notes():
        notes = get_notes()
        return render_template('notes.html', notes = notes)

    @app.route('/create_note', methods=['POST'])
    @login_required
    def create_note():
        title = request.form.get('title')
        content = request.form.get('content')
        remove_at = request.form.get('remove_at')
        created_at = datetime.now()

        new_note(current_user.id, title, content, created_at, remove_at)

        return jsonify({'message': 'Nota creada exitosamente'}), 200

    @app.route('/delete_note', methods=['POST'])
    @login_required
    def delete_note():
        remove_note(note_id)
        return jsonify({'message': 'Nota creada exitosamente'}), 200
    
    @app.route('/login', methods=['GET', 'POST'])
    def login() -> Response:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            email = request.form['email']
            password = request.form['password']

            possible_user = get_user(email)

            if possible_user and hashlib.md5(password.encode()).hexdigest() == possible_user[3]:
                user = User(possible_user)
                login_user(user)
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))

    @app.route('/logout')
    @login_required
    def logout() -> Response:
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/cotizacion', methods=['GET', 'POST'])
    @login_required
    def price_request() -> Response:

        if request.method == 'POST':
            search_text = request.form.get('search', '').strip()
            keywords = search_text.split()
        else:
            keywords = []

        parts = get_parts_by_name(keywords)

        return render_template('parts.html', parts=parts, search_text='')
    
    @app.route('/liberaciones', methods=['GET'])
    @login_required
    def unlocks() -> Response:
        return render_template('unlocks.html')
    
    """
        Para generar correos usamos la api de 1secmail, para ello podemos usar el dominio
        por defecto de esta api, aunque hay más solo he probado con este y funciona bien.

        Por cualquier modificación a futuro la documentacion esta en: https://www.1secmail.com/api/
    """

    @app.route('/generate_temp_email')
    @login_required
    def generate_temp_email_route() -> dict:
        username, domain, email_address = generate_temp_email()  
        return jsonify({"username": username, "domain": domain, "email_address": email_address})
    
    @app.route('/read_email/<username>/<domain>/<mail_id>')
    @login_required
    def get_email_content(username, domain, mail_id) -> dict:
        api_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={mail_id}"
        response = requests.get(api_url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch email content."}), 500

    @app.route('/check_inbox/<username>/<domain>')
    @login_required
    def check_inbox(username, domain) -> dict:
        api_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
        response = requests.get(api_url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch emails."}), 500
    
    @app.route('/ordenes/todas', methods=['GET'])
    @login_required
    def all_orders() -> Response:
        orders = get_all_repair_orders()
        return render_template('all_orders.html', orders=orders)

    @app.route('/ordenes', methods=['GET', 'POST'])
    @login_required
    def orders() -> Response:
        if request.method == 'POST':
            client_name = request.form.get('client_name')
            model = request.form.get('model')
            service = request.form.get('service')
            observations = request.form.get('observations', '')
            cost = float(request.form.get('cost'))
            investment = float(request.form.get('investment'))
            new_repair_order(client_name, current_user.id, model, service, observations, '', '', cost, investment)
            return redirect(url_for('orders'))

        user_agent = request.headers.get('User-Agent')
        ua = user_agents.parse(user_agent)

        # Solo cargamos las ordenes pendientes.
        orders = get_unfinished_repair_orders()

        if ua.is_mobile:
            return render_template('orders_mobile.html', orders=orders)
        else:
            return render_template('orders.html', orders=orders)

    @app.route('/ordenes/validar/<int:repair_order_id>', methods=['POST'])
    @login_required
    def validate_order(repair_order_id) -> Response:
        validate_repair_order(repair_order_id)
        return redirect(url_for('orders'))

    @app.route('/ordenes/eliminar/<int:order_id>', methods=['POST'])
    @login_required
    def delete_order_route(order_id) -> Response:
        delete_repair_order(order_id)
        return redirect(url_for('orders'))
    
    """
        La lógica para subir imagenes también requiere ajustes como la compresión de las mismas
        he intentado bajar la calidad de las mismas antes de guardarlas pero actualmente desconozco
        si esto funciona bien.

        La función allowed_file solamente verifica si la imagen es compatible en los formatos, de tal
        manera que si el usuario usa la cámara del celular no pueda subir videos (de momento).

        A su vez, la orientación de las imagenes se ve afectada algunas veces dependiendo del celular
        que tome la foto, la función compress_image más allá de hacer la compresión verifica la orientación.

        Aunque es posible subir varias imagenes al mismo tiempo recomiendo hacerlo una por una.
    """

    @app.route('/ordenes/eliminar_foto/<int:media_id>', methods=['POST'])
    @login_required
    def delete_photo(media_id) -> Response:
        delete_order_media(media_id)
        return redirect(url_for('orders'))

    @app.route('/ordenes/editar/<int:repair_order_id>', methods=['GET', 'POST'])
    @login_required
    def edit_order(repair_order_id) -> Response:
        if request.method == 'POST':
            client_name = request.form['client_name']
            model = request.form['model']
            service = request.form['service']
            observations = request.form['observations']
            repair_details = request.form['repair_details']
            post_details = request.form['post_details']
            cost = request.form['cost']
            investment = request.form['investment']

            update_repair_order(client_name, model, service, observations, repair_details, post_details, cost, investment, repair_order_id)
            
            if 'files' in request.files:
                files = request.files.getlist('files')
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{repair_order_id}_' + filename)
                        file.save(file_path)
                        compress_image(file_path, compressed_path)
                        os.remove(file_path)

                        new_order_media(repair_order_id, f'order_photos/{repair_order_id}_{filename}'.replace('\\', '/'))

        order = get_repair_order(repair_order_id)
        order_media = get_order_media(repair_order_id)

        # Si la orden que esta siendo editada no contiene imagenes mandamos una imagen nula default.

        if order_media == ():
            order_media = ({'media_id': -1, 'order_id': -1,'directory': 'order_photos/no_image.jpg'},)

        user_agent = request.headers.get('User-Agent')
        ua = user_agents.parse(user_agent)

        if ua.is_mobile:
            return render_template('edit_order_mobile.html', order=order, order_media=order_media)
        else:
            return render_template('edit_order.html', order=order, order_media=order_media)


    @app.route('/marcas')
    @login_required
    def brands() -> Response:
        search_query = request.args.get('search', '').lower()
        error = None

        brands = load_brands_from_cache()
        if not brands:
            brands = fetch_brands_from_api()
            if brands:
                save_brands_to_cache(brands)
            else:
                error = "Hubo un problema al comunicarse con la API de especificaciones de teléfonos."

        if search_query:
            brands = [brand for brand in brands if search_query in brand['brand_name'].lower()]

        return render_template('brands.html', brands=brands, error=error)
        
    @app.route('/marcas/<brand_slug>')
    @login_required
    def information(brand_slug) -> Response:
        search_query = request.args.get('search', '').lower()
        page = request.args.get('page', 1, type=int)
        error = None

        last_valid_page = app.config.get(f'last_page_{brand_slug}', 1)

        try:
            response = requests.get(f'http://phone-specs-api.vercel.app/brands/{brand_slug}?page={page}')
            data = response.json()

            if data['status']:
                title = data['data']['title']
                current_page = data['data']['current_page']
                last_page = data['data']['last_page']
                phones = data['data']['phones']

                if not phones and current_page > 1:
                    return redirect(url_for('information', brand_slug=brand_slug, page=last_valid_page, search=search_query))

                app.config[f'last_page_{brand_slug}'] = current_page

            else:
                error = "No se encontraron datos para la marca solicitada."
                title = "Información no disponible"
                phones = []

        except Exception as e:
            error = "Hubo un problema al comunicarse con la API de especificaciones de teléfonos."
            title = "Error de conexión"
            phones = []

        if search_query:
            phones = [phone for phone in phones if search_query in phone['phone_name'].lower()]

        return render_template('phones.html', title=title, brand_slug=brand_slug, phones=phones, current_page=page, last_page=last_page, search_query=search_query, error=error)

    def get_phone_details(detail_url) -> dict:
        response = requests.get(detail_url)
        return response.json()

    @app.route('/details/', methods=['GET'])
    @login_required
    def phone_details() -> Response:
        detail_url = request.args.get('url')
        phone = get_phone_details(detail_url)
        return render_template('phone_details.html', phone=phone['data'])

    @app.route('/api/order-stats', methods=['GET'])
    @login_required
    def order_stats() -> dict:
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # Si no se proporciona un rango de fechas, se usa el mes actual
        if not start_date or not end_date:
            current_year = datetime.now().year
            current_month = datetime.now().month
            start_date = datetime(current_year, current_month, 1).strftime('%Y-%m-%d')
            end_date = datetime(current_year, current_month, 28).strftime('%Y-%m-%d')  # Para asegurar que el mes se termine en 28

        connection = get_connection()
        cursor = connection.cursor()

        # Filtrado de datos por rango de fechas
        cursor.execute("""
            SELECT 
                cost, 
                investment, 
                delivered_at 
            FROM repair_orders 
            WHERE status='Entregado' 
            AND delivered_at BETWEEN %s AND %s
        """, (start_date, end_date))
        
        delivered_records = cursor.fetchall()
        delivered_data = [
            {
                'cost': record[0],
                'investment': record[1],
                'date': record[2].strftime('%Y-%m-%d %H:%M:%S')
            } for record in delivered_records
        ]

        cursor.execute("""
            SELECT 
                cost, 
                investment, 
                created_at 
            FROM repair_orders 
            WHERE status='Pendiente' 
            AND created_at BETWEEN %s AND %s
        """, (start_date, end_date))
        
        pending_records = cursor.fetchall()
        pending_data = [
            {
                'cost': record[0],
                'investment': record[1],
                'date': record[2].strftime('%Y-%m-%d %H:%M:%S')
            } for record in pending_records
        ]
        
        # Calculamos las sumas de cost y investment
        delivered_cost = sum(record['cost'] for record in delivered_data)
        delivered_investment = sum(record['investment'] for record in delivered_data)
        delivered_profit = delivered_cost - delivered_investment

        pending_cost = sum(record['cost'] for record in pending_data)
        pending_investment = sum(record['investment'] for record in pending_data)
        pending_balance = pending_cost - pending_investment

        connection.close()

        return jsonify({
            'profit': delivered_profit,
            'invest': pending_investment,
            'pending': pending_balance,
            'deliveredRecords': delivered_data,
            'pendingRecords': pending_data
        })
    try:
        """
        El parámetro de host en 0.0.0.0 hará que puedan ver el render de las rutas de la
        página desde la ip de su máquina, pueden probarlo con su celular u otra máquina
        siempre que esten conectados en la misma red.

        También recuersen hacerlo usando https y no http.

        Ejemplo: https://192.168.100.10:5000

        Si quieren cambiar el protocolo de https a http, solo quiten ssl_context como parámetro.
        """
        start_cache_updater()
        threading.Thread(target=auto_backup_thread, daemon=True).start()
        app.run(host = '0.0.0.0', port = 5050, debug = True)
    except KeyboardInterrupt:
        exit()
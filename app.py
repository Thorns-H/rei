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
import calendar
from typing import Optional
import threading
import user_agents
import requests
import hashlib
import os
import subprocess
import re
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
import numpy as np
import csv
import io

from modules.db_connection import get_connection
from modules.db_connection import new_note, get_notes, get_note_by_id, update_note, remove_note
from modules.db_connection import get_products, new_product, get_product_by_id, update_product, delete_product, sell_product
from modules.db_connection import get_parts_by_name
from modules.db_connection import new_repair_order, update_repair_order, get_repair_order, validate_repair_order, delete_repair_order, get_all_repair_orders, get_unfinished_repair_orders
from modules.db_connection import new_order_media, get_order_media, delete_order_media
from modules.db_connection import get_user
from modules.backup_implementation import auto_backup_thread, perform_backup

from modules.email_handlers import generate_temp_email

from modules.image_handlers import allowed_file, compress_image
from werkzeug.utils import secure_filename

from modules.cache_implementation import start_cache_updater, load_brands_from_cache, save_brands_to_cache, fetch_brands_from_api

# --- Importaciones IA ---
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from markupsafe import escape
import mysql.connector
from mysql.connector import Error

# Encargado de cargar las variables establecidas en el .env
load_dotenv(override = True)

# Configuramos la aplicación para soportar la subida de imagenes
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/order_photos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# Para la api de los telefonos y la interfaz usamos un cache simple
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

"""
    Las configuraciones y estructuras de nuestro usuario usando el login manager
    que nos provee flask_login.
"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Variables Globales para la IA ---
global_entries = []
global_model = None


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
    return redirect(url_for('notes'))


@app.route('/notes/edit/<int:note_id>', methods=['POST'])
@login_required
def edit_note_post(note_id):
    
    note = get_note_by_id(note_id)
    if not note or note['user_id'] != current_user.id:
        flash('No tienes permiso para editar esta nota.', 'danger')
        return redirect(url_for('notes'))

    title = request.form.get('title')
    content = request.form.get('content')
    remove_at = request.form.get('remove_at')
    update_note(note_id, title, content, remove_at)
    
    return redirect(url_for('notes'))

@app.route('/notes/delete/<int:note_id>')
@login_required
def delete_note_route(note_id):

    note = get_note_by_id(note_id)
    if not note:
        flash('No se encontró la nota.', 'danger')
        return redirect(url_for('notes'))
    
    # Solo el usuario que creó la nota puede eliminarla
    if note['user_id'] != current_user.id:
        flash('No tienes permiso para eliminar esta nota.', 'danger')
        return redirect(url_for('notes'))

    try:
        remove_note(note_id)
        flash('Nota eliminada con éxito.', 'success')
    except Exception as e:
        flash(f'Error al eliminar la nota: {e}', 'danger')
    
    return redirect(url_for('notes'))



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
    query = request.args.get("q", "").lower()  # lo que escribe el usuario en el buscador
    orders = get_all_repair_orders()

    if query:
        orders = [
            order for order in orders
            if query in order['client_name'].lower()
            or query in f"{order['repair_order_id']:06d}".lower()
            or query in order['service'].lower()
            or query in order['status'].lower()
        ]

    return render_template('all_orders.html', orders=orders, query=query)

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
        

        last_day_num = calendar.monthrange(current_year, current_month)[1]
        end_date = datetime(current_year, current_month, last_day_num).strftime('%Y-%m-%d')

        # Añadimos la hora final para incluir el último día
        end_date = f"{end_date} 23:59:59"

    else:
        end_date = f"{end_date} 23:59:59"

    connection = get_connection()
    cursor = connection.cursor()


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

# ----- productos ---------

@app.route('/product/create', methods=['POST'])
@login_required
def create_product():
    if 'image' not in request.files:
        flash('No se seleccionó ningún archivo de imagen', 'danger')
        return redirect(url_for('index'))
        
    file = request.files['image']
    
    if file.filename == '':
        flash('No se seleccionó ningún archivo de imagen', 'danger')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        
        
        filename = secure_filename(file.filename)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"prod_{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
        compressed_path = file_path 
        
        file.save(file_path)
        compress_image(file_path, compressed_path, 800) 
        

        final_image_folder = os.path.join('static', 'images')
        final_image_path = os.path.join(final_image_folder, unique_filename)
        
        
        os.rename(compressed_path, final_image_path)
        
        image_db_name = unique_filename 

        try:
            new_product(name, image_db_name, category, description, price, stock)
            flash('Producto creado exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al crear el producto: {e}', 'danger')
            
    return redirect(url_for('index'))


@app.route('/product/edit/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    stock = int(request.form.get('stock'))
    
    image_db_name = None 


    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):

            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"prod_{timestamp}_{filename}"
            
            final_image_folder = os.path.join('static', 'images')
            final_image_path = os.path.join(final_image_folder, unique_filename)

            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(temp_path)
            compress_image(temp_path, final_image_path, 800) 
            os.remove(temp_path) 
            
            image_db_name = unique_filename 
            
    try:
        update_product(product_id, name, category, description, price, stock, image_db_name)
        flash('Producto actualizado con éxito.', 'success')
    except Exception as e:
        flash(f'Error al actualizar el producto: {e}', 'danger')
        
    return redirect(url_for('index'))


@app.route('/product/delete/<int:product_id>')
@login_required
def delete_product_route(product_id):
    try:
        delete_product(product_id)
        flash('Producto eliminado con éxito.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el producto: {e}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/product/sell/<int:product_id>')
@login_required
def sell_product_route(product_id):
    try:
        
        success = sell_product(product_id, current_user.id)
        
        if success:
            flash('¡Venta registrada! El stock ha sido actualizado.', 'success')
        else:
            flash('El producto está agotado, no se puede vender.', 'danger')
            
    except Exception as e:
        flash(f'Error al procesar la venta: {e}', 'danger')
    
    return redirect(url_for('index'))

# --- IA ---

def daten_uploaden_sql():

    # Se conecta directo a la base de datos
    
    entries = []
    connection = None
    try:

        db_password = os.getenv("DB_PASSWORD")
        db_port = int(os.getenv("DB_PORT", 3306)) 

        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=db_password, 
            database=DB_NAME,
            port=db_port            
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT repair_order_id, observations, post_details 
                FROM repair_orders
                WHERE observations IS NOT NULL AND observations NOT IN ('', 'ninguna')
                AND post_details IS NOT NULL AND post_details NOT IN ('', 'ninguna')
            """
            cursor.execute(query)
            
            for row in cursor.fetchall():
                entries.append({
                    "repair_order_id": row["repair_order_id"],
                    "observations": row["observations"],
                    "post_details": row["post_details"]
                })
                
            cursor.close()

    except Error as e:
        print(f"Error al conectar o consultar MySQL: {e}")
        raise e 
    
    finally:
        if connection and connection.is_connected():
            connection.close()
            
    print(f"Valid entries found: {len(entries)}")
    for i, e in enumerate(entries[:3]):
        print(f"{i+1}. ID: {e['repair_order_id']} - Obs: {e['observations']} - Post: {e['post_details']}")

    if len(entries) < 3:
        raise ValueError("Not enough valid observations.")
    return entries

def train_word2vec(entries):
    corpus = [
        e["observations"].lower().split() 
        for e in entries 
        if e.get("observations")
    ]
    if not corpus:
        raise ValueError("No hay observaciones válidas para entrenar el modelo.")
        
    model = Word2Vec(vector_size=50, window=3, min_count=1, sg=1)
    model.build_vocab(corpus)
    model.train(corpus, total_examples=len(corpus), epochs=150)
    return model

def vectorize(text, model):
    words = text.lower().split()
    vectors = [model.wv[w] for w in words if w in model.wv.key_to_index]
    return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)

# Esta funcion solo se llama una sola vez
def initialize_ia():

    global global_entries, global_model
    print("-------------------------------------Iniciando carga de datos y entrenamiento de IA--------------------------------------")
    try:
        global_entries = daten_uploaden_sql()
        global_model = train_word2vec(global_entries)
        print("---------------------------------------IA entrenada------------------------------------")
    except Exception as e:
        print(f"ERROR FATAL: No se pudo inicializar la IA. {e}")
        # Definimos como None para evitar el NameError y que la ruta
        # /diagnosticar muestre un error controlado
        global_entries = []
        global_model = None

@app.route("/diagnosticar")
# @login_required # Descomenta esto cuando lo integres
def diagnosticar():
    observacion = request.args.get("observacion", "").strip()
    if not observacion:
        return "<h3 style='color:red'>No se proporcionó ninguna observación.</h3>"

    # se verifica que la IA este cargada
    if not global_model or not global_entries:
        return "<h3 style='color:red'>Error: El sistema de IA no está inicializado. (Revise la consola para 'ERROR FATAL')</h3>"

    try:
        
        input_vec = vectorize(observacion, global_model)
        if np.all(input_vec == 0):
            return render_template(
                "diagnose.html", 
                resultados=[], 
                entrada=observacion, 
                error="No se encontraron palabras clave de tu observación en la base de datos."
            )

        # Calcular similitudes
        similar = []
        for entry in global_entries:
            vec = vectorize(entry["observations"], global_model)
            score = cosine_similarity([input_vec], [vec])[0][0]
            similar.append((score, entry))

        # Top 5
        best = sorted(similar, key=lambda x: x[0], reverse=True)[:5]

        results = [{
            "id": e["repair_order_id"],
            "observations": e["observations"],
            "post_details": e["post_details"],
            "score": round(score, 2)
        } for score, e in best if score > 0.1] 

        return render_template("diagnose.html", resultados=results, entrada=observacion)

    except Exception as e:
        return f"<h3 style='color:red'>Error en diagnóstico: {str(e)}</h3>"

#inicia la IA antes de prender el servidor
initialize_ia()

if __name__ == '__main__':
    try:
        """
        El parámetro de host en 0.0.0.0 hará que puedan ver el render de las rutas de la
        página desde la ip de su máquina, pueden probarlo con su celular u otra máquina
        siempre que esten conectados en la misma red.
        """
        start_cache_updater()
        threading.Thread(target=auto_backup_thread, daemon=True).start()
        app.run(host = '0.0.0.0', port = 8000, debug = True)
        
    except KeyboardInterrupt:
        exit()
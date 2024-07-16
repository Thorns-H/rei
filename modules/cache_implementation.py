from datetime import datetime

import threading
import requests
import json
import time
import os

CACHE_FILE_PATH = 'cache/brands.json'

def fetch_brands_from_api() -> list:
    try:
        response = requests.get('http://phone-specs-api.vercel.app/brands')
        response.raise_for_status()
        data = response.json()
        brands = data['data'] if data['status'] else []
        return brands
    except Exception as e:
        print(f"Error obteniendo datos de la API: {e}")
        return []

def save_brands_to_cache(brands)  -> None:
    with open(CACHE_FILE_PATH, 'w') as cache_file:
        json.dump(brands, cache_file)

def load_brands_from_cache() -> list:
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'r') as cache_file:
            return json.load(cache_file)
    return []

def update_cache() -> None:
    while True:
        current_time = datetime.now()
        if current_time.hour == 12 or current_time.hour == 0:
            brands = fetch_brands_from_api()
            save_brands_to_cache(brands)
        time.sleep(3600)

def start_cache_updater():
    cache_updater_thread = threading.Thread(target=update_cache)
    cache_updater_thread.daemon = True
    cache_updater_thread.start()
# 🌐 REI Web Assistant

REI Web Assistant is a comprehensive web application designed to facilitate the management of a phone repair business. The application offers various features including price quotations, 
product information lookup, order management, and more. This project is built using Flask, a lightweight web framework for Python, and leverages Bootstrap for the front-end design.

# Showcase (Updated 18/12/2024) 
https://github.com/user-attachments/assets/ee433e69-1cb4-42d2-a1c2-0f4fee638154

## Basic setup:

* Clone this repository.
```
git clone https://github.com/Thorns-H/rei.git && cd rei
```
* Using your SGBD (in this example im using mysql) create and import the database:
```
CREATE DATABASE new_database;
mysql -u username -p new_database < sql_source/database.sql
```

## Database Diagram
![](https://drive.google.com/uc?export=view&id=185PqdotsheNfz3w2crXXDIYWsKEOz2Kf)

* You need to create a .env file with all your personal information to run the app, this is an example:
```
DB_HOST = YOUR_HOST
DB_USER = YOUR_USER
DB_PASSWORD = YOUR_PASSWORD
DB_NAME = YOUR_DATABASE
DB_PORT = YOUR_PORT (3306 by default)
FLASK_SECRET_KEY = YOUR_FLASK_KEY
```
## Setting up the dependencies:

* Linux:
```
python3 -m venv rei_venv
source rei_venv/bin/activate
pip3 install -r requirements.txt
```
* Windows:
```
py -m venv rei_venv
source rei_venv/Scripts/activate.bat
pip install -r requirements.txt
```

Finishing this steps you can now run the `app.py` and log into the browser using `DB_HOST:5050`.

## API's
* To get all the phones data: [phone-specs-api](https://github.com/azharimm/phone-specs-api).
* To generate temporaly emails: [1secmail](https://www.1secmail.com/api/).



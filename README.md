# 🌐 REI Web Assistant

REI Web Assistant is a comprehensive web application designed to facilitate the management of a phone repair business. The application offers various features including price quotations, 
product information lookup, order management, and more. This project is built using Flask, a lightweight web framework for Python, and leverages Bootstrap for the front-end design.

## How to run

* Clone this repository.
```
git clone https://github.com/Thorns-H/rei.git && cd rei
```
* Using your SGBD (in this example im using mysql) create and import the database:
```
CREATE DATABASE new_database;
mysql -u username -p new_database < sql_source/database.sql
```
* You need to create a .env file with all your personal information to run the app, this is an example:
```
DB_USER = YOUR_USER
DB_PASSWORD = YOUR_PASSWORD
DB_NAME = YOUR_DATABASE
DB_PORT = YOUR_PORT
FLASK_SECRET_KEY = YOUR_FLASK_KEY
```

## Preview
![](https://s12.gifyu.com/images/SYJF6.gif)

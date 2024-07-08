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

## API's
* To get all the phones data: [phone-specs-api](https://github.com/azharimm/phone-specs-api).
* To generate temporaly emails: [1secmail](https://www.1secmail.com/api/).

## Preview (some screenshots can be outdated)
![](https://drive.google.com/uc?export=view&id=1AwbvBeaCfHdeYx7lDBseJF5FZLRMy1m1)
![](https://drive.google.com/uc?export=view&id=1gGshO7zAEBmmI5T7C2_860inx62_cipq)
![](https://drive.google.com/uc?export=view&id=10td2nPxjk7v4zZKUxUpLUOUZG-Ndg11o)
![](https://drive.google.com/uc?export=view&id=1TaNzcytM_TRgHZ7-pLKbQC8X7iRc5rFC)
![](https://drive.google.com/uc?export=view&id=1U1jox2g9mb6QkK2W_6PnRfgEYYvCFVip)
![](https://drive.google.com/uc?export=view&id=1PMhxMW0EQ2UuI1hFI0rqwgRUPrgAJPRf)
![](https://drive.google.com/uc?export=view&id=1mUI-g8n5yoCV1I6hVS-pHVqVDLSzj0-O)

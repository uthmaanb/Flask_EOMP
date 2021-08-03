import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password


# class Product(object):
#     def __init__(self, prod_id, name, prod_type):
#         self.id = prod_id
#         self.name = name
#         self.type = prod_type


def users_table():
    conn = sqlite3.connect('shop.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "username TEXT NOT NULL, "
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "address TEXT NOT NULL)")
    print("users table created successfully")
    conn.close()


def fetch_users():
    with sqlite3.connect('shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchall()

        new_data = []

        for data in user:
            new_data.append(User(data[0], data[1], data[5]))
    return new_data


def prod_table():
    conn = sqlite3.connect('shop.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "name TEXT NOT NULL,"
                 "price TEXT NOT NULL,"
                 "description TEXT NOT NULL,"
                 "prod_type TEXT"
                 "quantity TEXT NOT NULL)")
    print("product table created successfully")
    conn.close()


# def fetch_prod():
#     with sqlite3.connect("shop.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM products")
#         items = cursor.fetchall()
#
#         new_item = []
#
#         for data in items:
#             print(data)
#             new_item.append(Product(data[0], data[1], data[4]))
#         return new_item


users_table()
# prod_table()
users = fetch_users()
# products = fetch_prod()


user_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

# prod_table = {p.name: p for p in products}
# productid_table = {p.id: p for p in products}


def authenticate(username, password):
    user = user_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']

        with sqlite3.connect('shop.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users("
                           "username,"
                           "first_name,"
                           "last_name,"
                           "email,"
                           "password,"
                           "address) VALUES(?, ?, ?, ?, ?, ?)",
                           (username, first_name, last_name, email, password, address))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/prod-registration/', methods=["POST"])
def prod_registration():
    response = {}

    if request.method == "POST":

        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        prod_type = request.form['prod']
        quantity = request.form['username']

        with sqlite3.connect('shop.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users("
                           "username,"
                           "first_name,"
                           "last_name,"
                           "email,"
                           "password,"
                           "address) VALUES(?, ?, ?, ?, ?, ?)",
                           (name, price, description, prod_type, quantity))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/show-products')
def show_products():
    response = {}

    with sqlite3.connect("shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")

        response["status_code"] = 200
        response["description"] = "Displaying all products successfully"
        response["data"] = cursor.fetchall()
    return jsonify(response)


if __name__ == '__main__':
    app.run()

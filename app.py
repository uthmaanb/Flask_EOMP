import hmac
import sqlite3

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


# create class as part of flask requirements
class User(object):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.usern ame = username
        self.password = password


# create tables in sqlite
def users_table():
    conn = sqlite3.connect('shoppy.db')
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
    with sqlite3.connect('shoppy.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchall()

        new_data = []

        for data in user:
            new_data.append(User(data[0], data[1], data[5]))
    return new_data


def prod_table():
    conn = sqlite3.connect('shoppy.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "name TEXT NOT NULL,"
                 "price TEXT NOT NULL,"
                 "description TEXT NOT NULL,"
                 "prod_type TEXT NOT NULL,"
                 "quantity TEXT NOT NULL)")
    print("product table created successfully")
    conn.close()


users_table()
prod_table()
users = fetch_users()


user_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


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

        with sqlite3.connect('shoppy.db') as conn:
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
        prod_type = request.form['prod_type']
        quantity = request.form['quantity']

        with sqlite3.connect('shoppy.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products("
                           "name,"
                           "price,"
                           "description,"
                           "prod_type,"
                           "quantity) VALUES(?, ?, ?, ?, ?)",
                           (name, price, description, prod_type, quantity))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/show-products')
def show_products():
    response = {}

    with sqlite3.connect("shoppy.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")

        response["status_code"] = 200
        response["description"] = "Displaying all products successfully"
        response["data"] = cursor.fetchall()
    return jsonify(response)


@app.route('/delete-products/<int:prod_id>')
def delete_products(prod_id):
    response = {}
    with sqlite3.connect("shoppy.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE prod_id=" + str(prod_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product successfully deleted"

    return response


@app.route('/edit-prod/<int:prod_id>', methods=["PUT"])
def edit_products(prod_id):
    response = {}
    if request.method == "PUT":
        with sqlite3.connect("shoppy.db") as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect("shoppy.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET price=? WHERE prod_id=?", (put_data["price"], prod_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200
                return response

            if incoming_data.get("quantity") is not None:
                put_data["quantity"] = incoming_data.get("quantity")
                with sqlite3.connect("shoppy.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET quantity=? WHERE prod_id=?", (put_data["quantity"], prod_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200
                return response


if __name__ == '__main__':
    app.run()

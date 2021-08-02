import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


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


def prod_table():
    conn = sqlite3.connect('shop.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS products(user_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "name TEXT NOT NULL,"
                 "description TEXT NOT NULL,"
                 "price TEXT NOT NULL,"
                 "quantity TEXT NOT NULL)")
    print("product table created successfully")
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


users = fetch_users()

users_table()
prod_table()


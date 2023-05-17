from flask import Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib
from login_registration.login_registration import login_registration_blueprint
from products.products import products_blueprint
from carts.carts import carts_blueprint
from orders.orders import orders_blueprint
from reviews.reviews import reviews_blueprint
from chats.chats import chats_blueprint
from complaints.complaints import complaints_blueprint
from home.home import home_blueprint
from db import conn


app = Flask(__name__)


app.register_blueprint(login_registration_blueprint)
app.register_blueprint(products_blueprint)
app.register_blueprint(carts_blueprint)
app.register_blueprint(orders_blueprint)
app.register_blueprint(reviews_blueprint)
app.register_blueprint(chats_blueprint)
app.register_blueprint(complaints_blueprint)
app.register_blueprint(home_blueprint)


app.secret_key = os.urandom(24)


if __name__ == '__main__':
    app.run(debug=True)
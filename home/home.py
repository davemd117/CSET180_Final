from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

home_blueprint = Blueprint("home_blueprint", __name__, template_folder="templates")


@home_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        session.clear()
        return render_template('home.html')
    

@home_blueprint.route('/filter_category_gpu')
def filter_category_gpu():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='GPU'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@home_blueprint.route('/filter_category_mobo')
def filter_category_mobo():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='Motherboard'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@home_blueprint.route('/filter_category_ram')
def filter_category_ram():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='RAM'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@home_blueprint.route('/filter_category_case')
def filter_category_case():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='Case'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)
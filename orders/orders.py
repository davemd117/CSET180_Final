from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

orders_blueprint = Blueprint("orders_blueprint", __name__, template_folder="templates")


@orders_blueprint.route('/orders')
def orders():
    id = session['id']
    user_type = session['user_type']
    if user_type == 'customer':
        orders = conn.execute(text("SELECT * FROM orders WHERE customer_id = :id").bindparams(id=id)).fetchall()
        products = conn.execute(text("SELECT o.order_id, opl.order_id, opl.variant_id, opl.quantity, p.title, p.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price FROM orders o JOIN order_product_lists opl ON o.order_id = opl.order_id JOIN product_variations pv ON opl.variant_id = pv.variant_id JOIN products p ON pv.product_id = p.product_id WHERE o.customer_id = :id").bindparams(id=id)).fetchall()
        return render_template('orders.html', orders=orders, products=products)
    elif user_type == 'vendor':
        orders = conn.execute(text("SELECT DISTINCT o.order_id, o.date, o.order_status FROM orders o JOIN order_product_lists opl ON o.order_id = opl.order_id JOIN product_variations pv ON opl.variant_id = pv.variant_id JOIN products p ON pv.product_id = p.product_id WHERE p.vendor_id = :id").bindparams(id=id)).fetchall()
        products = conn.execute(text("SELECT o.order_id, opl.order_id, opl.variant_id, opl.quantity, p.title, p.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price FROM orders o JOIN order_product_lists opl ON o.order_id = opl.order_id JOIN product_variations pv ON opl.variant_id = pv.variant_id JOIN products p ON pv.product_id = p.product_id WHERE p.vendor_id = :id").bindparams(id=id)).fetchall()
        return render_template('orders.html', orders=orders, products=products)
    

@orders_blueprint.route('/update_order_status', methods=['POST'])
def update_order_status():
    conn.execute(text("UPDATE orders SET order_status = :order_status WHERE order_id = :order_id").bindparams(order_id=request.form['order_id']), request.form)
    conn.commit()
    return redirect(url_for('orders_blueprint.orders'))


@orders_blueprint.route('/submit_review', methods=['POST'])
def submit_review():
    id = session['id']
    conn.execute(text("INSERT INTO reviews VALUES (:id, :product_id, :variant_id, curdate(), :rating, :description)").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('orders_blueprint.orders'))


@orders_blueprint.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    id = session['id']
    conn.execute(text("INSERT INTO complaints (customer_id, product_id, variant_id, complaint_title, complaint_description, demand, complaint_date, complaint_status) VALUES (:id, :product_id, :variant_id, :complaint_title, :complaint_description, :demand, curdate(), 'pending')").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('orders_blueprint.orders'))


# Tested and working
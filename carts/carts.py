from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

carts_blueprint = Blueprint("carts_blueprint", __name__, template_folder="templates")


@carts_blueprint.route('/cart')
def cart():
    id = session['id']
    cart = conn.execute(text("SELECT c.customer_id, c.product_id, c.variant_id, c.quantity, p.title, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM carts c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id WHERE customer_id = :id").bindparams(id=id)).fetchall()
    return render_template('cart.html', cart=cart)


@carts_blueprint.route('/update_cart', methods=['POST'])
def update_cart():
    id = session['id']
    conn.execute(text("UPDATE carts SET quantity = :quantity WHERE customer_id = :id AND variant_id = :variant_id").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('carts_blueprint.cart'))


@carts_blueprint.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    id = session['id']
    conn.execute(text("DELETE FROM carts WHERE customer_id = :id AND variant_id = :variant_id").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('carts_blueprint.cart'))


@carts_blueprint.route('/place_order', methods=['POST'])
def place_order():
    id = session['id']
    cart = conn.execute(text("SELECT * FROM carts WHERE customer_id = :id").bindparams(id=id))
    if cart.rowcount == 0:
        flash('Cart is empty!')
        return redirect(url_for('carts_blueprint.cart'))
    conn.execute(text("INSERT INTO orders (customer_id, price, date, order_status) VALUES (:id, :total, curdate(), 'pending');").bindparams(id=id), request.form)
    conn.commit()
    order_id = conn.execute(text("SELECT order_id FROM orders WHERE customer_id = :id ORDER BY order_id DESC LIMIT 1").bindparams(id=id)).fetchone()[0]
    conn.execute(text("INSERT INTO order_product_lists SELECT :order_id, variant_id, quantity FROM carts WHERE customer_id = :id").bindparams(order_id=order_id, id=id))
    conn.commit()
    conn.execute(text("UPDATE product_variations pv JOIN carts c ON pv.variant_id = c.variant_id SET pv.inventory_count = pv.inventory_count - c.quantity WHERE c.customer_id = :id").bindparams(id=id))
    conn.commit()
    conn.execute(text("DELETE FROM carts WHERE customer_id = :id").bindparams(id=id))
    conn.commit()
    return redirect(url_for('orders_blueprint.orders'))

# All tested and working
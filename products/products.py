from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

products_blueprint = Blueprint("products_blueprint", __name__, template_folder="templates")


@products_blueprint.route('/render_products')
def render_products():
    if 'id' in session:
        id = session['id']
    if 'user_type' in session:
        user_type = session['user_type']
        if user_type == 'vendor':
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
            return render_template('products.html', products=products)
        elif user_type == 'admin':
            vendors = conn.execute(text("SELECT username FROM users WHERE user_type='vendor'")).fetchall()
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
            return render_template('products.html', products=products, vendors=vendors)
        elif user_type == 'customer':
            categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
            colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
            sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id")).fetchall()
            return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)
    else:
        categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
        colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
        sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id")).fetchall()
        return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@products_blueprint.route('/filter_category', methods=['POST'])
def filter_category():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category=:filter_category"), request.form).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@products_blueprint.route('/filter_color', methods=['POST'])
def filter_color():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE pv.color=:filter_color"), request.form).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@products_blueprint.route('/filter_size', methods=['POST'])
def filter_size():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE pv.size=:filter_size"), request.form).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@products_blueprint.route('/filter_stock_status', methods=['POST'])
def filter_stock_status():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    if request.form['stock_status'] == 'in_stock':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE pv.inventory_count > 0")).fetchall()
        return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)
    elif request.form['stock_status'] == 'out_of_stock':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE pv.inventory_count = 0")).fetchall()
        return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)
    

@products_blueprint.route('/filter_search', methods=['POST'])
def filter_search():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    search_results = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON pv.product_id = p.product_id WHERE p.title LIKE :search OR p.description LIKE :search OR u.username LIKE :search"), {'search': f'%{request.form["search"]}%'})
    return render_template('products.html', products=search_results, categories=categories, colors=colors, sizes=sizes)


@products_blueprint.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    inventory_count = conn.execute(text("SELECT inventory_count FROM product_variations WHERE variant_id = :variant_id"), request.form).fetchone()[0]
    if inventory_count == 0:
        flash('Item out of stock')
        return redirect(url_for('products_blueprint.render_products'))
    id = session['id']
    result = conn.execute(text("SELECT * FROM carts WHERE customer_id = :id AND variant_id = :variant_id").bindparams(id=id), request.form)
    if result.rowcount == 1:
        flash('Item already in cart')
        return redirect(url_for('products_blueprint.render_products'))
    else:
        conn.execute(text("INSERT INTO carts (customer_id, product_id, variant_id, quantity) VALUES (:id, :product_id, :variant_id, :quantity)").bindparams(id=id), request.form)
        conn.commit()
        flash('Item added to cart')
        return redirect(url_for('products_blueprint.render_products'))
    

@products_blueprint.route('/add_product', methods=['POST'])
def add_product():
    id = session['id']
    user_type = session['user_type']
    discount = request.form['discount_price']
    discount_date = request.form['discount_end_date']
    if discount == '' or discount_date == '':
        discount = None
        discount_date = None
    if user_type == 'vendor':
        conn.execute(text("INSERT INTO products (vendor_id, title, category, description) VALUES (:id, :title, :category, :description)").bindparams(id=id), request.form)
        conn.commit()
    elif user_type == 'admin':
        vendor_id = conn.execute(text("SELECT user_id FROM users WHERE username = :username").bindparams(username=request.form['vendor_name'])).fetchone()[0]
        conn.execute(text("INSERT INTO products (vendor_id, title, category, description) VALUES (:vendor_id, :title, :category, :description)").bindparams(vendor_id=vendor_id), request.form)
        conn.commit()
    product_id = conn.execute(text("SELECT product_id FROM products WHERE title = :title").bindparams(title=request.form['title'])).fetchone()[0]
    conn.execute(text("INSERT INTO product_variations (product_id, image, size, color, price, discount_price, discount_end_date, inventory_count) VALUES (:product_id, :image, :size, :color, :price, :discount, :discount_date, :inventory_count)").bindparams(product_id=product_id, discount=discount, discount_date=discount_date), request.form)
    conn.commit()
    flash('Product added successfully')
    return redirect(url_for('products_blueprint.render_products'))


@products_blueprint.route('/add_variant', methods=['POST'])
def add_variant():
    id = session['id']
    discount = request.form['discount_price']
    discount_date = request.form['discount_end_date']
    if discount == '' or discount_date == '':
        discount = None
        discount_date = None
    product_id = request.form['product_id']
    valid_id = conn.execute(text("SELECT product_id FROM products WHERE product_id = :product_id").bindparams(product_id=product_id)).fetchone()
    if valid_id == None:
        flash('Invalid product id')
        return redirect(url_for('products_blueprint.render_products'))
    conn.execute(text("INSERT INTO product_variations (product_id, image, size, color, price, discount_price, discount_end_date, inventory_count) VALUES (:product_id, :image, :size, :color, :price, :discount, :discount_date, :inventory_count)").bindparams(discount=discount, discount_date=discount_date), request.form)
    conn.commit()
    flash('Variant added successfully')
    return redirect(url_for('products_blueprint.render_products'))



@products_blueprint.route('/update_product', methods=['POST'])
def update_product():
    id = session['id']
    product_id = request.form['product_id']
    valid_id = conn.execute(text("SELECT product_id FROM products WHERE product_id = :product_id").bindparams(product_id=product_id)).fetchone()
    if valid_id == None:
        flash('Invalid Product ID')
        return redirect(url_for('products_blueprint.render_products'))
    conn.execute(text("UPDATE products SET title = :title, category = :category, description = :description WHERE product_id = :product_id").bindparams(product_id=product_id), request.form)
    conn.commit()
    flash('Product updated successfully')
    return redirect(url_for('products_blueprint.render_products'))


@products_blueprint.route('/update_variant', methods=['POST'])
def update_variant():
    id = session['id']
    user_type = session['user_type']
    discount = request.form['discount_price']
    discount_date = request.form['discount_end_date']
    if discount == '' or discount_date == '':
        discount = None
        discount_date = None
    conn.execute(text("UPDATE product_variations SET image = :image, size = :size, color = :color, price = :price, discount_price = :discount, discount_end_date = :discount_date, inventory_count = :inventory_count WHERE variant_id = :variant_id").bindparams(discount=discount, discount_date=discount_date), request.form)
    conn.commit()
    flash('Variant updated successfully')
    return redirect(url_for('products_blueprint.render_products'))


@products_blueprint.route('/delete_product', methods=['POST'])
def delete_product():
    variant_id = request.form['variant_id']
    variant_in_cart = conn.execute(text("SELECT * FROM carts WHERE variant_id = :variant_id").bindparams(variant_id=variant_id))
    if variant_in_cart.rowcount > 0:
        flash('Product is in a cart')
        return redirect(url_for('products_blueprint.render_products'))
    variant_ordered = conn.execute(text("SELECT * FROM order_product_lists WHERE variant_id = :variant_id").bindparams(variant_id=variant_id))
    if variant_ordered.rowcount > 0:
        flash('Product has already been ordered')
        return redirect(url_for('products_blueprint.render_products'))
    conn.execute(text("DELETE FROM product_variations WHERE variant_id = :variant_id").bindparams(variant_id=variant_id))
    conn.commit()
    product_id = request.form['product_id']
    query = conn.execute(text("SELECT * FROM product_variations WHERE product_id = :product_id").bindparams(product_id=product_id))
    if query.rowcount == 0:
        conn.execute(text("DELETE FROM products WHERE product_id = :product_id").bindparams(product_id=product_id))
        conn.commit()
        return redirect(url_for('products_blueprint.render_products'))


# Need to carefully test again
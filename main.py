from flask import Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

app = Flask(__name__)

conn_str = "mysql://root:6D8D^nQYfZS*Wt@localhost/cset180_final"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

app.secret_key = os.urandom(24)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        session.clear()
        return render_template('home.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    else:
        email = request.form['email']
        query = conn.execute(text("select * from users where email = :email").bindparams(email=email))
        if query.rowcount == 1:
            return render_template('registration.html', message='E-mail already in use')
        username = request.form['username']
        query = conn.execute(text("select * from users where username = :username").bindparams(username=username))
        if query.rowcount == 1:
            return render_template('registration.html', message='Username already in use')
        conn.execute(text("INSERT INTO users (user_type, email, username, password, first_name, last_name) VALUES (:user_type, :email, :username, :password, :first_name, :last_name)"), request.form)
        conn.commit()
        return render_template('registration.html', message='Registration successful')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user = request.form['user']
        password = request.form['password']
        user_info = conn.execute(text("SELECT * FROM users WHERE username=:user OR email=:user").bindparams(user=user)).fetchone()
        if user_info:
            if conn.execute(text("SELECT password FROM users WHERE username=:user OR email=:user").bindparams(user=user)).fetchone()[0] == password:
                user_type = user_info.user_type
                if user_type == 'customer':
                    session['id'] = user_info.user_id
                    session['user_type'] = user_type
                    session['username'] = user_info.username
                    return render_template('my_account.html')
                elif user_type == 'vendor':
                    session['id'] = user_info.user_id
                    session['user_type'] = user_type
                    session['username'] = user_info.username
                    return redirect('render_products')
                elif user_type == 'admin':
                    session['id'] = user_info.user_id
                    session['user_type'] = user_type
                    session['username'] = user_info.username
                    return redirect('render_products')
            else:
                return render_template('login.html', message='Invalid password')
        else:
            return render_template('login.html', message='Invalid Username or E-mail')


@app.route('/render_products')
def render_products():
    id = session['id']
    user_type = session['user_type']
    if user_type == 'vendor':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
        return render_template('products.html', products=products)
    elif user_type == 'admin':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products)
    elif user_type == 'customer':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products)
    

@app.route('/add_product', methods=['POST'])
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
        conn.execute(text("INSERT INTO products (vendor_id, title, category, description) VALUES (:vendor_id, :title, :category, :description)"), request.form)
        conn.commit()
    product_id = conn.execute(text("SELECT product_id FROM products WHERE title = :title").bindparams(title=request.form['title'])).fetchone()[0]
    conn.execute(text("INSERT INTO product_variations (product_id, image, size, color, price, discount_price, discount_end_date, inventory_count) VALUES (:product_id, :image, :size, :color, :price, :discount, :discount_date, :inventory_count)").bindparams(product_id=product_id, discount=discount, discount_date=discount_date), request.form)
    conn.commit()
    if user_type == 'vendor':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
        return render_template('products.html', products=products, Message='Product added successfully')
    elif user_type == 'admin':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products, Message='Product added successfully')


@app.route('/add_variant', methods=['POST'])
def add_variant():
    id = session['id']
    user_type = session['user_type']
    discount = request.form['discount_price']
    discount_date = request.form['discount_end_date']
    if discount == '' or discount_date == '':
        discount = None
        discount_date = None
    product_id = request.form['product_id']
    valid_id = conn.execute(text("SELECT product_id FROM products WHERE product_id = :product_id").bindparams(product_id=product_id)).fetchone()
    if valid_id == None:
        if user_type == 'vendor':
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
            return render_template('products.html', products=products, Message='Invalid product id')
        elif user_type == 'admin':
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
            return render_template('products.html', products=products, Message='Invalid product id')
    conn.execute(text("INSERT INTO product_variations (product_id, image, size, color, price, discount_price, discount_end_date, inventory_count) VALUES (:product_id, :image, :size, :color, :price, :discount, :discount_date, :inventory_count)").bindparams(discount=discount, discount_date=discount_date), request.form)
    conn.commit()
    if user_type == 'vendor':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
        return render_template('products.html', products=products, Message='Product variant added successfully')
    elif user_type == 'admin':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products, Message='Product variant added successfully')


@app.route('/update_product', methods=['POST'])
def update_product():
    id = session['id']
    user_type = session['user_type']
    product_id = request.form['product_id']
    valid_id = conn.execute(text("SELECT product_id FROM products WHERE product_id = :product_id").bindparams(product_id=product_id)).fetchone()
    if valid_id == None:
        if user_type == 'vendor':
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
            return render_template('products.html', products=products, Message='Invalid product id')
        elif user_type == 'admin':
            products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
            return render_template('products.html', products=products, Message='Invalid product id')
    conn.execute(text("UPDATE products SET title = :title, category = :category, description = :description WHERE product_id = :product_id").bindparams(product_id=product_id), request.form)
    conn.commit()
    if user_type == 'vendor':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
        return render_template('products.html', products=products, Message='Product updated successfully')
    elif user_type == 'admin':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products, Message='Product updated successfully')


@app.route('/update_variant', methods=['POST'])
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
    if user_type == 'vendor':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
        return render_template('products.html', products=products, message='Product variant updated successfully')
    elif user_type == 'admin':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products, message='Product variant updated successfully')


@app.route('/delete_product', methods=['POST'])
def delete_product():
    id = session['id']
    user_type = session['user_type']
    conn.execute(text("DELETE FROM product_variations WHERE variant_id = :variant_id").bindparams(variant_id=request.form['variant_id']))
    conn.commit()
    query = conn.execute(text("SELECT * FROM product_variations WHERE product_id = :product_id").bindparams(product_id=request.form['product_id']))
    if query.rowcount == 0:
        conn.execute(text("DELETE FROM products WHERE product_id = :product_id").bindparams(product_id=request.form['product_id']))
        conn.commit()
    if user_type == 'vendor':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE vendor_id=:id;").bindparams(id=id)).fetchall()
        return render_template('products.html', products=products)
    elif user_type == 'admin':
        products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id;")).fetchall()
        return render_template('products.html', products=products)
    

@app.route('/my_account')
def my_account():
    return render_template('my_account.html')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    id = session['id']
    result = conn.execute(text("SELECT * FROM carts WHERE customer_id = :id AND variant_id = :variant_id").bindparams(id=id), request.form)
    if result.rowcount == 1:
        flash('Item already in cart')
        return redirect(url_for('render_products'))
    else:
        conn.execute(text("INSERT INTO carts (customer_id, product_id, variant_id, quantity) VALUES (:id, :product_id, :variant_id, :quantity)").bindparams(id=id), request.form)
        conn.commit()
        flash('Item added to cart')
        return redirect(url_for('render_products'))
    

@app.route('/cart')
def cart():
    id = session['id']
    cart = conn.execute(text("SELECT c.customer_id, c.product_id, c.variant_id, c.quantity, p.title, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date FROM carts c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id WHERE customer_id = :id").bindparams(id=id)).fetchall()
    return render_template('cart.html', cart=cart)


if __name__ == '__main__':
    app.run(debug=True)
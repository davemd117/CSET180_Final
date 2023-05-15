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
        print('Test')
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
        password = request.form['password']
        encrypted_password = hashlib.sha224(password.encode('utf-8')).hexdigest()
        conn.execute(text("INSERT INTO users (user_type, email, username, password, first_name, last_name) VALUES (:user_type, :email, :username, :encrypted_password, :first_name, :last_name)").bindparams(encrypted_password=encrypted_password), request.form)
        conn.commit()
        return render_template('registration.html', message='Registration successful')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user = request.form['user']
        password = request.form['password']
        encrypted_password = hashlib.sha224(password.encode('utf-8')).hexdigest()
        user_info = conn.execute(text("SELECT * FROM users WHERE username=:user OR email=:user").bindparams(user=user)).fetchone()
        if user_info:
            if conn.execute(text("SELECT password FROM users WHERE username=:user OR email=:user").bindparams(user=user)).fetchone()[0] == encrypted_password:
                user_type = user_info.user_type
                if user_type == 'customer':
                    session['id'] = user_info.user_id
                    session['user_type'] = user_type
                    session['username'] = user_info.username
                    return redirect('my_account')
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


@app.route('/filter_category', methods=['POST'])
def filter_category():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category=:filter_category"), request.form).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_category_gpu')
def filter_category_gpu():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='GPU'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_category_mobo')
def filter_category_mobo():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='Motherboard'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_category_ram')
def filter_category_ram():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='RAM'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_category_case')
def filter_category_case():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.product_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE p.category='Case'")).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_color', methods=['POST'])
def filter_color():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE pv.color=:filter_color"), request.form).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_size', methods=['POST'])
def filter_size():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    products = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON p.product_id = pv.product_id WHERE pv.size=:filter_size"), request.form).fetchall()
    return render_template('products.html', products=products, categories=categories, colors=colors, sizes=sizes)


@app.route('/filter_stock_status', methods=['POST'])
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
    

@app.route('/filter_search', methods=['POST'])
def filter_search():
    categories = conn.execute(text("SELECT DISTINCT category FROM products")).fetchall()
    colors = conn.execute(text("SELECT DISTINCT color FROM product_variations")).fetchall()
    sizes = conn.execute(text("SELECT DISTINCT size FROM product_variations")).fetchall()
    search_results = conn.execute(text("SELECT u.user_id, u.username, p.product_id, p.vendor_id, p.title, p.category, p.description, pv.variant_id, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM users u JOIN products p ON u.user_id = p.vendor_id JOIN product_variations pv ON pv.product_id = p.product_id WHERE p.title LIKE :search OR p.description LIKE :search OR u.username LIKE :search"), {'search': f'%{request.form["search"]}%'})
    return render_template('products.html', products=search_results, categories=categories, colors=colors, sizes=sizes)

    

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
        vendor_id = conn.execute(text("SELECT user_id FROM users WHERE username = :username").bindparams(username=request.form['vendor_name'])).fetchone()[0]
        conn.execute(text("INSERT INTO products (vendor_id, title, category, description) VALUES (:vendor_id, :title, :category, :description)").bindparams(vendor_id=vendor_id), request.form)
        conn.commit()
    product_id = conn.execute(text("SELECT product_id FROM products WHERE title = :title").bindparams(title=request.form['title'])).fetchone()[0]
    conn.execute(text("INSERT INTO product_variations (product_id, image, size, color, price, discount_price, discount_end_date, inventory_count) VALUES (:product_id, :image, :size, :color, :price, :discount, :discount_date, :inventory_count)").bindparams(product_id=product_id, discount=discount, discount_date=discount_date), request.form)
    conn.commit()
    flash('Product added successfully')
    return redirect(url_for('render_products'))


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
    variant_id = request.form['variant_id']
    variant_in_cart = conn.execute(text("SELECT * FROM carts WHERE variant_id = :variant_id").bindparams(variant_id=variant_id))
    if variant_in_cart.rowcount > 0:
        flash('Product is in a cart')
        return redirect(url_for('render_products'))
    variant_ordered = conn.execute(text("SELECT * FROM order_product_lists WHERE variant_id = :variant_id").bindparams(variant_id=variant_id))
    if variant_ordered.rowcount > 0:
        flash('Product has already been ordered')
        return redirect(url_for('render_products'))
    conn.execute(text("DELETE FROM product_variations WHERE variant_id = :variant_id").bindparams(variant_id=variant_id))
    conn.commit()
    product_id = request.form['product_id']
    query = conn.execute(text("SELECT * FROM product_variations WHERE product_id = :product_id").bindparams(product_id=product_id))
    if query.rowcount == 0:
        conn.execute(text("DELETE FROM products WHERE product_id = :product_id").bindparams(product_id=product_id))
        conn.commit()
    return redirect(url_for('render_products'))

@app.route('/my_account')
def my_account():
    id = session['id']
    user_info = conn.execute(text("SELECT * FROM users WHERE user_id = :id").bindparams(id=id)).fetchone()
    return render_template('my_account.html', user_info=user_info)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    inventory_count = conn.execute(text("SELECT inventory_count FROM product_variations WHERE variant_id = :variant_id"), request.form).fetchone()[0]
    if inventory_count == 0:
        flash('Item out of stock')
        return redirect(url_for('render_products'))
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
    cart = conn.execute(text("SELECT c.customer_id, c.product_id, c.variant_id, c.quantity, p.title, pv.image, pv.size, pv.color, pv.price, pv.discount_price, pv.discount_end_date, pv.inventory_count FROM carts c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id WHERE customer_id = :id").bindparams(id=id)).fetchall()
    return render_template('cart.html', cart=cart)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    id = session['id']
    conn.execute(text("UPDATE carts SET quantity = :quantity WHERE customer_id = :id AND variant_id = :variant_id").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('cart'))


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    id = session['id']
    conn.execute(text("DELETE FROM carts WHERE customer_id = :id AND variant_id = :variant_id").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('cart'))


@app.route('/place_order', methods=['POST'])
def place_order():
    id = session['id']
    cart = conn.execute(text("SELECT * FROM carts WHERE customer_id = :id").bindparams(id=id))
    if cart.rowcount == 0:
        flash('Cart is empty!')
        return redirect(url_for('cart'))
    conn.execute(text("INSERT INTO orders (customer_id, price, date, order_status) VALUES (:id, :total, curdate(), 'pending');").bindparams(id=id), request.form)
    conn.commit()
    order_id = conn.execute(text("SELECT order_id FROM orders WHERE customer_id = :id ORDER BY order_id DESC LIMIT 1").bindparams(id=id)).fetchone()[0]
    conn.execute(text("INSERT INTO order_product_lists SELECT :order_id, variant_id, quantity FROM carts WHERE customer_id = :id").bindparams(order_id=order_id, id=id))
    conn.commit()
    conn.execute(text("UPDATE product_variations pv JOIN carts c ON pv.variant_id = c.variant_id SET pv.inventory_count = pv.inventory_count - c.quantity WHERE c.customer_id = :id").bindparams(id=id))
    conn.commit()
    conn.execute(text("DELETE FROM carts WHERE customer_id = :id").bindparams(id=id))
    conn.commit()
    return redirect(url_for('orders'))


@app.route('/orders')
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
    

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    conn.execute(text("UPDATE orders SET order_status = :order_status WHERE order_id = :order_id").bindparams(order_id=request.form['order_id']), request.form)
    conn.commit()
    return redirect(url_for('orders'))


@app.route('/submit_review', methods=['POST'])
def submit_review():
    id = session['id']
    conn.execute(text("INSERT INTO reviews VALUES (:id, :product_id, :variant_id, curdate(), :rating, :description)").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('orders'))


@app.route('/reviews')
def reviews():
    reviews = conn.execute(text("SELECT p.title, pv.size, pv.color, pv.image, u.first_name, u.last_name, r.rating, r.review_date, r.description FROM reviews r JOIN products p ON r.product_id = p.product_id JOIN product_variations pv ON r.variant_id = pv.variant_id JOIN users u ON r.customer_id = u.user_id")).fetchall()
    return render_template('reviews.html', reviews=reviews)


@app.route('/filter_rating' , methods=['POST'])
def filter_rating():
    rating_filter = request.form['rating_filter']
    if rating_filter == 'high':
        reviews = conn.execute(text("SELECT p.title, pv.size, pv.color, pv.image, u.first_name, u.last_name, r.rating, r.review_date, r.description FROM reviews r JOIN products p ON r.product_id = p.product_id JOIN product_variations pv ON r.variant_id = pv.variant_id JOIN users u ON r.customer_id = u.user_id ORDER BY r.rating DESC")).fetchall()
        return render_template('reviews.html', reviews=reviews)
    elif rating_filter == 'low':
        reviews = conn.execute(text("SELECT p.title, pv.size, pv.color, pv.image, u.first_name, u.last_name, r.rating, r.review_date, r.description FROM reviews r JOIN products p ON r.product_id = p.product_id JOIN product_variations pv ON r.variant_id = pv.variant_id JOIN users u ON r.customer_id = u.user_id ORDER BY r.rating ASC")).fetchall()
        return render_template('reviews.html', reviews=reviews)


@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    id = session['id']
    conn.execute(text("INSERT INTO complaints (customer_id, product_id, variant_id, complaint_title, complaint_description, demand, complaint_date, complaint_status) VALUES (:id, :product_id, :variant_id, :complaint_title, :complaint_description, :demand, curdate(), 'pending')").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('orders'))


@app.route('/complaints')
def complaints():
    id = session['id']
    user_type = session['user_type']
    if user_type == 'customer':
        complaints = conn.execute(text("SELECT u.first_name, u.last_name, c.complaint_title, c.demand, c.complaint_date, c.complaint_status, p.title, pv.image, pv.size, pv.color, c.complaint_description FROM complaints c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id JOIN users u ON c.customer_id = u.user_id WHERE c.customer_id=:id").bindparams(id=id)).fetchall()
        return render_template('complaints.html', complaints=complaints)
    elif user_type == 'admin':
        complaints = conn.execute(text("SELECT u.first_name, u.last_name, c.complaint_id, c.complaint_title, c.demand, c.complaint_date, c.complaint_status, p.title, pv.image, pv.size, pv.color, c.complaint_description FROM complaints c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id JOIN users u ON c.customer_id = u.user_id")).fetchall()
        return render_template('complaints.html', complaints=complaints)
    

@app.route('/update_complaint_status', methods=['POST'])
def update_complaint_status():
    conn.execute(text("UPDATE complaints SET complaint_status = :complaint_status WHERE complaint_id = :complaint_id"), request.form)
    conn.commit()
    return redirect(url_for('complaints'))


@app.route('/chat')
def chat():
    id = session['id']
    if session['user_type'] == 'customer':
        vendors = conn.execute(text("SELECT user_id, username FROM users WHERE user_type = 'vendor'")).fetchall()
        admins = conn.execute(text("SELECT user_id, username FROM users WHERE user_type = 'admin'")).fetchall()
        chat_threads = conn.execute(text("SELECT c.vendor_admin_id, c.thread_title, u.username FROM chat_threads c JOIN users u ON vendor_admin_id = user_id WHERE customer_id=:id").bindparams(id=id)).fetchall()
        chats = conn.execute(text("SELECT * FROM chat_messages WHERE sender_id=:id OR recipient_id=:id").bindparams(id=id)).fetchall()
        return render_template('chat.html', chat_threads=chat_threads, chats=chats, vendors=vendors, admins=admins)
    elif session['user_type'] == 'vendor' or session['user_type'] == 'admin':
        chat_threads = conn.execute(text("SELECT c.customer_id, c.thread_title, u.username FROM chat_threads c JOIN users u ON customer_id = user_id WHERE vendor_admin_id=:id").bindparams(id=id)).fetchall()
        chats = conn.execute(text("SELECT * FROM chat_messages WHERE sender_id=:id OR recipient_id=:id").bindparams(id=id)).fetchall()
        return render_template('chat.html', chat_threads=chat_threads, chats=chats)


@app.route('/create_thread_customer', methods=['POST'])
def create_chat_customer():
    id = session['id']
    vendor_admin_id = request.form['vendor_admin_id']
    existing_thread = conn.execute(text("SELECT * FROM chat_threads WHERE customer_id=:id AND vendor_admin_id=:vendor_admin_id").bindparams(id=id, vendor_admin_id=vendor_admin_id))
    if existing_thread.rowcount == 1:
        flash('Chat already exists')
        return redirect(url_for('chat'))
    conn.execute(text("INSERT INTO chat_threads (customer_id, vendor_admin_id, thread_title) VALUES (:id, :vendor_admin_id, :thread_title)").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('chat'))


@app.route('/send_message', methods=['POST'])
def send_message_customer():
    id = session['id']
    conn.execute(text("INSERT INTO chat_messages (sender_id, recipient_id, message) VALUES (:id, :recipient_id, :message)").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('chat'))


if __name__ == '__main__':
    app.run(debug=True)
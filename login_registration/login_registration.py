from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

login_registration_blueprint = Blueprint("login_registration_blueprint", __name__, template_folder="templates")


@login_registration_blueprint.route('/registration', methods=['GET', 'POST'])
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


@login_registration_blueprint.route('/login', methods=['GET', 'POST'])
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
        

@login_registration_blueprint.route('/my_account')
def my_account():
    id = session['id']
    user_info = conn.execute(text("SELECT * FROM users WHERE user_id = :id").bindparams(id=id)).fetchone()
    return render_template('my_account.html', user_info=user_info)
from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

chats_blueprint = Blueprint("chats_blueprint", __name__, template_folder="templates")


@chats_blueprint.route('/chat')
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


@chats_blueprint.route('/create_thread_customer', methods=['POST'])
def create_chat_customer():
    id = session['id']
    vendor_admin_id = request.form['vendor_admin_id']
    existing_thread = conn.execute(text("SELECT * FROM chat_threads WHERE customer_id=:id AND vendor_admin_id=:vendor_admin_id").bindparams(id=id, vendor_admin_id=vendor_admin_id))
    if existing_thread.rowcount == 1:
        flash('Chat already exists')
        return redirect(url_for('chats_blueprint.chat'))
    conn.execute(text("INSERT INTO chat_threads (customer_id, vendor_admin_id, thread_title) VALUES (:id, :vendor_admin_id, :thread_title)").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('chats_blueprint.chat'))


@chats_blueprint.route('/send_message', methods=['POST'])
def send_message_customer():
    id = session['id']
    conn.execute(text("INSERT INTO chat_messages (sender_id, recipient_id, message) VALUES (:id, :recipient_id, :message)").bindparams(id=id), request.form)
    conn.commit()
    return redirect(url_for('chats_blueprint.chat'))


# Tested and working

from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

complaints_blueprint = Blueprint("complaints_blueprint", __name__, template_folder="templates")


@complaints_blueprint.route('/complaints')
def complaints():
    id = session['id']
    user_type = session['user_type']
    if user_type == 'customer':
        complaints = conn.execute(text("SELECT u.first_name, u.last_name, c.complaint_title, c.demand, c.complaint_date, c.complaint_status, p.title, pv.image, pv.size, pv.color, c.complaint_description FROM complaints c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id JOIN users u ON c.customer_id = u.user_id WHERE c.customer_id=:id").bindparams(id=id)).fetchall()
        return render_template('complaints.html', complaints=complaints)
    elif user_type == 'admin':
        complaints = conn.execute(text("SELECT u.first_name, u.last_name, c.complaint_id, c.complaint_title, c.demand, c.complaint_date, c.complaint_status, p.title, pv.image, pv.size, pv.color, c.complaint_description FROM complaints c JOIN products p ON c.product_id = p.product_id JOIN product_variations pv ON c.variant_id = pv.variant_id JOIN users u ON c.customer_id = u.user_id")).fetchall()
        return render_template('complaints.html', complaints=complaints)
    

@complaints_blueprint.route('/update_complaint_status', methods=['POST'])
def update_complaint_status():
    conn.execute(text("UPDATE complaints SET complaint_status = :complaint_status WHERE complaint_id = :complaint_id"), request.form)
    conn.commit()
    return redirect(url_for('complaints_blueprint.complaints'))


# Tested and working
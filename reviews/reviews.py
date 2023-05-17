from flask import Blueprint, Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib

from db import conn

reviews_blueprint = Blueprint("reviews_blueprint", __name__, template_folder="templates")


@reviews_blueprint.route('/reviews')
def reviews():
    reviews = conn.execute(text("SELECT p.title, pv.size, pv.color, pv.image, u.first_name, u.last_name, r.rating, r.review_date, r.description FROM reviews r JOIN products p ON r.product_id = p.product_id JOIN product_variations pv ON r.variant_id = pv.variant_id JOIN users u ON r.customer_id = u.user_id")).fetchall()
    return render_template('reviews.html', reviews=reviews)


@reviews_blueprint.route('/filter_rating' , methods=['POST'])
def filter_rating():
    rating_filter = request.form['rating_filter']
    if rating_filter == 'high':
        reviews = conn.execute(text("SELECT p.title, pv.size, pv.color, pv.image, u.first_name, u.last_name, r.rating, r.review_date, r.description FROM reviews r JOIN products p ON r.product_id = p.product_id JOIN product_variations pv ON r.variant_id = pv.variant_id JOIN users u ON r.customer_id = u.user_id ORDER BY r.rating DESC")).fetchall()
        return render_template('reviews.html', reviews=reviews)
    elif rating_filter == 'low':
        reviews = conn.execute(text("SELECT p.title, pv.size, pv.color, pv.image, u.first_name, u.last_name, r.rating, r.review_date, r.description FROM reviews r JOIN products p ON r.product_id = p.product_id JOIN product_variations pv ON r.variant_id = pv.variant_id JOIN users u ON r.customer_id = u.user_id ORDER BY r.rating ASC")).fetchall()
        return render_template('reviews.html', reviews=reviews)
    

# Seems to be workig fine now, tested and working.
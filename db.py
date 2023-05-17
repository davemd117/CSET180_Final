from flask import Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import os
import hashlib
conn_str = "mysql://root:6D8D^nQYfZS*Wt@localhost/cset180_final"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()
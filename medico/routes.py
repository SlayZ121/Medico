from medico import app
from flask import render_template, redirect, url_for, flash, request



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('./templates/home.html')

@app.route('/about')
def about_page():
    return render_template('./templates/about.html')

@app.route('/contact')
def contact_page():
    return render_template('./templates/contact.html')

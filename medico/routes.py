from medico import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from .mailkey import mailkey
from medico.models import User
from medico import db
from flask_login import login_user, logout_user, login_required, current_user

app.secret_key = 'your_secret_key'  # Add your secret key here

otp = randint(1000, 9999)

def send_otp(email):
    sender_email = 'slayz9168@gmail.com'
    receiver_email = email
    password = mailkey

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Your OTP'

    message.attach(MIMEText(f'Your OTP is: {otp}', 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/otp')
def otp_page():
    return render_template('otp.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        session['role'] = request.form['role']
        return redirect(url_for('verify'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        attempted_user = User.query.filter_by(email_address=request.form['email']).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=request.form['password']
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password do not match! Please try again', category='danger')
    return render_template('login.html')

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/verify')
def verify():
    email = session.get('email')
    if email and send_otp(email):
        flash('OTP has been sent to your email', category='info')
        return render_template('otp.html')
    else:
        flash('Failed to send OTP. Please try again.', category='danger')
        return redirect(url_for('signup_page'))

@app.route('/validate', methods=['POST'])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        username = session.get('username')
        email_address = session.get('email')
        password = session.get('password')
        role = session.get('role')
        
        if username and email_address and password and role:
            user_to_create = User(username=username,
                                  email_address=email_address,
                                  password=password,
                                  role=role)
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
            session.pop('username', None)
            session.pop('email', None)
            session.pop('password', None)
            session.pop('role', None)
            return redirect(url_for('home_page'))
        else:
            flash('Session expired or invalid data. Please try signing up again.', category='danger')
            return redirect(url_for('signup_page'))
    else:
        flash('Invalid OTP. Please try again.', category='danger')
        return render_template('otp.html')

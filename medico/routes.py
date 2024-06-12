from medico import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from .mailkey import mailkey,secretkey
from medico.models import User, Appointment
from medico import db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date, time
from flask import Blueprint, request, jsonify, render_template
import google.generativeai as genai


bp = Blueprint('routes', __name__)

genai.configure(api_key=secretkey)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

system_instruction = "Friendly"

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)

def run_chat(message):
    convo = model.start_chat(history=[
        {
            "role": "user",
            "parts": ["You are Medico Bot, a friendly assistant..."]  # Your initial instruction
        }
    ])
    convo.send_message(message)
    return convo.last.text




app.secret_key = 'your_secret_key'  # Add your secret key here

otp = randint(1000, 9999)

def send_otp(email):
    sender_email = 'medicohealthorg@gmail.com'
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

@bp.route('/chatbot', methods=['POST'])
def chatbot():
    if request.method == 'POST':
        data = request.json
        message = data.get("message")
        response = run_chat(message)
        return jsonify({'message': message, 'response': response})

@bp.route('/index')
def index():
    return render_template('chatbot.html')


@app.route('/my-appointments')
@login_required
def my_appointments():
    appointments = Appointment.query.filter_by(user_id=current_user.id).all()

    
    return render_template('appointment1.html', appointments=appointments)


@app.route('/bmi')
@login_required
def bmi_page():
    return render_template('bmi.html')
@app.route('/aptcheck')
@login_required
def aptcheck_page():
    return render_template('appointment0.html')

@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment_page():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        date_str = request.form['date']
        time_str = request.form['time']
        doctor_id = request.form['doctor_id']

        # Convert date and time from string to date and time objects
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time_str, '%H:%M').time()

        # Assume you have a way to get the user_id of the logged-in user
        user_id = current_user.id

        # Create a new appointment
        new_appointment = Appointment(
            name=name,
            phone=phone,
            email=email,
            date=appointment_date,
            time=appointment_time,
            doctor_id=doctor_id,
            user_id=user_id
        )

        # Add to the database
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('home_page'))

    return render_template('appointment.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        session['role'] = request.form['role']
        username = session.get('username')
        email_address = session.get('email')
        password = session.get('password')
        role = session.get('role')
        if username and email_address and password and role:
            
            existing_user = User.query.filter((User.username == username) | (User.email_address == email_address)).first()
            if existing_user:
                flash('A user with the same username or email already exists. Please try signing up with a different username or email.', category='danger')
                return redirect(url_for('signup_page'))
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
        flash('Invalid OTP. Please try again.', category='danger')
        return render_template('otp.html')

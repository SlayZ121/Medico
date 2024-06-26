from medico import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from .mailkey import mailkey, secretkey
from medico.models import User, Appointment, ModifiedSchedule
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
            "parts": ["You are Medico Bot, a friendly assistant for the Medico Web Application. that has exciting features like booking appointments, checking schedule, giving complaint, chatbot of course that is yourself, BMI calculator, and a dietary recommender. You assist users with our website. but you don't reply long messages you reply short and sweet and precise. The creators of this web application are Dhanalakshmi Dhanapal, Aarthi Honguthi, and Sriram Reddy"]
        }
    ])
    convo.send_message(message)
    return convo.last.text

app.secret_key = secretkey

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

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    message = data.get("message")
    response = run_chat(message)
    return jsonify({'message': message, 'response': response})

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


@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule_page():
    doctors = User.query.filter_by(role='medical_staff').all()
    return render_template('scheduler.html', doctors=doctors)

@app.route('/modify-schedule/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def modify_schedule(doctor_id):
    doctor = User.query.get_or_404(doctor_id)

    if request.method == 'POST':
        date_str = request.form['date']
        from_time = request.form['from_time']
        to_time = request.form['to_time']
        admin_email = 'slayz9168@gmail.com'  # Replace with actual admin email

        # Generate OTP and store it in session
        otp = randint(1000, 9999)
        session['otp'] = otp
        session['doctor_id'] = doctor_id
        session['date_str'] = date_str
        session['from_time'] = from_time
        session['to_time'] = to_time

        # Send email to admin with modification request and OTP
        subject = "Schedule Modification Request"
        body = f"""
        <html>
        <body>
            <p>Dear Admin,</p>
            <p>The following modification request has been submitted by {doctor.username}:</p>
            <table border="1" cellpadding="10" cellspacing="0">
                <tr>
                    <td><strong>Doctor Name:</strong></td>
                    <td>{doctor.username}</td>
                </tr>
                <tr>
                    <td><strong>Date:</strong></td>
                    <td>{date_str}</td>
                </tr>
                <tr>
                    <td><strong>From Time:</strong></td>
                    <td>{from_time}</td>
                </tr>
                <tr>
                    <td><strong>To Time:</strong></td>
                    <td>{to_time}</td>
                </tr>
            </table>
            <p>Please verify and confirm the changes.</p>
            <p>OTP for verification: {otp}</p>
        </body>
        </html>
        """

        sender_email = 'medicohealthorg@gmail.com'
        receiver_email = admin_email
        password = mailkey

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            flash('Your modification request has been sent successfully! Please check your email for OTP.', 'success')
            return redirect(url_for('otp_verification_modify'))
        except Exception as e:
            flash(f'Failed to send modification request. Error: {e}', 'danger')

    return render_template('modify.html', doctor=doctor)

@app.route('/otp-verification-modify', methods=['GET', 'POST'])
@login_required
def otp_verification_modify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        stored_otp = session.get('otp')
        doctor_id = session.get('doctor_id')
        date_str = session.get('date_str')
        from_time = session.get('from_time')
        to_time = session.get('to_time')

        if stored_otp and int(entered_otp) == stored_otp:
            # OTP verified successfully, save modification in the database
            new_schedule = ModifiedSchedule(
                doctor_id=doctor_id,
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                from_time=datetime.strptime(from_time, '%H:%M').time(),
                to_time=datetime.strptime(to_time, '%H:%M').time()
            )
            db.session.add(new_schedule)
            db.session.commit()
            
            session.pop('otp', None)
            session.pop('doctor_id', None)
            session.pop('date_str', None)
            session.pop('from_time', None)
            session.pop('to_time', None)
            
            flash('OTP verification successful! Schedule modified.', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')

    return render_template('otp_verify.html')

@app.route('/api/get-modified-schedule')
def get_modified_schedule():
    doctor_name = request.args.get('doctor_name')
    date_str = request.args.get('date')

    doctor = User.query.filter_by(username=doctor_name).first()
    if doctor:
        modified_schedule = ModifiedSchedule.query.filter_by(doctor_id=doctor.id, date=datetime.strptime(date_str, '%Y-%m-%d').date()).first()
        if modified_schedule:
            return jsonify({
                'exists': True,
                'from_time': modified_schedule.from_time.strftime('%H:%M'),
                'to_time': modified_schedule.to_time.strftime('%H:%M')
            })

    return jsonify({'exists': False})

@app.route('/medicalrecord')
@login_required
def medrecord_page():
    return render_template('records.html')


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

        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time_str, '%H:%M').time()

        user_id = current_user.id

        new_appointment = Appointment(
            name=name,
            phone=phone,
            email=email,
            date=appointment_date,
            time=appointment_time,
            doctor_id=doctor_id,
            user_id=user_id
        )

        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('home_page'))

    return render_template('appointment.html')

@app.route('/complaint', methods=['GET', 'POST'])
@login_required
def complaint_page():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        hostel = request.form['hostel']
        category = request.form['category']
        details = request.form['subject']

        subject = "New Complaint Received"
        body = f"""
        <html>
        <body>
            <table border="1" cellpadding="10" cellspacing="0">
                <tr>
                    <td><strong>Name:</strong></td>
                    <td>{name}</td>
                </tr>
                <tr>
                    <td><strong>Phone:</strong></td>
                    <td>{phone}</td>
                </tr>
                <tr>
                    <td><strong>Hostel:</strong></td>
                    <td>{hostel}</td>
                </tr>
                <tr>
                    <td><strong>Category:</strong></td>
                    <td>{category}</td>
                </tr>
                <tr>
                    <td><strong>Details:</strong></td>
                    <td>{details}</td>
                </tr>
            </table>
        </body>
        </html>
        """

        sender_email = 'medicohealthorg@gmail.com'
        receiver_email = 'slayz9168@gmail.com'
        password = mailkey

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            flash('Your complaint has been sent successfully!', 'success')
        except Exception as e:
            flash(f'Failed to send complaint. Error: {e}', 'danger')

        return redirect(url_for('home_page'))
    return render_template('complaint.html')

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
        if role == 'medical_staff':
            return redirect(url_for('verify', admin=True))
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
    role = session.get('role')
    if role == 'medical_staff':
        email = 'slayz9168@gmail.com'  # Send OTP to admin for medical staff role
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

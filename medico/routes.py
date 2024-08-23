from medico import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from .mailkey import mailkey, secretkey
from medico.models import User, Appointment, ModifiedSchedule,MedicalRecord,Pill
from medico import db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date, time
from flask import Blueprint, request, jsonify, render_template
import google.generativeai as genai
from random import uniform as rnd
import pandas as pd

# Assuming get_images_links is a function from ImageFinder module that fetches image links
from .ImageFinder import get_images_links as find_image

bp = Blueprint('routes', __name__)

recipes_df = pd.read_csv(r'C:\medicobtp\medico\recipes.csv')

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


class Generator:
    def __init__(self, nutrition_input: list):
        self.nutrition_input = nutrition_input

    def generate(self):
        # Use the recipes dataset to generate recipes
        sample_recipes = recipes_df.sample(n=3).to_dict(orient='records')  # Sample 3 recipes
        for recipe in sample_recipes:
            recipe['Calories'] = recipe['Calories']
            recipe['image_link'] = find_image(recipe['Name'])
            # Include recipe instructions and nutritional content
            recipe['Instructions'] = recipe['RecipeInstructions']
            recipe['Nutrients'] = {
                'Calories': recipe['Calories'],
                'Fat Content': recipe['FatContent'],
                'Saturated Fat Content': recipe['SaturatedFatContent'],
                'Cholesterol Content': recipe['CholesterolContent'],
                'Sodium Content': recipe['SodiumContent'],
                'Carbohydrate Content': recipe['CarbohydrateContent'],
                'Fiber Content': recipe['FiberContent'],
                'Sugar Content': recipe['SugarContent'],
                'Protein Content': recipe['ProteinContent']
            }
        return {"output": sample_recipes}

class Person:
    def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.meals_calories_perc = meals_calories_perc
        self.weight_loss = weight_loss

    def calculate_bmi(self):
        bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        return bmi

    def display_result(self):
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            category = 'Underweight'
            color = 'Red'
        elif 18.5 <= bmi < 25:
            category = 'Normal'
            color = 'Green'
        elif 25 <= bmi < 30:
            category = 'Overweight'
            color = 'Yellow'
        else:
            category = 'Obesity'
            color = 'Red'
        return bmi, category, color

    def calculate_bmr(self):
        if self.gender == 'Male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr

    def calories_calculator(self):
        activities = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight = weights[activities.index(self.activity)]
        maintain_calories = self.calculate_bmr() * weight
        return maintain_calories

    def generate_recommendations(self):
        total_calories = self.weight_loss * self.calories_calculator()
        recommendations = []
        for meal in self.meals_calories_perc:
            meal_calories = self.meals_calories_perc[meal] * total_calories
            recommended_nutrition = [
                meal_calories, rnd(10, 40), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75), rnd(4, 20), rnd(0, 10), rnd(30, 175)
            ]
            generator = Generator(recommended_nutrition)
            recommended_recipes = generator.generate()['output']
            for recipe in recommended_recipes:
                recipe['image_link'] = find_image(recipe['Name'])
            recommendations.append(recommended_recipes)
        return recommendations

@app.route('/diet', methods=['GET', 'POST'])
@login_required
def diet():
    if request.method == 'POST':
        age = int(request.form.get('age'))
        height = int(request.form.get('height'))
        weight = int(request.form.get('weight'))
        gender = request.form.get('gender')
        activity = request.form.get('activity')
        weight_loss_option = request.form.get('weight_loss_option')
        number_of_meals = int(request.form.get('number_of_meals'))

        plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
        weights = [1, 0.9, 0.8, 0.6]
        weight_loss = weights[plans.index(weight_loss_option)]

        if number_of_meals == 3:
            meals_calories_perc = {'breakfast': 0.35, 'lunch': 0.40, 'dinner': 0.25}
        elif number_of_meals == 4:
            meals_calories_perc = {'breakfast': 0.30, 'morning snack': 0.05, 'lunch': 0.40, 'dinner': 0.25}
        else:
            meals_calories_perc = {'breakfast': 0.30, 'morning snack': 0.05, 'lunch': 0.40, 'afternoon snack': 0.05, 'dinner': 0.20}

        person = Person(age, height, weight, gender, activity, meals_calories_perc, weight_loss)
        bmi, category, color = person.display_result()
        maintain_calories = person.calories_calculator()

        recommendations = person.generate_recommendations()
        return render_template('results.html', bmi=bmi, category=category, color=color, maintain_calories=maintain_calories,
                               weight_loss_option=weight_loss_option, recommendations=recommendations)
    return render_template('index.html')

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
     if current_user.role == 'medical_staff':
        
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
     else:
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

@app.route('/medicalrecord', methods=['GET', 'POST'])
def medicalrecord_page():
    if request.method == 'POST':
        name = request.form['named']
        roll_number = request.form['rollnod']
        phone_number = request.form['phoned']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        hostel = request.form['hostel']
        pills = request.form['pills']
        complaint = request.form['subject']

        new_record = MedicalRecord(
            name=name,
            roll_number=roll_number,
            phone_number=phone_number,
            date=date,
            hostel=hostel,
            pills=pills,
            complaint=complaint
        )
        
        try:
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('medicalrecord_page'))
        except Exception as e:
            flash('There was an issue adding your record')

    records = MedicalRecord.query.all()
    return render_template('records.html', records=records)
@app.route('/filtermedrecord', methods=['GET', 'POST'])
@login_required
def filter_medical():
    if request.method == 'POST':
        roll_number = request.form.get('rollNumber')
        hostel = request.form.get('hostel')
        date_str = request.form.get('date')

        if not (roll_number or hostel or date_str):
            return redirect(url_for('medicalrecord_page'))

        query = MedicalRecord.query

        if roll_number:
            query = query.filter_by(roll_number=roll_number)

        if hostel and hostel != "----":
            query = query.filter_by(hostel=hostel)

        if date_str:
            try:
                appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter_by(date=appointment_date)
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('medicalrecord_page'))

        records = query.all()
        return render_template('records.html', records=records)

    # Handle GET request if needed (though POST is expected for filtering)
    return redirect(url_for('medicalrecord_page'))


@app.route('/pillrecord')
@login_required
def pill_page():
    return render_template('pillmaintenance.html')
@app.route('/add_pill', methods=['POST','GET'])
def add_pill():
    name = request.form.get('name')
    category = request.form.get('category')
    quantity = int(request.form.get('quantity'))
    expiry_date_input = request.form.get('date')

    expiry_dates = []

    if expiry_date_input:
        expiry_date = datetime.strptime(expiry_date_input, '%Y-%m-%d').date()
        expiry_dates.append(expiry_date.strftime('%Y-%m-%d'))

    pill = Pill.query.filter_by(name=name, category=category).first()

    if pill:
        pill.quantity += quantity
        
        if expiry_dates:
            if pill.expiry_dates is None:
                pill.expiry_dates = []

            for date_str in expiry_dates:
                if date_str not in pill.expiry_dates:
                    pill.expiry_dates.append(date_str)

        db.session.commit()
        flash('Pill quantity updated and new expiry date added successfully!', 'success')
    else:
        new_pill = Pill(name=name, category=category, quantity=quantity, expiry_dates=expiry_dates)
        db.session.add(new_pill)
        db.session.commit()
        flash('New pill added successfully!', 'success')

    return redirect(url_for('pill_page'))


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

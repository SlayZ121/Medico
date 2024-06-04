from medico import app
from flask import render_template, redirect, url_for, flash, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
from .mailkey import mailkey


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

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/otp')
def otp_page():
    return render_template('otp.html')




@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # form = LoginForm()
    # if form.validate_on_submit():
    #     attempted_user = User.query.filter_by(username=form.username.data).first()
    #     if attempted_user and attempted_user.check_password_correction(
    #             attempted_password=form.password.data
    #     ):
    #         login_user(attempted_user)
    #         flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
    #         return redirect(url_for('market_page'))
    #     else:
    #         flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', )

# @app.route('/logout')
# def logout_page():
#     logout_user()
#     flash("You have been logged out!", category='info')
#     return redirect(url_for("home_page"))

@app.route('/verify', methods=["POST"])
def verify():
    email = request.form['email']
    send_otp(email)
    return render_template('signup.html')

@app.route('/validate', methods=['POST'])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        # form = RegisterForm()
    # if request.form.validate_on_submit():
    #     user_to_create = User(username=form.username.data,
    #                           email_address=form.email_address.data,
    #                           password=form.password1.data)
    #     db.session.add(user_to_create)
    #     db.session.commit()
    #     login_user(user_to_create)
    #     flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
    #     return redirect(url_for('market_page'))
    # if form.errors != {}: #If there are not errors from the validations
    #     for err_msg in form.errors.values():
    #         flash(f'There was an error with creating a user: {err_msg}', category='danger')
        return redirect(url_for("home_page"))
    return render_template('otp.html')
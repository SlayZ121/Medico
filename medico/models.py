from medico import db, login_manager, bcrypt, app
from flask_login import UserMixin
from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    role = db.Column(db.String(length=10), nullable=False)
    specialisation = db.Column(db.String(length=100), nullable=True) 
    
    # Relationship for user appointments
    user_appointments = db.relationship('Appointment', 
                                        foreign_keys='Appointment.user_id', 
                                        backref='user', 
                                        lazy=True)
    
    # Relationship for doctor appointments
    doctor_appointments = db.relationship('Appointment', 
                                          foreign_keys='Appointment.doctor_id', 
                                          backref='doctor', 
                                          lazy=True)

    def __repr__(self):
        return f'User {self.username}'
    
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Appointment for {self.name} on {self.date} at {self.time}'
    
    def get_doctor_name(self):
        doctor = User.query.get(self.doctor_id)
        return doctor.username if doctor else "Unknown Doctor"
    
class ModifiedSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    from_time = db.Column(db.Time, nullable=False)
    to_time = db.Column(db.Time, nullable=False)

    doctor = db.relationship('User', back_populates='modified_schedules')

User.modified_schedules = db.relationship('ModifiedSchedule', back_populates='doctor')
